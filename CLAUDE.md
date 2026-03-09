# Basis-Konfiguration

> Verhaltensregeln: Hooks (`managed-rules-inject.sh`) — always + keyword-triggered
> Agents/Skills/MCP: Hooks + AgentDB (`~/mem-search.sh "query"`)

## Sprachen
Primaer: Deutsch | Code: English

## Pfade
- Projekte: `~/activi-dev-repos/`
- Wissensdatenbank: `~/activi-dev-repos/amp-brain/`
- Memory DB: `~/.claude/memory.db`
- Suchen: `~/mem-search.sh "query"` | Speichern: `~/mem-add.sh "text" namespace type`

## Skills Auto-Discovery
**Semantic Search:** `~/.claude/scripts/search-skills.sh "query"`
**Filter:** `~/.claude/scripts/filter-skills.sh --category X --min-installs Y`

**Auto-Trigger Keywords:**
- Backend: api, rest, graphql, server, backend, database, auth, cache
- AI Building: agent, rag, llm, prompt, embedding, langchain, vector
- DevOps: docker, kubernetes, k8s, ci/cd, deploy, pipeline, terraform
- Testing: test, jest, pytest, playwright, cypress, e2e, unit
- Mobile: ios, android, react-native, flutter, expo, mobile
- Cloud: aws, azure, gcp, lambda, serverless, cloud
- Security: security, auth, encryption, owasp, vulnerability
- MLOps: mlops, model, training, monitoring, feature-store

**Workflow:** Detect keyword → Run search-skills.sh → Suggest top skills → Install on request

## Slash Commands
`/workflow` `/mandatory-rules` `/character-profiles` `/skill-catalog`

## Backup
Original: `~/.claude/CLAUDE.md.backup`
