---
name: skill-catalog
description: Searchable index of all available skills. Shows overview of all skills categorized by domain. Use when user asks "show my skills", "what skills do I have", "zeige mir die Skills".
---

# Skill Catalog - All Available Skills

Complete overview of all skills in your workspace.

## Core System Skills (Always Active)

### 🎯 workflow.skill
**Purpose:** Complete project workflow from inception to production
**Triggers:** Starting new project, "show me the workflow"
**Contains:**
- Phase 0: Inception (Wingman → Architect → Designer → Planner)
- Phase 1-7: Execution with Phase-Gates
- Change Request & Restart Process
- Cascade Re-Validation
- All Freeze Points

### 🔒 mandatory-rules.skill
**Purpose:** 27 unverhandelbare Pflicht-Regeln
**Triggers:** Always active - applies to ALL agents
**Contains:**
- Approval & Gates (Regeln 1-4)
- Quality & Testing (Regeln 5-9)
- Kommunikation (Regeln 10-13)
- Enforcement (Regeln 14-16)
- Production-Level Quality (Regel 17)
- Dokumentations-Archivierung (Regel 18)
- Cross-Project Learning (Regeln 21-24)
- Dokumentations-Kategorien (Regel 25)
- Scope Freeze (Regel 26)
- Cascade Re-Validation (Regel 27)

### 🎭 character-profiles.skill
**Purpose:** All agent modes/roles
**Triggers:** "Mode [profile]", "arbeite als [profile]"
**Profiles:**
- 🤝 Wingman (Requirements Gatherer)
- 🏗️ Architect (System Designer)
- 🎨 Designer (UI/UX Designer)
- 📋 Planner (Project Orchestrator)
- 💻 Developer (Implementer)
- 🔧 DevOps (Infrastructure Engineer)
- 🧪 Tester (Quality Assurance)
- 🔍 Reviewer (Code Reviewer)
- 🔐 Security Engineer (Security Specialist)
- 🔗 Integration Specialist (API Integrator)
- + Additional profiles

### 📋 skill-catalog.skill
**Purpose:** This skill - overview of all skills
**Triggers:** "Show my skills", "what skills do I have"

---

## Public Skills (Available from Claude)

### 📄 docx (Document Creation)
**Purpose:** Create, read, edit Word documents
**Triggers:** "create word doc", ".docx", "document"
**Use for:** Reports, memos, letters, templates

### 📑 pdf (PDF Handling)
**Purpose:** Read, extract, merge, split PDFs
**Triggers:** "pdf", "read PDF", "merge PDFs"
**Use for:** PDF manipulation, form filling, OCR

### 📊 pptx (Presentations)
**Purpose:** Create, read, edit presentations
**Triggers:** "presentation", "slides", ".pptx"
**Use for:** Slide decks, pitch decks

### 📈 xlsx (Spreadsheets)
**Purpose:** Create, read, edit spreadsheets
**Triggers:** ".xlsx", "spreadsheet", "excel"
**Use for:** Data analysis, tables, charts

### 🎨 frontend-design (UI Design)
**Purpose:** Create distinctive, production-grade frontend interfaces
**Triggers:** "build web component", "landing page", "website"
**Use for:** Web design, React components, HTML/CSS

### 🔧 product-self-knowledge (Anthropic Product Info)
**Purpose:** Up-to-date info about Claude products
**Triggers:** Questions about Claude API, Claude Code, pricing
**Use for:** Claude product questions, API documentation

---

## Example Skills (Optional Templates)

### 📝 doc-coauthoring
**Purpose:** Structured workflow for documentation
**Use for:** Writing specs, proposals, decision docs

### 🌐 web-artifacts-builder
**Purpose:** Complex multi-component HTML artifacts
**Use for:** Elaborate web applications with state management

### 🛠️ skill-creator
**Purpose:** Guide for creating effective skills
**Use for:** Creating new custom skills

### 🔌 mcp-builder
**Purpose:** Guide for creating MCP servers
**Use for:** Building Model Context Protocol integrations

### 🎨 canvas-design
**Purpose:** Create beautiful visual art in PNG/PDF
**Use for:** Posters, designs, static art pieces

### 🎨 algorithmic-art
**Purpose:** Create algorithmic art using p5.js
**Use for:** Generative art, flow fields, particle systems

---

## How to Use Skills

### Automatic Triggering
Skills trigger automatically based on:
- Task type (e.g., creating a Word doc triggers docx skill)
- Keywords in your request
- Work phase (e.g., project start triggers Wingman)

### Manual Activation
Explicitly call a skill:
- "Use workflow skill"
- "Mode Wingman"
- "Arbeite mit docx skill"

### Skill Combinations
Multiple skills can work together:
- character-profiles + workflow + mandatory-rules
- docx + frontend-design (for documentation with UI)
- xlsx + pptx (for data analysis + presentation)

---

## Skill Management

### Viewing Skills
- "Show my skills" → Triggers this catalog
- "What skills do I have?"
- "Zeige mir alle Skills"

### Adding Skills
- Settings → Skills → Upload Skill
- Upload .skill files

### Removing Skills
- Settings → Skills → Manage
- Deactivate or delete skills

---

## Recommended Skill Sets

### For New Projects
- ✅ workflow.skill
- ✅ mandatory-rules.skill
- ✅ character-profiles.skill
- ✅ doc-coauthoring (optional)

### For Web Development
- ✅ frontend-design
- ✅ web-artifacts-builder (complex apps)

### For Documentation
- ✅ docx
- ✅ pdf
- ✅ pptx
- ✅ doc-coauthoring

### For Design Work
- ✅ frontend-design
- ✅ canvas-design
- ✅ algorithmic-art

---

## Questions?

**To see details of a specific skill:**
"Tell me more about [skill-name] skill"

**To use a specific skill:**
"Use [skill-name] skill for [task]"

**To create a new skill:**
"Help me create a new skill for [purpose]"
(Uses skill-creator skill)
