# Optimize Agents.md - Token Compression & Efficiency (10k→2.5k)

## Overview
This skill provides techniques to compress and optimize AGENTS.md and agent configuration files, reducing token usage by 75% while maintaining all critical information. Transforms verbose agent definitions into efficient, scannable formats.

## Core Optimization Strategies

### 1. Remove Redundancy (30% reduction)

#### Before (Verbose)
```markdown
# Agent: Python-Pro

## Description
The Python-Pro agent is a specialized assistant designed for Python development tasks.
It provides comprehensive support for Python-based projects including web development,
data analysis, and automation tasks. This agent has deep expertise in Python frameworks
like Django, FastAPI, Flask, and more.

## Activation Trigger
This agent is automatically activated when the user mentions Python-related keywords
such as: python, django, fastapi, flask, etc. Users can also explicitly request this
agent by asking for Python expertise.

## Tool Access
The Python-Pro agent has access to the following tools:
- FileSystem: Full read/write access
- BashExecutor: Execution of bash commands
- GitVCS: Version control operations
```

#### After (Optimized)
```markdown
# Python-Pro

**Specialization:** Python web/data/automation
**Triggers:** python, django, fastapi, flask
**Tools:** FileSystem, BashExecutor, GitVCS
```

**Token Reduction:** 180 → 40 tokens (78% savings)

### 2. Use Structured Formats (40% reduction)

#### Avoid Prose Descriptions
```markdown
# BAD (Prose - high tokens)
The authentication agent handles various authentication mechanisms
including OAuth2, JWT, and session-based authentication. It provides
validation of tokens, management of credentials...

# GOOD (Structured)
**Specialization:** Authentication (OAuth2, JWT, Sessions)
**Primary Uses:** Token validation, Credential management
**Related:** authorization-agent, security-advisor
```

### 3. Table Format for Multiple Agents (35% reduction)

#### Instead of Individual Sections
```markdown
| Agent | Specialization | Triggers | Tools | Status |
|-------|---|---|---|---|
| python-pro | Python web/data | python, django, fastapi | FileSystem, Bash | Active |
| js-expert | JavaScript/TypeScript | js, ts, node, react | FileSystem, Bash | Active |
| devops-pro | Infrastructure/Deployment | docker, k8s, ci/cd | Docker, Bash, Git | Active |
| security-reviewer | Security Analysis | security, auth, crypto | FileSystem, CodeAnalysis | Active |
```

**Benefits:**
- 50% more agents in same space
- Quick scanning
- Easy comparison
- Sortable format

### 4. Abbreviation System (20% reduction)

Create abbreviation key at top of file:
```markdown
## Abbreviations
- **FS:** FileSystem (full R/W access)
- **Bash:** BashExecutor (command execution)
- **Git:** GitVCS (version control)
- **CA:** CodeAnalyzer (syntax/semantic)
- **MC:** MemoryCache (session storage)
- **R/O:** Read-Only
- **Req:** Required tools
- **Opt:** Optional tools
```

#### Before
```markdown
Tool Permissions:
- FileSystem (Read/Write Access)
- BashExecutor (Limited to project directory)
- GitVCS (Repository operations only)
```

#### After
```markdown
**Tools:** FS (R/W), Bash (proj-dir), Git
```

### 5. Inline Formatting (25% reduction)

```markdown
# BEFORE (Multi-line)
**Description:** This agent specializes in API design
**Status:** Active
**Category:** Core Development
**Tools:**
  - FileSystem
  - CodeAnalyzer
  - BashExecutor

# AFTER (Inline)
**API Designer** | Active | Core-Dev | FS, CA, Bash
```

### 6. Hierarchical Nesting (Remove nested sections)

#### Before
```markdown
# Backend Developer

## Overview
[2 paragraphs]

## Capabilities
### Database Operations
[Paragraph]
### Server Configuration
[Paragraph]

## Tools
### Required
[List]
### Optional
[List]

## Integration
### Works With
[List]
```

#### After
```markdown
# Backend-Dev
**DB Ops, Server Config | Req:** FS, Bash, Git | **Opt:** Docker, Monitor
**Integrates:** api-designer, db-admin
```

## Compression Formula: 10k → 2.5k

### Step-by-Step Reduction

#### Step 1: Identify Redundancy (Remove 30%)
- Remove adjectives (e.g., "comprehensive", "specialized")
- Remove repetitive phrases
- Consolidate similar descriptions

**Example:**
```
Before: "This comprehensive Python expert provides advanced support"
After: "Python expert"

Reduction: 12 tokens → 3 tokens
```

#### Step 2: Convert to Structure (Remove 40%)
- Replace prose with tables
- Use inline formatting
- Create abbreviation system

#### Step 3: Consolidate Definitions (Remove 25%)
- Merge related sections
- Use bullet points instead of paragraphs
- Create reference lists

#### Step 4: Remove Redundant Metadata (Remove 20%)
- Abbreviate tool names
- Remove duplicate status fields
- Consolidate trigger lists

### Final Result Target
```markdown
Original: 10,000 tokens
After Step 1 (-30%): 7,000 tokens
After Step 2 (-40%): 4,200 tokens
After Step 3 (-25%): 3,150 tokens
After Step 4 (-20%): 2,520 tokens

Final: 2.5k tokens (75% reduction)
```

## Complete Optimization Template

### Minimalist AGENTS.md Structure
```markdown
# Agent Registry - Optimized

## Abbreviations
FS=FileSystem | Bash=BashExecutor | Git=GitVCS | CA=CodeAnalyzer
MC=MemoryCache | Req=Required | Opt=Optional | R/O=Read-Only

## Quick Reference

| Agent | Specialization | Triggers | Tools | Links |
|-------|---|---|---|---|
| api-designer | REST/GraphQL APIs | api, rest, graphql | FS, CA | [link] |
| backend-dev | Server/DB/Auth | backend, server, db | FS, Bash, Git | [link] |
| python-pro | Python projects | python, django | FS, Bash | [link] |
| security-rev | Vuln/Auth/Crypto | security, auth | FS, CA | [link] |

## Trigger Mapping
- **Backend:** api-designer, backend-dev
- **Python:** python-pro
- **Security:** security-rev, auth-expert
- **Infrastructure:** devops-pro, cloud-architect

## Tool Matrix
| Tool | Agents | Access |
|------|--------|--------|
| FS | All | R/O or R/W |
| Bash | 6 agents | Limited |
| Git | 8 agents | Read ops |
| Docker | 3 agents | Required |

## Agent Details (Expanded on Demand)

### api-designer.md
REST/GraphQL architects | Triggers: api,rest,graphql | Tools: FS,CA

### backend-dev.md
Server-side expert | Triggers: backend,server | Tools: FS,Bash,Git
```

## Technique-Specific Examples

### 1. Abbreviations in Action

#### Full Version (85 tokens)
```markdown
The Python-Pro agent provides comprehensive support for Python development
including web frameworks like Django and FastAPI, data analysis with pandas
and numpy, and automation tasks. It has full access to FileSystem for reading
and writing code, BashExecutor for running Python scripts, and GitVCS for
version control operations.
```

#### Abbreviated (18 tokens)
```markdown
**Python-Pro** | Web/Data/Auto | Django, FastAPI, Pandas
**Tools:** FS (R/W), Bash, Git
```

**Reduction:** 79%

### 2. Table Format Example

#### Prose (150 tokens)
```markdown
## Available Agents

The system includes the following agents:

### Python Expert
Specializes in Python development including web frameworks, data analysis,
and automation. Triggers include python, django, and fastapi keywords.

### JavaScript Expert
Focuses on JavaScript and TypeScript development including React, Node.js,
and frontend frameworks. Triggered by js, ts, and react keywords.

### DevOps Engineer
Handles infrastructure and deployment tasks including Docker, Kubernetes,
and CI/CD pipelines. Triggered by docker, k8s, and deploy keywords.
```

#### Table (42 tokens)
```markdown
| Agent | Focus | Triggers |
|-------|-------|----------|
| python-pro | Web/Data/Auto | python, django, fastapi |
| js-expert | Frontend/Backend | js, ts, react, node |
| devops-pro | Infrastructure | docker, k8s, deploy |
```

**Reduction:** 72%

### 3. Nested Consolidation

#### Before (Complex Nesting - 120 tokens)
```markdown
# Backend Developer

## Overview
Description...

## Specializations
### Database
Details...

### APIs
Details...

### Authentication
Details...

## Tools Access
### Required Tools
- FileSystem
- BashExecutor

### Optional Tools
- Docker
- GitVCS

## Integration Points
Works with other agents...
```

#### After (Flat Structure - 30 tokens)
```markdown
# Backend-Dev
**DB, APIs, Auth** | **Req:** FS, Bash | **Opt:** Docker, Git
**Integrates:** api-designer, db-admin, auth-expert
```

**Reduction:** 75%

## Practical Implementation

### Phase 1: Audit Current AGENTS.md
```bash
#!/bin/bash
# Count tokens in current file
wc -w ~/.claude/AGENTS.md  # Word count approximation

# Identify verbose sections
grep -E "comprehensive|provides support|including" ~/.claude/AGENTS.md
```

### Phase 2: Create Abbreviation System
```markdown
## Define in .claude/rules/abbreviations.md
- Create central abbreviation reference
- Distribute to all team members
- Version control abbreviations
```

### Phase 3: Implement Compression

#### Create Backup
```bash
cp ~/.claude/AGENTS.md ~/.claude/AGENTS.md.backup
```

#### Apply Optimization
1. Replace prose with structured data
2. Convert descriptions to inline format
3. Create summary table
4. Move detailed info to separate files

#### Validation
```bash
# Verify no information lost
# Check all agents still accessible
# Test trigger keywords work
# Measure token reduction
```

### Phase 4: Distribute Optimization

#### Store Detailed Info Separately
```
.claude/
├── AGENTS.md (optimized summary)
├── agents-detailed/
│   ├── api-designer.md
│   ├── backend-dev.md
│   └── ...
```

#### Cross-Reference System
```markdown
# AGENTS.md
| api-designer | REST/GraphQL APIs | [Details](agents-detailed/api-designer.md)

# agents-detailed/api-designer.md
[Full detailed information when needed]
```

## Token Audit Checklist

Before deploying optimization:

- [ ] Word count reduced by 75% (10k → 2.5k)
- [ ] All agent information preserved
- [ ] Triggers remain complete
- [ ] Tools accurately listed
- [ ] Integration points clear
- [ ] All agents still searchable
- [ ] Abbreviations documented
- [ ] Links resolve correctly
- [ ] Backup created
- [ ] Team trained on new format

## Advanced Optimization

### Dynamic Agent Loading
Instead of static file, generate summary:
```bash
#!/bin/bash
# Generate optimized AGENTS.md from agents/
for agent in .claude/agents/*.md; do
  name=$(basename "$agent" .md)
  triggers=$(grep "Triggers:" "$agent" | cut -d: -f2)
  echo "| $name | ... | $triggers |"
done > .claude/AGENTS.md.generated
```

### Hierarchical Loading
```markdown
# Load agents on-demand
## Quick View (compressed summary)
## Detailed View (full specifications)
## Tool Matrix (reference)
```

## Maintenance & Versioning

### Updating Optimized Files
```markdown
Process:
1. Edit detailed agent file
2. Extract summary to AGENTS.md
3. Update abbreviations if needed
4. Regenerate tables
5. Validate compression ratio
```

### Compression Ratio Tracking
```
Version | Tokens | Reduction | Date
v1.0    | 10000  | baseline  | 2026-03-01
v1.1    | 5000   | 50%       | 2026-03-05
v2.0    | 2500   | 75%       | 2026-03-16
```

## Common Pitfalls to Avoid

1. **Over-compression** - Don't lose critical trigger keywords
2. **Inconsistent abbreviations** - Use defined abbreviations consistently
3. **Missing relationships** - Document agent integrations
4. **Stale data** - Keep detailed files synchronized
5. **Poor discoverability** - Maintain searchable format

## Related Skills
- agent-config
- claude-rules
- documentation-engineer
