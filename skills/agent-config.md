# Agent Configuration - CLAUDE.md & AGENTS.md Best Practices

## Overview
This skill provides best practices for configuring Claude Code agents, managing CLAUDE.md global instructions, and maintaining AGENTS.md documentation for multi-agent systems.

## Core Principles

### 1. CLAUDE.md Structure
Global configuration file that persists across all Claude Code sessions.

**Location:** `~/.claude/CLAUDE.md`

**Essential Sections:**
```markdown
# Basis-Konfiguration
- Verhaltensregeln (Behavior Rules)
- Sprachen (Languages)
- Pfade (Paths)
- Skills Auto-Discovery
- Slash Commands
- Backup Strategy
```

**Key Variables:**
- `Primaer: Deutsch | Code: English` — Language preferences
- Project directories path
- Knowledge base locations
- Memory database paths

### 2. AGENTS.md Structure
Documentation for agent specialization and orchestration.

**Location:** `.claude/AGENTS.md` or `~/.claude/AGENTS.md`

**Essential Sections:**
```markdown
## Agent Registry
- Agent Name
- Specialization
- Activation Trigger (keywords/conditions)
- Tool Permissions
- System Prompt
- Integration Points
```

### 3. Configuration Best Practices

#### Trigger Keywords
Implement semantic triggers for automatic agent invocation:

**Backend Keywords:** api, rest, graphql, server, backend, database, auth, cache
**AI Building:** agent, rag, llm, prompt, embedding, langchain, vector
**DevOps:** docker, kubernetes, k8s, ci/cd, deploy, pipeline, terraform
**Testing:** test, jest, pytest, playwright, cypress, e2e, unit
**Mobile:** ios, android, react-native, flutter, expo, mobile
**Cloud:** aws, azure, gcp, lambda, serverless, cloud
**Security:** security, auth, encryption, owasp, vulnerability
**MLOps:** mlops, model, training, monitoring, feature-store

#### Tool Access Configuration
```
Tool Inheritance Model:
- No specification → Inherit all available tools
- Empty list [] → No tools
- Explicit list → Only listed tools
```

#### System Prompt Guidelines
- Clear specialization domain
- Specific tool requirements
- Constraints and limitations
- Integration guidelines
- Error handling preferences

### 4. Directory Structure
```
~/.claude/
├── CLAUDE.md (global config)
├── agents/
│   ├── agent-1.md
│   ├── agent-2.md
│   └── AGENTS.md (registry)
├── skills/
│   └── skill-*.md
├── hooks/
├── memory.db
└── scripts/
```

### 5. Agent Context Isolation
Subagents operate with isolated contexts to prevent contamination:

**Benefits:**
- Prevents context bleed between specialized agents
- Maintains focused expertise
- Improves performance and accuracy
- Clear domain boundaries

**Implementation:**
- Each agent has separate conversation context
- Tools are scoped per agent configuration
- Memory is isolated unless explicitly shared

### 6. Auto-Discovery Workflow

**Semantic Search Script:**
```bash
~/.claude/scripts/search-skills.sh "query"
```

**Filtering:**
```bash
~/.claude/scripts/filter-skills.sh --category X --min-installs Y
```

**Workflow:**
1. Detect keyword in user request
2. Run semantic search on skills
3. Suggest top matches
4. Install on user request

### 7. Slash Commands
Standard commands for agent management:

```
/workflow         — Show workflow configuration
/mandatory-rules  — Display enforcement rules
/character-profiles — List active agent personas
/skill-catalog    — Browse available skills
```

### 8. Multi-Agent Orchestration Pattern

**Context Manager Role:**
- Manages inter-agent communication
- Determines agent activation
- Handles context merging
- Manages tool access

**Typical Flow:**
1. User request → Context Manager
2. Keyword detection → Agent selector
3. Agent invocation with isolated context
4. Response aggregation
5. Context isolation maintained

### 9. Configuration Validation

**Before deployment:**
- Validate YAML/JSON syntax
- Verify tool references exist
- Check trigger keyword uniqueness
- Validate file paths
- Test agent invocation

**Testing Checklist:**
- Single agent invocation works
- Multi-agent chains complete
- Context isolation verified
- Tools accessible
- Error handling active

### 10. Version Control & Backup

**Best Practices:**
- Commit CLAUDE.md changes
- Track agent definitions in git
- Maintain backup of AGENTS.md
- Document configuration changes
- Tag stable releases

**Backup Location:**
```
~/.claude/CLAUDE.md.backup
~/.claude/agents/AGENTS.md.backup
```

## Implementation Examples

### Example CLAUDE.md Entry
```markdown
## Sprachen
Primaer: Deutsch | Code: English

## Pfade
- Projekte: ~/activi-dev-repos/
- Wissensdatenbank: ~/activi-dev-repos/amp-brain/
- Memory DB: ~/.claude/memory.db

## Skills Auto-Discovery
**Auto-Trigger Keywords:**
- Backend: api, rest, graphql, server, backend
- Testing: test, jest, pytest, e2e, unit
```

### Example AGENTS.md Entry
```markdown
## Agent: Python-Pro
- **Specialization:** Python web development
- **Activation:** Triggered by 'python', 'django', 'fastapi'
- **Tools:** FileSystem, BashExecutor, GitVCS
- **System Prompt:** [Custom Python-focused prompt]
- **Integration:** Works with api-designer, backend-developer
```

## Advanced Topics

### Context Merging
When multiple agents need to collaborate:
1. Initial context passed to primary agent
2. Secondary agent receives filtered context
3. Results merged by context manager
4. Isolation maintained between agents

### Tool Permission Scoping
```markdown
Agent: security-reviewer
Tools:
  - FileSystem (read-only)
  - GitVCS (read-only)
  - CodeAnalyzer (full)
Restricted:
  - BashExecutor (no write)
```

### Memory Integration
```markdown
Memory Systems:
- Redis: Short-term cache
- PostgreSQL: Long-term storage
- Claude Memory: Session-specific
- SuperMemory: Cross-session persistence
```

## Troubleshooting

**Issue:** Agent not triggering
- Check trigger keywords in AGENTS.md
- Verify agent file exists in ~/.claude/agents/
- Validate CLAUDE.md syntax

**Issue:** Tool access denied
- Verify tool in agent configuration
- Check tool permissions in ~/.claude/
- Validate inheritance rules

**Issue:** Context bleeding
- Ensure agent isolation enabled
- Check multi-agent orchestration settings
- Verify context manager active

## Related Skills
- claude-rules
- optimize-agents-md
- agent-orchestration-multi-agent-optimize
