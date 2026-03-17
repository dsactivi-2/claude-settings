# Architektur

## Ziel

Ein lokales Arbeitssystem, das mehrere Terminale, Tickets, Notizen und spaetere Wissenssuche verbindet.

## Komponenten

- `Zellij`
  - interaktive Terminal-GUI
  - ein Workspace mit Tabs fuer Agent, Git, Notes, Logs
- `sync-agent.py`
  - schreibt Session- und Snapshot-Events
  - erzeugt Daily Notes und Ticket-Notizen
- `Obsidian-WorkOS`
  - lesbare Oberflaeche fuer Arbeitstage und Tickets
- `Linear`
  - spaetere Source of Truth fuer echte Tickets
- `RAG`
  - spaetere Suche ueber verdichtete Notizen und Session-Summaries

## Datenfluss

```text
Terminale / Zellij / Git / Claude / Editor
                |
                v
          sync-agent.py
         /      |      \
        v       v       v
    events   state   Obsidian
                         |
                         v
                   RAG-ready Notes
```

## Warum nicht Raw-Logging in RAG

Nicht jede Shell-Zeile ist spaeter nuetzlich. In RAG sollten nur landen:

- Daily Notes
- Ticket-Notizen
- Decision Notes
- Fehlerzusammenfassungen
- Session-Summaries

## Ticket-Zuordnung

Reihenfolge:

1. `WORKFLOW_TICKET_ID`
2. `LINEAR_TICKET_ID`
3. Ticket-ID aus Branch wie `HOOK-12`
4. sonst `UNASSIGNED`

## Nächste Ausbaustufen

- echte Linear API Anbindung
- Git Hook fuer Commit-Logging
- Editor-Integrationen
- RAG Export fuer Session-Summaries
