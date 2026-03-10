#!/usr/bin/env python3
"""control-agent.py — Auftrags-Kontrolle (Stop Hook)

Vergleicht die letzte User-Anweisung mit dem Agent-Ergebnis.
Prueft: Keyword-Coverage, Aktionsnachweis, Checklisten.
Exit 2 = Nachbessern noetig.
Exit 0 = OK, Agent darf stoppen.

Wird aufgerufen von: ~/.claude/hooks/control-agent.sh
Input: JSON via stdin (Claude Code Stop Hook Format)
"""

import sys
import json
import re
import os
import glob


def find_transcript(data):
    """Findet das Transcript-JSONL der aktuellen Session."""
    # Versuch 1: transcript_path aus Hook-Input
    tp = data.get("transcript_path", "")
    if tp and os.path.isfile(tp):
        return tp

    # Versuch 2: session_id -> Datei suchen
    sid = data.get("session_id", "")
    if sid:
        pattern = os.path.expanduser(f"~/.claude/projects/*/{sid}.jsonl")
        matches = glob.glob(pattern)
        if matches:
            return matches[0]

    # Versuch 3: Neueste JSONL-Datei
    pattern = os.path.expanduser("~/.claude/projects/*/*.jsonl")
    files = glob.glob(pattern)
    if files:
        return max(files, key=os.path.getmtime)

    return None


def get_last_user_message(path):
    """Extrahiert die letzte substanzielle User-Nachricht aus dem Transcript.

    Ueberspringt system-reminder-only Nachrichten und kurze Bestaetigungen.
    Liest nur die letzten 500 Zeilen fuer Performance.
    """
    msgs = []
    try:
        with open(path, "r") as f:
            lines = f.readlines()

        # Nur letzte 500 Zeilen — Performance bei grossen Transcripts
        for line in lines[-500:]:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue

            if entry.get("role") not in ("human", "user"):
                continue

            content = entry.get("content", "")
            if isinstance(content, list):
                texts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        texts.append(block.get("text", ""))
                content = " ".join(texts)

            # System-Reminders entfernen
            cleaned = re.sub(
                r"<system-reminder>.*?</system-reminder>", "", content, flags=re.DOTALL
            ).strip()

            if len(cleaned) > 15:
                msgs.append(cleaned)

    except (OSError, IOError):
        return None

    return msgs[-1] if msgs else None


def extract_keywords(text):
    """Extrahiert bedeutungsvolle Schluesselwoerter (4+ Zeichen, keine Stoppwoerter)."""
    stop_words = {
        # Deutsch
        "und", "oder", "aber", "dass", "eine", "einen", "einer", "einem",
        "dem", "den", "der", "die", "das", "ist", "sind", "wird", "werden",
        "hat", "haben", "kann", "soll", "muss", "bitte", "noch", "auch",
        "dann", "jetzt", "hier", "dort", "was", "wie", "wer", "welche",
        "wenn", "weil", "denn", "nach", "fuer", "ueber", "unter", "nicht",
        "kein", "keine", "sehr", "schon", "alle", "alles", "diese", "dieser",
        "dieses", "andere", "anderen", "mich", "dich", "sich", "sein",
        "seine", "seiner", "ihre", "ihrer", "wollen", "sollen", "muessen",
        "koennen", "duerfen", "warum", "nochmal", "nochmals", "eigentlich",
        "glaub", "glaube", "brauche", "brauch", "machen", "gemacht",
        # Englisch
        "this", "that", "with", "from", "the", "for", "and", "not",
        "please", "should", "would", "could", "make", "want", "need",
        "show", "just", "also", "have", "will", "some", "more", "than",
        "them", "they", "their", "what", "when", "which", "there", "about",
        "your", "like", "been", "into", "does", "were", "each",
    }

    words = re.findall(r"\b\w{4,}\b", text.lower())
    seen = set()
    unique = []
    for w in words:
        if w not in stop_words and w not in seen:
            seen.add(w)
            unique.append(w)
    return unique[:12]


def check_completion(user_msg, assistant_msg):
    """Prueft ob die Agent-Antwort die User-Anweisung abdeckt.

    Returns: Liste von Issues (leer = alles OK)
    """
    issues = []

    # 1. Keyword-Coverage
    kws = extract_keywords(user_msg)
    if kws and len(kws) >= 3:
        lower_resp = assistant_msg.lower()
        matched = sum(1 for k in kws if k in lower_resp)
        coverage = matched / len(kws)
        if coverage < 0.40:
            sample = ", ".join(kws[:5])
            issues.append(
                f"Nur {matched}/{len(kws)} Schluesselwoerter addressiert ({sample})"
            )

    # 2. Aufgaben-Erkennung: Imperativ-Woerter in User-Nachricht
    task_patterns = (
        r"(mach|erstell|schreib|bau|fix|deploy|install|konfigurier|einricht|"
        r"build|create|write|setup|implement|add|remove|update|change|restore|"
        r"wiederherstell|pruef|check|test|verifiz|zeig|loesch|delete|move|"
        r"refactor|optimier|reparier)"
    )
    task_words = re.findall(task_patterns, user_msg, re.IGNORECASE)

    if task_words and len(user_msg) > 50:
        # Aktionsnachweis im Ergebnis suchen
        action_evidence = re.search(
            r"(erstellt|geschrieben|geaendert|gefixt|eingerichtet|wiederhergestellt|"
            r"aktualisiert|geloescht|geprueft|verifiziert|getestet|hinzugefuegt|"
            r"repariert|optimiert|implementiert|"
            r"created|wrote|modified|fixed|updated|added|removed|implemented|"
            r"restored|verified|tested|checked|deleted|built|deployed)",
            assistant_msg,
            re.IGNORECASE,
        )
        checklist_evidence = re.search(
            r"(\[[ x]\]|ERLEDIGT|OFFEN|FEHLER|Erledigt|Fertig|Done|Completed|"
            r"Nachweis|Beweis|verifiziert|verified)",
            assistant_msg,
        )

        if not action_evidence and not checklist_evidence:
            issues.append(
                "Aufgabe erkannt aber kein Aktionsnachweis im Ergebnis"
            )

    # 3. Verhaeltnismaessigkeit: Lange Anweisung, kurze Antwort
    if len(user_msg) > 200 and len(assistant_msg) < 100:
        issues.append("Antwort unverhältnismässig kurz fuer die Anweisung")

    return issues


def main():
    # Input lesen
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    # Bereits in Nachbesserung: durchlassen (stop-enforcer prueft Details)
    if data.get("stop_hook_active", False):
        sys.exit(0)

    last_msg = data.get("last_assistant_message", "")
    if len(last_msg) < 100:
        sys.exit(0)

    # Transcript finden
    transcript = find_transcript(data)
    if not transcript:
        sys.exit(0)

    # User-Nachricht extrahieren
    user_msg = get_last_user_message(transcript)
    if not user_msg or len(user_msg) < 20:
        sys.exit(0)

    # Pruefung durchfuehren
    issues = check_completion(user_msg, last_msg)

    if issues:
        msg = " | ".join(issues)
        print(
            f"KONTROLL-AGENT: {msg}. "
            f"Pruefe ob die User-Anweisung vollstaendig erfuellt ist "
            f"und liefere Ergebnis mit Nachweis.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
