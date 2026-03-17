#!/usr/bin/env python3
"""
analyze-my-style.py
Analysiert alle gespeicherten Sessions und Memory-Einträge und
erstellt ein Profil: Wie arbeitet der User? Was sind seine Präferenzen?
"""

import sqlite3
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime

DB_PATH = os.path.expanduser("~/.claude/memory.db")

def load_all_memory():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT namespace, type, content, created_at
        FROM memory_entries
        WHERE status = 'active'
        ORDER BY created_at ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def extract_keywords(text):
    """Extrahiert relevante Technologie- und Workflow-Keywords."""
    tech_patterns = {
        "Languages":     r'\b(Python|TypeScript|JavaScript|Bash|SQL|Go|Rust|Swift)\b',
        "Frameworks":    r'\b(FastAPI|Next\.js|React|Vue|Express|NestJS|LangChain|LangGraph)\b',
        "AI/ML":         r'\b(Ollama|LLM|RAG|pgvector|Qdrant|embedding|vector|OpenAI|Claude|Gemini|Qwen|llama)\b',
        "DevOps":        r'\b(Docker|Kubernetes|Tailscale|SSH|Caddy|Nginx|GitHub|Git|CI/CD|LaunchAgent)\b',
        "Databases":     r'\b(PostgreSQL|Redis|SQLite|pgvector|MongoDB|Supabase)\b',
        "Infra/Hosting": r'\b(Hetzner|VPS|Server|Cloud|iCloud|local|lokal)\b',
        "Tools":         r'\b(Portkey|Open Interpreter|Claude Code|hooks?|MCP|AgentDB)\b',
    }
    found = defaultdict(Counter)
    for category, pattern in tech_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            found[category][m.lower()] += 1
    return found

def analyze_work_patterns(entries):
    """Analysiert Verhaltensmuster aus den Session-Einträgen."""
    patterns = {
        "confirm_before_action": 0,
        "automation_focus": 0,
        "security_focus": 0,
        "local_first": 0,
        "full_solution": 0,
        "infrastructure": 0,
        "ai_tools": 0,
        "debugging": 0,
        "documentation": 0,
    }

    signals = {
        "confirm_before_action": [
            "bestätigt", "anweisung", "nur nach anweisung", "explizit", "keine proaktive",
            "kommunikation nach anweisungen", "confirm", "approved"
        ],
        "automation_focus": [
            "automatisch", "automatisiert", "hook", "launchagent", "auto-sync",
            "script", "pipeline", "automation", "interval"
        ],
        "security_focus": [
            "sicherheit", "security", "token", "api key", "secret", "verschlüssel",
            "guardrail", "block", "owasp", "jwt", "ssh"
        ],
        "local_first": [
            "lokal", "local", "ollama", "offline", "kein api", "keine api",
            "on-premise", "privat", "privacy"
        ],
        "full_solution": [
            "vollständig", "komplett", "production", "produktionsreif", "verifiziert",
            "getestet", "abgeschlossen", "konfiguriert"
        ],
        "infrastructure": [
            "server", "docker", "container", "vps", "hetzner", "tailscale",
            "vpn", "reverse proxy", "caddy", "nginx"
        ],
        "ai_tools": [
            "rag", "embedding", "vector", "llm", "agent", "mcp", "memory",
            "portkey", "open interpreter"
        ],
        "debugging": [
            "fehler", "error", "bug", "fix", "behoben", "debug",
            "analyse", "identifiziert"
        ],
        "documentation": [
            "dokumentation", "claude.md", "session-state", "memory", "notiz",
            "protokoll", "zusammenfassung"
        ],
    }

    for row in entries:
        text = row["content"].lower()
        for key, words in signals.items():
            if any(w in text for w in words):
                patterns[key] += 1

    return patterns

def find_recurring_topics(entries):
    """Findet häufig wiederkehrende Themen/Projekte."""
    topics = Counter()
    topic_map = {
        "hooks & automation":    ["hook", "launchagent", "auto-sync", "script", "session"],
        "memory system":         ["memory", "agentdb", "redis", "pgvector", "embedding"],
        "open interpreter":      ["open interpreter", "oi-", "ollama", "profil"],
        "docker & server":       ["docker", "container", "hetzner", "server", "ssh"],
        "ai & rag":              ["rag", "llm", "vector", "portkey", "agent"],
        "security & auth":       ["jwt", "token", "security", "guardrail", "block"],
        "cleanup & refactoring": ["cleanup", "dedup", "konsolidie", "refactor"],
        "testing & verification":["test", "verifizier", "check", "health"],
    }
    for row in entries:
        text = row["content"].lower()
        for topic, keywords in topic_map.items():
            if any(k in text for k in keywords):
                topics[topic] += 1
    return topics

def analyze_decisions(entries):
    """Extrahiert wichtige Entscheidungen."""
    decisions = []
    for row in entries:
        if row["namespace"] == "decisions":
            decisions.append(row["content"][:200])
    return decisions

def compute_tech_stack(entries):
    """Aggregiert Technologie-Nutzung über alle Einträge."""
    combined = "\n".join(r["content"] for r in entries)
    return extract_keywords(combined)

def print_profile(entries):
    total = len(entries)
    namespaces = Counter(r["namespace"] for r in entries)

    patterns = analyze_work_patterns(entries)
    topics = find_recurring_topics(entries)
    tech = compute_tech_stack(entries)
    decisions = analyze_decisions(entries)

    # Zeitraum
    timestamps = [r["created_at"] for r in entries if r["created_at"]]
    if timestamps:
        oldest = datetime.fromtimestamp(min(timestamps) / 1000).strftime("%d.%m.%Y")
        newest = datetime.fromtimestamp(max(timestamps) / 1000).strftime("%d.%m.%Y")
        timerange = f"{oldest} → {newest}"
    else:
        timerange = "unbekannt"

    print("=" * 60)
    print("  USER ARBEITSPROFIL — Analyse aus Session-History")
    print("=" * 60)
    print(f"\n📊 Datenbasis: {total} Einträge | Zeitraum: {timerange}")
    print(f"   Namespaces: {dict(namespaces)}\n")

    print("━" * 60)
    print("🧠 ARBEITSSTIL — Verhaltens-Muster")
    print("━" * 60)
    max_val = max(patterns.values()) or 1
    style_labels = {
        "confirm_before_action": "Bestätigung vor Aktion      (kein Blindflug)",
        "automation_focus":      "Automation-first             (alles automatisieren)",
        "security_focus":        "Security-bewusst             (Token, Secrets, Guards)",
        "local_first":           "Local/Privacy-first          (Ollama, lokal, offline)",
        "full_solution":         "Vollständige Lösungen        (kein TODO, kein Placeholder)",
        "infrastructure":        "Infrastruktur-affin          (Server, Docker, VPN)",
        "ai_tools":              "AI-Tools Heavy User          (RAG, Agents, MCP)",
        "debugging":             "Debugging-getrieben          (Fehler analysieren, fixen)",
        "documentation":         "Dokumentation wichtig        (Memory, CLAUDE.md)",
    }
    for key, label in style_labels.items():
        val = patterns[key]
        bar = "█" * int(val / max_val * 20)
        print(f"  {label:<42} [{bar:<20}] {val}")

    print()
    print("━" * 60)
    print("🔁 HÄUFIGSTE THEMEN (Projekte & Arbeitsfelder)")
    print("━" * 60)
    for topic, count in topics.most_common(10):
        bar = "█" * min(count * 2, 30)
        print(f"  {topic:<28} {bar} ({count}x)")

    print()
    print("━" * 60)
    print("🛠  TECHNOLOGIE-STACK (aus Session-History extrahiert)")
    print("━" * 60)
    for category, counts in tech.items():
        if counts:
            top = ", ".join(f"{k}({v})" for k, v in counts.most_common(5))
            print(f"  {category:<16} {top}")

    print()
    print("━" * 60)
    print("✅ KERNEIGENSCHAFTEN — Zusammenfassung")
    print("━" * 60)

    traits = []
    if patterns["confirm_before_action"] > 3:
        traits.append("• Arbeitet niemals blind — will immer wissen was passiert bevor es ausgeführt wird")
    if patterns["automation_focus"] > 5:
        traits.append("• Automatisiert konsequent: Hooks, Scripts, LaunchAgents für alles Wiederholende")
    if patterns["local_first"] > 3:
        traits.append("• Privacy/Local-first: bevorzugt lokale Modelle (Ollama) gegenüber Cloud-APIs")
    if patterns["security_focus"] > 3:
        traits.append("• Security-bewusst: schützt Tokens, baut Guardrails, keine unsicheren Abkürzungen")
    if patterns["full_solution"] > 5:
        traits.append("• Erwartet vollständige, produktionsreife Lösungen — kein 'der Rest ist analog'")
    if patterns["infrastructure"] > 5:
        traits.append("• Infrastruktur-Profi: Server, Docker, VPN, Reverse Proxies selbst aufgebaut")
    if patterns["ai_tools"] > 4:
        traits.append("• Heavy AI-User: baut eigene Agents, RAG-Systeme, Memory-Stacks")
    if topics["memory system"] > 3:
        traits.append("• Investiert in persistentes Memory (AgentDB, Redis, pgvector) für AI-Kontinuität")
    if topics["hooks & automation"] > 5:
        traits.append("• Hat komplexes Hooks-System aufgebaut das Claude Code-Verhalten steuert")
    if patterns["debugging"] > 8:
        traits.append("• Debuggt systematisch: identifiziert Root Cause, fixiert direkt, keine Workarounds")

    for t in traits:
        print(f"  {t}")

    if decisions:
        print()
        print("━" * 60)
        print("📌 WICHTIGE ENTSCHEIDUNGEN (aus decisions-Namespace)")
        print("━" * 60)
        for i, d in enumerate(decisions[:3], 1):
            short = d.replace("\n", " ")[:180]
            print(f"  [{i}] {short}...")

    print()
    print("=" * 60)
    print("  Profil generiert aus ~/.claude/memory.db")
    print(f"  {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 60)

if __name__ == "__main__":
    entries = load_all_memory()
    if not entries:
        print("Keine Einträge in memory.db gefunden.")
    else:
        print_profile(entries)
