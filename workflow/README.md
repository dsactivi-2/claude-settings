# Dev Workflow Hub

Lokales Grundsystem fuer:

- Zellij als Terminal-GUI
- Obsidian als Wissensspeicher
- Linear als Ticket-Quelle
- Git/Terminal als Event-Quellen
- spaetere RAG-Anbindung auf verdichteten Notizen

## Struktur

- `config.json` zentrale Pfade und Defaults
- `sync-agent.py` CLI fuer Sessions, Snapshots und Obsidian-Notizen
- `workflow-shell-hooks.zsh` Shell-Hooks fuer zsh
- `zellij-dev-workflow.kdl` Startlayout fuer Zellij

## Schnellstart

```bash
python3 ~/.claude/workflow/sync-agent.py init
python3 ~/.claude/workflow/sync-agent.py session-start
python3 ~/.claude/workflow/sync-agent.py snapshot
python3 ~/.claude/workflow/sync-agent.py session-stop
zellij --layout ~/.claude/workflow/zellij-dev-workflow.kdl
```

## Linear

Noch kein API-Schluessel hinterlegt. Ticket-Zuordnung laeuft lokal ueber:

- Branch-Namen wie `HOOK-12-allowlist-expiry`
- `LINEAR_TICKET_ID`
- `WORKFLOW_TICKET_ID`

## RAG

Fuer RAG nur verdichtete Daten indexieren:

- Daily Notes
- Ticket-Notizen
- Entscheidungsnotizen
- Session-Summaries
