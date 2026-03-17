---
name: "Sessions & Memory — All-in Setup"
description: "Optimales Multi-Layer Memory System für produktive Agenten. Integriert OpenClaw memory-core (MEMORY.md + Daily Logs), Supermemory als Langzeit-Store, Hybrid-Search (BM25 + Vector), MMR Diversity, Temporal Decay, QMD-Backend und Session-Indexierung. Für Callcenter-Agenten und Produktiv-Systeme."
version: "1.1.0"
category: "memory"
tags: ["memory", "sessions", "rag", "hybrid-search", "mmr", "temporal-decay", "qmd", "supermemory", "openclaw", "vector-search", "bm25", "embeddings", "ollama"]
triggers: ["memory", "session", "remember", "forget", "recall", "history", "context", "MEMORY.md", "daily log", "vector search", "embedding", "supermemory", "qmd", "hybrid search", "compaction"]
---

# Sessions & Memory — All-in Setup

Produktiv-Empfehlung: **Supermemory** (Plugin) als Haupt-Langzeit-Store + **memory-core** (Markdown) als lokale, erklärbare Schicht + **Hybrid-Search** für maximale Treffsicherheit.

## Wann diesen Skill nutzen

- Agenten mit langen Session-Historien (Callcenter, Support, Research)
- Wenn alte Infos neuere überschatten (→ Temporal Decay aktivieren)
- Wenn redundante Snippets zurückkommen (→ MMR aktivieren)
- Bei semantisch ähnlichen aber unterschiedlich formulierten Abfragen (→ Hybrid Search)
- Für Session-übergreifendes Gedächtnis (→ Session Memory aktivieren)

---

## 1. Memory-Architektur (3 Schichten)

| Schicht | Datei/Store | Zweck | Persistenz |
|---------|------------|-------|-----------|
| **Kurzzeit** | `memory/YYYY-MM-DD.md` | Laufende Session-Notizen, Append-only | 7–30 Tage |
| **Langzeit** | `MEMORY.md` | Kuratierte Fakten, Entscheidungen, Präferenzen | Permanent |
| **Vector Store** | SQLite (`.openclaw/memory/<agentId>.sqlite`) | Semantic Search über alle Markdown-Dateien | Persistent |
| **Supermemory** | Cloud-Plugin | Langzeit-Store mit Cross-Agent-Zugriff | Permanent |

### Schreib-Regel
```
Entscheidungen + Präferenzen + Fakten → MEMORY.md
Laufende Notizen + Session-Kontext → memory/YYYY-MM-DD.md
"Remember this" → SOFORT in Datei schreiben, NICHT im RAM behalten
```

### Memory Tools (OpenClaw — nur diese zwei existieren)
```
memory_search  → Semantische Suche über alle indizierten Markdown-Chunks
memory_get     → Direktes Lesen einer Memory-Datei (Pfad + optionale Zeilen)
```

> **WICHTIG:** Es gibt kein `memory_write`-Tool. Schreiben geschieht über normale Datei-Writes (Write-Tool / Bash).

---

## 2. Supermemory Plugin Setup

Supermemory ist ein OpenClaw-Memory-Plugin das als Haupt-Langzeit-Store fungiert. Beide Plugins gleichzeitig aktiv:

```javascript
// openclaw.config.js — Plugin-Slot-Konfiguration
plugins: {
  slots: {
    memory: ["supermemory", "memory-core"]  // Beide aktiv: Cloud + Lokal
  }
},

supermemory: {
  apiKey: process.env.SUPERMEMORY_API_KEY,  // In .zshrc setzen: export SUPERMEMORY_API_KEY=...
  // Supermemory als primärer Long-Term-Store
  // memory-core (MEMORY.md + Daily Logs) als lokale erklärbare Schicht
}
```

> Für rein lokale Setups (offline, Privacy): nur `memory: "memory-core"` setzen.

---

## 3. All-in Konfiguration (openclaw config)

```javascript
agents: {
  defaults: {
    // ── EMBEDDING PROVIDER (Gemini — beste Qualität) ─────────────────
    memorySearch: {
      enabled: true,                             // Explizit aktivieren
      provider: "gemini",
      model: "gemini-embedding-2-preview",
      outputDimensionality: 3072,                // Höchste Qualität
      fallback: "openai",                        // Fallback wenn Gemini offline
      remote: {
        apiKey: "${GEMINI_API_KEY}",             // Env-Var-Referenz (kein process.env!)
        batch: { enabled: true, concurrency: 2 }
      },

      // ── EMBEDDING CACHE ─────────────────────────────────────────────
      cache: {
        enabled: true,
        maxEntries: 50000
      },

      // ── HYBRID SEARCH (BM25 + Vector) ───────────────────────────────
      query: {
        hybrid: {
          enabled: true,
          vectorWeight: 0.7,                     // 70% Semantic
          textWeight: 0.3,                       // 30% BM25 Keywords
          candidateMultiplier: 4,

          // MMR — Duplikate reduzieren
          mmr: {
            enabled: true,
            lambda: 0.7                          // 0=Max Diversity, 1=Max Relevance
          },

          // Temporal Decay — Aktuelle Infos bevorzugen
          temporalDecay: {
            enabled: true,
            halfLifeDays: 30
          }
        }
      },

      // ── LIMITS ──────────────────────────────────────────────────────
      limits: {
        maxResults: 8,
        maxSnippetChars: 700
      },

      // ── CITATIONS ───────────────────────────────────────────────────
      citations: "auto",                         // auto | on | off

      // ── EXTRA PFADE (NUR spezifische Verzeichnisse!) ─────────────────
      // WARNUNG: Niemals ~/activi-dev-repos komplett — CPU-Feedback-Loop möglich!
      extraPaths: [
        { name: "brain", path: "~/activi-dev-repos/amp-brain", pattern: "**/*.md" },
        { name: "hooks-docs", path: "~/.claude/hooks", pattern: "**/*.md" }
      ],

      // ── SESSION MEMORY (experimentell) ──────────────────────────────
      experimental: { sessionMemory: true },
      sources: ["memory", "sessions"],
      sync: {
        watch: false,                            // DEAKTIVIERT: fseventsd CPU-Problem vermeiden
        sessions: {
          deltaBytes: 50000,
          deltaMessages: 25
        }
      },

      // ── VECTOR STORE ────────────────────────────────────────────────
      store: {
        vector: { enabled: true }               // sqlite-vec Beschleunigung
      }
    },

    // ── PRE-COMPACTION FLUSH ────────────────────────────────────────────
    compaction: {
      reserveTokensFloor: 20000,
      memoryFlush: {
        enabled: true,
        softThresholdTokens: 4000,
        systemPrompt: "Session nähert sich Kompaktierung. Wichtige Infos JETZT in Memory schreiben.",
        prompt: "Schreibe dauerhaften Kontext in die heutige Daily-Log-Datei (memory/YYYY-MM-DD.md mit heutigem Datum). Antworte mit NO_REPLY wenn nichts zu speichern."
      }
    }
  }
}
```

---

## 4. Lokaler Modus — Ollama Embeddings (offline, kein API Key)

Für vollständig lokale Setups (Privacy-kritisch, offline):

```javascript
memorySearch: {
  enabled: true,
  provider: "ollama",                          // Kein API Key nötig
  // Ollama muss laufen: ollama serve
  // Empfohlenes Embedding-Modell:
  // ollama pull nomic-embed-text  (best lokal)
  // oder: ollama pull mxbai-embed-large
  fallback: "none",                            // Kein Remote-Fallback
  cache: { enabled: true, maxEntries: 50000 },
  query: {
    hybrid: {
      enabled: true,
      vectorWeight: 0.7,
      textWeight: 0.3,
      mmr: { enabled: true, lambda: 0.7 },
      temporalDecay: { enabled: true, halfLifeDays: 30 }
    }
  }
}
```

```bash
# Setup
ollama pull nomic-embed-text    # ~274 MB, speziell für Embeddings optimiert
ollama serve                    # Falls nicht als Daemon laufend
```

> Deine installierten Modelle (qwen2.5-coder, glm4, llama3.1, dolphin-mistral) sind **Chat-Modelle**, keine Embedding-Modelle. `nomic-embed-text` separat pullen.

---

## 5. QMD Backend (für große Korpora: >500 Dateien)

Aktiviere QMD wenn: >500 Memory-Dateien, BM25+Vector+Reranking gewünscht, oder offline-fähige lokale Suche benötigt.

```javascript
// Separater Top-Level Key — parallel zu agents.defaults
memory: {
  backend: "qmd",
  citations: "auto",
  qmd: {
    includeDefaultMemory: true,
    searchMode: "query",                         // qmd | vsearch | query
    update: {
      interval: "5m",
      debounceMs: 15000,
      onBoot: true,
      waitForBootSync: false                     // Nicht blockieren beim Start
    },
    limits: {
      maxResults: 8,
      maxSnippetChars: 700,
      maxInjectedChars: 5000,
      timeoutMs: 4000
    },
    scope: {
      default: "deny",
      rules: [
        { action: "allow", match: { chatType: "direct" } }
      ]
    },
    paths: [
      { name: "brain", path: "~/activi-dev-repos/amp-brain", pattern: "**/*.md" },
      { name: "hooks-docs", path: "~/.claude/hooks", pattern: "**/*.md" }
    ],
    sessions: {
      enabled: true,
      retentionDays: 90
    }
  }
}
```

### QMD Installation
```bash
# QMD CLI installieren (vollständige URL — kein npm-Paket!)
bun install -g https://github.com/tobi/qmd

# SQLite mit Extensions (macOS)
brew install sqlite

# Manuelles Index-Warm-up (optional)
STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
export XDG_CONFIG_HOME="$STATE_DIR/agents/main/qmd/xdg-config"
export XDG_CACHE_HOME="$STATE_DIR/agents/main/qmd/xdg-cache"
qmd update && qmd embed
qmd query "test" -c memory-root --json >/dev/null 2>&1
```

### Migration: builtin SQLite → QMD (ohne Datenverlust)
```bash
# 1. Laufenden OpenClaw-Agent stoppen
# 2. Backup des bestehenden Index
cp -r ~/.openclaw/memory ~/.openclaw/memory.backup-$(date +%Y%m%d)

# 3. QMD installieren + testen (siehe oben)
# 4. config: memory.backend = "qmd" setzen
# 5. OpenClaw neu starten → QMD indexiert automatisch alle vorhandenen .md-Dateien
# 6. Test: memory_search("test") sollte Ergebnisse liefern
# 7. Falls Fehler: backend auf "builtin" zurücksetzen → Backup vorhanden
```

---

## 6. Claude Code Memory Integration

Mapping der OpenClaw Memory Tools auf das bestehende `~/mem-*` System:

| OpenClaw Tool | Claude Code Äquivalent | Pfad |
|--------------|----------------------|------|
| `memory_search` | `~/mem-search.sh "query"` | `~/.claude/memory.db` (11 MB) |
| `memory_get` | `Read` Tool | `~/.claude/projects/.../memory/` |
| File Write | `~/mem-add.sh "text" ns type` | `~/.claude/memory.db` |
| `MEMORY.md` | `MEMORY.md` | `~/.claude/projects/-Users-dsselmanovic/memory/MEMORY.md` |
| Daily log | `pre-compact-*.md` | `~/.claude/projects/-Users-dsselmanovic/memory/` |

### 3-Schichten Suche (vollständig)
```bash
# Layer 1: Semantic Search in Claude Memory DB
~/mem-search.sh "query"

# Layer 2: Alle Schichten
python3 ~/.claude/bin/mem-query.py "query" --all-layers

# Layer 3: OpenClaw memory_search (falls aktiv)
# → wird direkt im Agent-Kontext aufgerufen, kein Shell-Befehl
```

---

## 7. Memory-Regeln & Schreib-Protokoll

### Was IMMER in MEMORY.md speichern
- Architektur-Entscheidungen mit Begründung
- Kritische Pfade und Konfigurationen (SSH, APIs, Ports)
- User-Präferenzen für Workflow und Tools
- Lösung für wiederkehrende Probleme
- Hooks, Services, ihre Status und bekannte Bugs

### Was in Daily Log (`memory/YYYY-MM-DD.md`)
- Aktueller Task-Fortschritt
- Temporäre Debugging-Notizen
- In-Progress Work / offene Fragen
- Kontext der laufenden Session

### Was NICHT speichern
- Session-spezifischer Kontext (nach Abschluss wertlos)
- Unverifizierte Annahmen aus einzelner Datei
- Duplikate von CLAUDE.md-Inhalt
- Spekulative Schlüsse

### Daily Log Retention (Cleanup)
```bash
# Alte Daily Logs bereinigen (älter als 30 Tage)
find ~/.openclaw/workspace/memory -name "20[0-9][0-9]-[0-9][0-9]-[0-9][0-9].md" \
  -mtime +30 -delete

# Cronjob (optional) — täglich um 03:00
# 0 3 * * * find ~/.openclaw/workspace/memory -name "2*.md" -mtime +30 -delete
```

---

## 8. Temporal Decay Referenz

| Alter | Score-Multiplikator | Beispiel |
|-------|---------------------|---------|
| Heute | 100% | Aktuelle Session-Notizen |
| 7 Tage | ~84% | Letzte Woche |
| 30 Tage | 50% | Letzter Monat |
| 90 Tage | 12.5% | Letztes Quartal |
| 180 Tage | ~1.6% | Vor 6 Monaten |

**Nicht betroffen:** `MEMORY.md` + undatierte Dateien (z.B. `memory/network.md`, `memory/projects.md`)

**Halflife anpassen:**
- `14` — Sprint-Planung, sehr kurzlebiger Kontext
- `30` — Standard (Daily-Note-heavy) ← empfohlen
- `90` — Wenn ältere Notizen oft noch relevant sind

---

## 9. MMR Diversity Referenz

MMR löst das "5 fast identische Snippets"-Problem:

```
λ = 1.0  → Nur Relevanz (kein Diversity-Boost)
λ = 0.7  → Empfehlung: Balance Relevanz + Diversität  ← DEFAULT
λ = 0.5  → Moderate Diversität
λ = 0.0  → Maximale Diversität (ignoriert Relevanz)
```

**Aktivieren wenn:** `memory_search` gibt redundante, nahezu identische Snippets zurück.

---

## 10. Multimodal Memory (Gemini — Bilder + Audio)

Für Agenten die auch Bilder/Audio aus der Wissensdatenbank abrufen:

```javascript
memorySearch: {
  provider: "gemini",
  model: "gemini-embedding-2-preview",
  fallback: "none",                            // PFLICHT bei multimodal!
  remote: {
    apiKey: "${GEMINI_API_KEY}"                // PFLICHT für Gemini
  },
  extraPaths: [
    "~/activi-dev-repos/amp-brain/assets",
    "~/voice-notes"
  ],
  multimodal: {
    enabled: true,
    modalities: ["image", "audio"],
    maxFileBytes: 10000000                     // 10 MB pro Datei
  }
}
```

Unterstützte Formate:
- **Bilder:** `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
- **Audio:** `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac`

---

## 11. Callcenter / Produktiv-Agent Quickstart

```bash
# 1. Verzeichnisstruktur anlegen
mkdir -p ~/.openclaw/workspace/memory

# 2. MEMORY.md initialisieren (falls nicht vorhanden)
touch ~/.openclaw/workspace/MEMORY.md

# 3. Heutigen Daily Log anlegen
echo "# Session $(date +%Y-%m-%d)" > \
  ~/.openclaw/workspace/memory/$(date +%Y-%m-%d).md

# 4. (Optional) QMD für große Korpora
bun install -g https://github.com/tobi/qmd && brew install sqlite

# 5. (Optional) Lokale Embeddings
ollama pull nomic-embed-text
```

### Minimum-Config (90% der Produktiv-Fälle)
```javascript
agents: {
  defaults: {
    memorySearch: {
      enabled: true,
      provider: "gemini",
      model: "gemini-embedding-2-preview",
      remote: { apiKey: "${GEMINI_API_KEY}" },
      cache: { enabled: true, maxEntries: 50000 },
      citations: "auto",
      query: {
        hybrid: {
          enabled: true,
          vectorWeight: 0.7,
          textWeight: 0.3,
          mmr: { enabled: true, lambda: 0.7 },
          temporalDecay: { enabled: true, halfLifeDays: 30 }
        }
      }
    }
  }
}
```

---

## 12. Debugging & Health Checks

```bash
# Claude Memory DB Status
ls -lh ~/.claude/memory.db
~/mem-search.sh "test query"

# OpenClaw Memory Index Status
ls -lh ~/.openclaw/memory/ 2>/dev/null || echo "Kein OpenClaw Index gefunden"

# QMD Status (falls aktiviert)
STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
export XDG_CONFIG_HOME="$STATE_DIR/agents/main/qmd/xdg-config"
export XDG_CACHE_HOME="$STATE_DIR/agents/main/qmd/xdg-cache"
qmd query "test" --json 2>&1 | head -20

# Session Logs
ls -lh ~/.openclaw/agents/main/sessions/ 2>/dev/null

# Auto-Sync Hook Status (Claude Code)
launchctl print gui/$(id -u)/com.claude.hooks.autosync

# CPU-Check (fseventsd Warnung)
ps aux | grep fseventsd | awk '{print $3, $11}'
```

### Häufige Probleme

| Problem | Ursache | Lösung |
|---------|---------|--------|
| Alte Infos überschatten neue | Temporal Decay deaktiviert | `temporalDecay.enabled: true` |
| Redundante Snippets | MMR deaktiviert | `mmr.enabled: true` |
| Langsame Suche | Kein Cache / kein sqlite-vec | `cache.enabled: true` |
| fseventsd hohe CPU | `sync.watch: true` + viele extraPaths | `sync.watch: false` setzen |
| QMD startet nicht | Binary fehlt oder falsche URL | `bun install -g https://github.com/tobi/qmd` |
| QMD SQLite-Fehler | SQLite ohne Extensions | `brew install sqlite` |
| Embedding-Fehler (Gemini) | API Key fehlt | `export GEMINI_API_KEY=...` in `.zshrc` |
| Memory nach Compaction verloren | memoryFlush deaktiviert | `compaction.memoryFlush.enabled: true` |
| Multimodal funktioniert nicht | `fallback` nicht auf `"none"` | `fallback: "none"` setzen |
| `memory_write` not found | Tool existiert nicht | Normale File Writes nutzen |

---

## Referenz: OpenClaw Memory Tools

| Tool | Parameter | Rückgabe |
|------|-----------|---------|
| `memory_search(query)` | Semantischer Suchstring | Snippets (Text, Pfad, Zeilen, Score) |
| `memory_get(path, line?, n?)` | Workspace-relativer Pfad | Datei-Inhalt (Markdown) |

Beide Tools nur aktiv wenn `memorySearch.enabled = true` für den Agenten gesetzt ist.
