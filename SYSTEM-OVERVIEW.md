# System-Uebersicht

Konsolidierte Referenz aller Regeln, Hooks, Commands, Agents, Skills und Tools.
Stand: 2026-02-25

---

## 1. Architektur

```
User-Prompt
  |
  v
[SessionStart] --> managed-prompt.sh, load-patterns.sh, session-log-start.sh
  |
  v
[UserPromptSubmit] --> managed-rules-inject.sh (Always + Keyword Rules)
  |
  v
[PreToolUse] --> Bash: git-blocker | Task: model-enforcer, skill-inject, managed-prompt
               | Edit/Write: managed-prompt, block-secrets-in-code
  |
  v
  Tool-Ausfuehrung
  |
  v
[PostToolUse] --> context-monitor (alle) | edit-reviewer (Edit/Write)
  |
  v
[Stop] --> stop-round-tracker, control-agent, stop-enforcer
[SubagentStart] --> subagent-context
[SubagentStop] --> subagent-round-tracker, subagent-enforcer
[PreCompact] --> managed-prompt
[SessionEnd] --> git-save, mem-save-hook, hook-learn, session-log-end
```

---

## 2. Hook-Pipeline (22 Scripts, 10 Events)

| Event | Scripts (Reihenfolge) |
|---|---|
| SessionStart | managed-prompt (init) -> load-patterns -> session-log-start |
| UserPromptSubmit | managed-rules-inject (Always + Keyword Rules) |
| PreToolUse:Bash | git-blocker (destruktive Git-Befehle blockieren) |
| PreToolUse:Task | model-enforcer -> skill-inject -> managed-prompt (task-rules) |
| PreToolUse:Edit/Write | managed-prompt (edit-rules) -> block-secrets-in-code |
| PostToolUse:All | context-monitor (Kontext-Verbrauch) |
| PostToolUse:Edit/Write | edit-reviewer (Aenderungen pruefen) |
| PreCompact | managed-prompt (Kontext sichern) |
| Stop | stop-round-tracker -> control-agent -> stop-enforcer |
| SubagentStart | subagent-context |
| SubagentStop | subagent-round-tracker -> subagent-enforcer |
| SessionEnd | git-save -> mem-save-hook -> hook-learn -> session-log-end |

---

## 3. Always-Rules (jede Nachricht)

| Regel | Inhalt |
|---|---|
| Ehrlichkeit | Nie luegen, nie faken, nie ungetesteten Code als fertig markieren |
| Approval | Nicht ohne explizites "bestaetige"/"confirm"/"approved" fortfahren |
| Clean Work | Vollstaendige Loesungen, keine Platzhalter, kein Ghost-Code |
| Zero Excuses | 7-Punkt-Checkliste: alles verifizieren, jede Datei nochmal lesen |
| Quality Code | Keine Abkuerzungen, Tests mitschreiben, Test-IDs in jedem UI-Element |

---

## 4. Keyword-Rules

| Nr | Trigger-Keywords | Regel |
|---|---|---|
| 1 | erklaer, unterschied, was ist | Kurz und klar antworten |
| 2 | vergleich, vs | Immer als Tabelle |
| 3 | recherch, such mir, research | Internet nutzen, Quellen angeben, 2x verifizieren |
| 4 | phase, schritt, step | Nur Phase/Schritt 1, dann STOP |
| 5 | programmier, bau mir, erstell mir, build | Ohne Docs nicht starten, fehlende auflisten |
| 6 | projekt, anwendung | Rueckfragen stellen statt losrennen |
| 7 | management, delegiere, koordiniere | Management-Level: ALLE Code-Tasks delegieren |
| 8 | sub.agent, executor, architect... | Agent-Routing: haiku/sonnet/opus je Komplexitaet |
| 9 | skill, autopilot, ultrawork, ralph... | Skill-Routing aktivieren |
| 10 | codex, gemini, mcp, openai | MCP-Tools: ask_codex (gpt-5.3), ask_gemini (gemini-3-pro) |
| 11 | state_, notepad, project.memory | OMC State/Notepad/Project-Memory Tools |
| 12 | cancel, broad request, continuation | OMC-Protokolle: Cancel, Parallel, Continuation |
| 13 | session.state, wal.protokoll | Session-State: WAL-Prinzip, Recovery, Memory-Flush |
| 14 | prompt.bibliothek, auto.prompt | Auto-Prompt: Embedding-basierte Vorschlaege |
| 15 | kontext, context.%, flush | Self-Check: Kontext-Verbrauch, Emergency Flush |
| 16 | memory, mem.search, agentdb | Memory-System: SQLite + 1536-dim Vektoren |
| 17 | implementier, refactor, code... | Delegation: Conductor-Rolle, Code nie selbst aendern |
| 18 | hooks, hook-rebuild | Hook-Konfiguration: 8-Event-Protokoll verifizieren |
| 19 | deduplication, consolidation, cleanup | Deduplizierung und Clean Storage |
| 20 | pattern, learning, adaptive | Agent-Learning: Patterns tracken, Reasoning persistieren |

---

## 5. Slash Commands

| Command | Zeilen | Inhalt | Wann nutzen |
|---|---|---|---|
| /mandatory-rules | 664 | 27 Pflichtregeln, gruppiert nach Prioritaet | Regelwerk nachschlagen |
| /workflow | 936 | Phase 0-7, Gates, Freezes, Change Requests | Neues Projekt starten |
| /character-profiles | 416 | 10+ Agent-Modi mit Deliverables und Gates | Rollenwechsel |
| /skill-catalog | 196 | Alle Skills kategorisiert | Skill-Uebersicht |
| /claude-flow-help | 104 | System/Agent/Task/Memory/SPARC/Swarm/MCP | Claude-Flow Befehle |
| /claude-flow-memory | 108 | Store/Query/Stats/Export/Import/Cleanup | Memory-Operationen |
| /claude-flow-swarm | 206 | Strategien, Agent-Typen, Optionen, Beispiele | Multi-Agent-Koordination |

---

## 6. 27 Mandatory Rules (gruppiert)

### Prioritaet 0 -- Absolut
Keine Data Loss. Security nicht kompromittieren. Production nicht brechen.

### Regeln 1-4: Approval und Gates

| Nr | Regel |
|---|---|
| 1 | Keine Phase ohne explizites "bestaetige"/"confirm"/"approved" |
| 2 | Wingman: Requirements vollstaendig klaeren, Zusammenfassung bestaetigen lassen |
| 3 | Architect: Vollstaendige Doku (Architecture Doc, NFRs, Playbooks, IaC, API Specs) |
| 4 | Planner: Phase-Gate-System zwingend (Dev, Test, Review, Bugfix, Docs, Meeting, Sign-Off) |

### Regeln 5-9: Quality und Testing

| Nr | Regel |
|---|---|
| 5 | Developer: OTOP Standards, Test-First, Quality Gates (Lint, Types, kein Debug-Code) |
| 6 | DevOps: IaC only, Secrets nie im Code, SSL/TLS, Least-Privilege, Backup getestet |
| 7 | Tester: Alle Kategorien (Unit/Integration/E2E/API/Security/Performance/A11y), 100% Pass |
| 8 | Reviewer: 100% Code Coverage, Security Checklist, OWASP Top 10 |
| 9 | Dokumentation: Immer aktuell, Setup/API/Architecture/Deployment/Troubleshooting |

### Regeln 10-13: Kommunikation

| Nr | Regel |
|---|---|
| 10 | Bei Unklarheit fragen, Blocker sofort melden, Stakeholder-Updates |
| 11 | Quality NIEMALS fuer Speed opfern, bei Zeitdruck Scope reduzieren |
| 12 | 5 kritische Gates: Wingman->Architect->Designer->Planner->Phase N+1 |
| 13 | Notfall: Sofort melden, kein unilateral action, Playbook befolgen |

### Regeln 14-16: Enforcement

| Nr | Regel |
|---|---|
| 14 | Minor=Warning+Fix, Major=Phase blocked+Revert, Critical=Immediate Rollback |
| 15 | Keine Ausnahmen ohne User-Genehmigung, User-Override moeglich aber dokumentiert |
| 16 | Compliance-Checks: Daily (Tests/Reviews/Docs), Weekly (Regeln), Phase (komplett) |

### Regeln 17-20: Standards

| Nr | Regel |
|---|---|
| 17 | Jede Phase = Production-Ready (Testing, Security, Performance, Monitoring) |
| 18 | Projekt-Ordnerstruktur zwingend, nichts loeschen, alle Versionen behalten |
| 19 | Jeder Agent muss dokumentieren (Interview/Architecture/Design/Plan/Code/Tests) |
| 20 | Fehlende Doku = Blocker, Task gilt als nicht complete |

### Regeln 21-24: Cross-Project Learning

| Nr | Regel |
|---|---|
| 21 | Vergangene Projekte pruefen, Pattern Recognition, Fehler nicht wiederholen |
| 22 | Cross-References, Pattern Library, Metrics tracken |
| 23 | Antworten mit echter Dokumentation, nie ohne Wissensdatenbank-Pruefung |
| 24 | Search und Retrieval Tools nutzen, automatische Knowledge Application |

### Regeln 25-27: Freeze und Validation

| Nr | Regel |
|---|---|
| 25 | 5 Doku-Kategorien: Standard+Must-Have+Good-to-Have (auto) + Nice-to-Have+Not-Required (User fragen) |
| 26 | Absoluter Scope Freeze nach Planner-Approval, einzige Ausnahme: Funktionalitaet verhindert |
| 27 | Cascade Re-Validation: Bei Restart zurueck zu Phase 1, nicht zur aktuellen Phase |

---

## 7. Workflow-Phasen

| Phase | Name | Dauer | Fokus |
|---|---|---|---|
| 0a | Wingman | 2-5 Tage | Requirements klaeren, Briefing erstellen |
| 0b | Architect | 5-10 Tage | Systemarchitektur, NFRs, Playbooks, API Specs |
| 0c | Designer | 10-15 Tage | Design System, alle Screens, Flows, Components |
| 0d | Planner | 3-5 Tage | Execution Plan, 105 Tasks, Timeline, Phase-Gates |
| 1 | Foundation | Woche 1-2 | Repo, CI/CD, Dev-Environment, Staging, Monitoring |
| 2 | Core Backend | Woche 3-5 | DB Schema, API, CRUD, Endpoints, Logging, Metrics |
| 3 | Agent Service | Woche 6-8 | Agent-Management, Docker, ECS, Status-Monitoring |
| 4 | Frontend | Woche 9-11 | UI-Framework, Components, WebSocket, Dashboard |
| 5 | Monitoring | Woche 12-13 | Prometheus, Grafana, ELK, Alerts |
| 6 | Testing | Woche 14-15 | Integration, Load, Security, Performance, Pen-Test |
| 7 | Production | Woche 16 | Terraform, Deploy, Smoke Tests, DNS, SSL, Go-Live |

Jede Phase durchlaeuft: Development -> Testing -> Code Review -> Bug Fixing -> Docs -> Review Meeting -> Sign-Off

---

## 8. Agent-Modi

| Agent | Wann | Deliverables | Gate |
|---|---|---|---|
| Wingman | Projektstart | Interview Notes, Briefing | User: "bestaetige" |
| Architect | Nach Wingman | Architecture Doc, NFRs, Playbooks, IaC, API Specs | User: "bestaetige" |
| Designer | Nach Architect | Design System, Screens, Flows, Components, Prototypes | User: "bestaetige Design" -> DESIGN FREEZE |
| Planner | Nach Designer | Execution Plan, Tasks, Timeline, Phase-Gates | User: "bestaetige Plan" -> SCOPE FREEZE |
| Developer | Phase 1-7 | Code, Tests, Task-Docs | Phase-Gate |
| DevOps | Phase 1-7 | Infrastruktur, CI/CD, Monitoring, Secrets | Phase-Gate |
| Tester | Nach Development | Test Plans, Results, Coverage, Bug Reports | 100% Pass |
| Reviewer | Nach Development | Review Checklists, Findings | 100% Coverage |
| Security Eng. | Phase 1, 6 | Audit Report, Vulnerability Assessment, Pen-Test | Keine Vulnerabilities |
| Integration Sp. | Phase 3 | Integration Docs, API Connections, Tests | Phase-Gate |
Weitere: Data Engineer (ETL), Tech Writer (Docs), SRE (Reliability) -- bei Bedarf.
Aktivierung: "Mode [Name]" oder "Arbeite als [Name]"

---

## 9. Skills

### Kern-Skills (immer aktiv)

| Skill | Trigger |
|---|---|
| workflow | Neues Projekt, "show workflow" |
| mandatory-rules | Immer aktiv |
| character-profiles | "Mode [Name]" |
| skill-catalog | "show my skills" |

### Arbeits-Skills (Keyword-aktiviert)

| Skill | Trigger-Phrase | Zweck |
|---|---|---|
| autopilot | "build me" | Autonomes Bauen |
| ralph | "dont stop" | Ununterbrochen weiterarbeiten |
| ultrawork (ulw) | "ulw" | Intensivmodus |
| ultrapilot | "parallel build" | Paralleles Bauen |
| ecomode | "eco" | Ressourcenschonend |
| swarm | "coordinated agents" | Multi-Agent-Koordination |
| pipeline | "chain agents" | Agenten verketten |
| ultraqa | auto | Automatische Qualitaetssicherung |
| plan | "plan this" | Planung |
| ralplan | iterativ | Iterative Planung |
| tdd | "test first" | Test-Driven Development |
| build-fix | "type errors" | Build-Fehler beheben |
| code-review | "review code" | Code-Review |
| security-review | -- | Security-Pruefung |
| deepsearch | "find in codebase" | Codebase durchsuchen |
| research | "analyze data" | Datenanalyse |
| frontend-ui-ux | UI-Aenderungen (silent) | UI/UX-Arbeit |
| git-master | Git-Operationen (silent) | Git-Verwaltung |
| cancel | "cancelomc" | Aktuellen Modus abbrechen |

Konfliktloesung: explizit > default, ecomode > ultrawork

### Public Skills
docx (Word), pdf (PDF), pptx (Praesentationen), xlsx (Tabellen), frontend-design (UI-Components)

---

## 10. Claude-Flow Commands

### System
```
./claude-flow start [--ui]     # Starten
./claude-flow status           # Status
./claude-flow monitor          # Echtzeit-Monitoring
./claude-flow stop             # Stoppen
```

### Agents
```
./claude-flow agent spawn <type> [--name --priority]
./claude-flow agent list | info <id> | terminate <id>
```

### Tasks
```
./claude-flow task create <type> "desc" | list | status <id> | cancel <id>
./claude-flow task workflow <file>
```

### Memory
```
./claude-flow memory store "key" "value" [--namespace]
./claude-flow memory query "search" [--namespace --limit]
./claude-flow memory stats [--namespace]
./claude-flow memory export/import <file> [--namespace]
./claude-flow memory cleanup [--days --namespace]
```

### SPARC
```
./claude-flow sparc "task"           # SPARC-Orchestrator
./claude-flow sparc modes            # 17+ Modi anzeigen
./claude-flow sparc run <mode> "task"
./claude-flow sparc tdd "feature"
```

### Swarm
```
./claude-flow swarm "task" --strategy <auto|development|research|analysis|testing|optimization|maintenance>
Optionen: --background --monitor --ui --parallel --distributed --review --testing --max-agents <n>
Koordination: centralized (default) | distributed | hierarchical | mesh | hybrid
```

---

## 11. Memory-System

### Lokale AgentDB (SQLite + Vektoren)

| Komponente | Pfad/Befehl |
|---|---|
| Datenbank | `~/.claude/memory.db` (SQLite + 1536-dim Embeddings) |
| Suchen | `~/mem-search.sh "query"` |
| Speichern | `~/mem-add.sh "text" namespace type` |
| 3-Schichten-Suche | `python3 ~/.claude/bin/mem-query.py "query" --all-layers` |
| Auto-Save | Bei Stop + SessionEnd (via Hooks) |

Namespaces: decisions, techstack, patterns, errors, projects, preferences
Types: semantic, episodic, procedural, working, pattern

### OMC State Tools

| Tool | Zweck |
|---|---|
| state_read/write/clear/list_active | Aktiven Modus verwalten |
| notepad_read/write_priority/write_working | Notizen (priority=permanent, working=7d) |
| project_memory_read/write/add_note | Projekt-spezifischer Speicher |

Pfade: `{worktree}/.omc/state/`, `{worktree}/.omc/notepad.md`, `{worktree}/.omc/project-memory.json`

### Claude-Flow Memory

Namespaces: default, agents, tasks, sessions, swarm, project, spec, arch, impl, test, debug

---

## 12. MCP-Tools

| Tool | Modell | Staerke | Einsatz |
|---|---|---|---|
| ask_codex | gpt-5.3-codex | Code, Planung, Review | Ersetzt: architect, planner, critic, code-reviewer, security-reviewer, tdd-guide |
| ask_gemini | gemini-3-pro | 1M Context, Design | Ersetzt: designer, writer, vision |

Protokoll: MCP-DIRECT fuer Ersatz-Tasks, IMMER context_files mitgeben, Fallback=Claude Agent, MCP=beratend (mit Tests verifizieren), background:true fuer lange Calls. Timeout bis 1h.

Nicht-MCP-ersetzbar: executor, explore, researcher, scientist, build-fixer, qa-tester, git-master, deep-executor

---

## 13. Freeze-Points

| Freeze | Ausloeser | Was ist gesperrt | Ausnahme |
|---|---|---|---|
| Design Freeze | User: "bestaetige Design" | Alle Design-Aenderungen (Farben, Layout, Components) | Nur wenn Funktionalitaet verhindert |
| Scope Freeze | User: "bestaetige Plan" | ALLES (Features, Design, Architektur, Scope, Timeline) | Nur wenn Funktionalitaet verhindert |
| Phase Gate | Ende jeder Phase | Naechste Phase blockiert bis 100% complete | Kein Weiter ohne Sign-Off aller Stakeholder |

Change-Request-Eskalation: Developer -> Planner -> Architect -> Designer -> User
Bei Restart: Cascade Re-Validation ab Phase 1 (nicht ab aktueller Phase)

---

## 14. Pfade und Konfiguration

### Systemdateien

| Datei | Pfad |
|---|---|
| Global Config | `~/.claude/CLAUDE.md` |
| Settings/Hooks | `~/.claude/settings.json` |
| Hook-Scripts | `~/.claude/hooks/*.sh` |
| Slash Commands | `~/.claude/commands/*.md` |
| Memory DB | `~/.claude/memory.db` |
| Memory Scripts | `~/mem-search.sh`, `~/mem-add.sh`, `~/.claude/bin/mem-query.py` |
| Backup | `~/.claude/CLAUDE.md.backup` |

### Projektdateien

| Pfad | Inhalt |
|---|---|
| `~/activi-dev-repos/` | Alle Projekte |
| `~/activi-dev-repos/amp-brain/` | Wissensdatenbank |
| `{worktree}/.omc/` | OMC State, Notepad, Project-Memory |
| `{worktree}/.omc/SESSION-STATE.md` | Session-State (WAL-Prinzip) |

### Wissensdatenbank-Struktur
`/wissensdatenbank/projekte/[projekt]/` mit Unterordnern: `00-inception/` (wingman, architect, designer, planner), `01-phase1..07/` (plan, development, testing, review, bugs, docs, metrics, sign-off), `daily-standups/`, `weekly-reports/`, `incidents/`, `project-summary/`

### Sprachen und Routing
Sprachen: Primaer Deutsch, Code English.
Agent-Routing: Einfach=Haiku (writer, executor-low), Standard=Sonnet (executor, researcher, designer, qa-tester), Komplex=Opus (planner, critic, architect, code-reviewer, security-reviewer)
