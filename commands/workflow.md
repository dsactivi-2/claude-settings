---
name: workflow
description: Complete project workflow from inception to production. Defines all phases, gates, agent transitions, and quality checkpoints. Use this skill whenever starting a new project or when user asks about the overall process.
---

# Complete Project Workflow

This skill defines the complete workflow for all software development projects, from initial idea to production launch.

## Overview

The workflow consists of two main parts:
1. **PHASE 0: INCEPTION** - Requirements gathering and design (before any development)
2. **PHASE 1-7: EXECUTION** - Actual development with strict quality gates

```
PROJECT START
     ↓
PHASE 0: INCEPTION
  🤝 Wingman → 🏗️ Architect → 🎨 Designer → 📋 Planner
  [User Approvals Required at Each Step]
     ↓
  🔒 SCOPE FREEZE ACTIVATED
     ↓
PHASE 1-7: EXECUTION
  💻 Developer │ 🔧 DevOps │ 🧪 Tester │ 🔐 Security
  [Quality Gates at Each Phase]
     ↓
PRODUCTION LAUNCH 🚀
```

---

## PHASE 0: INCEPTION (Before Development)

### Step 1: 🤝 WINGMAN (Requirements Gathering)

**Duration:** 2-5 days

**Purpose:** Extract and clarify ALL requirements from the user

**Process:**
1. Ask clarifying questions (ONE at a time)
2. Gather requirements:
   - Core purpose
   - Functional requirements
   - Technical context
   - Constraints & priorities
3. Synthesize understanding
4. Present summary: "Habe ich das richtig verstanden?"
5. Wait for confirmation
6. Create detailed briefing

**Documentation Created:**
- ✅ User Interview Notes
- ✅ Requirements Gathered
- ✅ Briefing Document (Final)
- 📋 NICE-TO-HAVE consultation (user decides)
- 📋 NOT-NECESSARY consultation (user decides)

**Output:** Complete Requirements Briefing

**Gate:** ⏸️ USER APPROVAL REQUIRED
- User must say: "bestätige" / "confirm" / "approved"
- ❌ Cannot proceed without explicit confirmation
- "ok", "ja", "gut" is NOT sufficient!

**Location in Wissensdatenbank:**
```
/wissensdatenbank/projekte/[projekt]/00-inception/wingman/
```

---

### Step 2: 🏗️ ARCHITECT (System Design)

**Duration:** 5-10 days

**Purpose:** Design complete system architecture

**Input:** Approved Briefing from Wingman

**Process:**
1. Analyze requirements
2. Design complete system architecture:
   - High-level architecture
   - Component breakdown
   - Technology stack (with rationale)
   - Data architecture
   - API design
   - Security architecture
   - Deployment architecture
   - Monitoring & observability
   - Scalability strategy
   - Integration points
   - Disaster recovery
3. Define Non-Functional Requirements (NFRs)
4. Create Technical Playbooks (minimum 6):
   - Agent Deployment Playbook
   - Database Migration Playbook
   - Incident Response Playbook
   - Performance Optimization Playbook
   - Security Audit Playbook
   - Developer Onboarding Playbook
5. Create Infrastructure as Code templates
6. Document API specifications
7. Explain design to user (in understandable terms)
8. Answer user questions

**Documentation Created:**
- ✅ System Architecture Document (45+ pages)
- ✅ Non-Functional Requirements
- ✅ Technical Playbooks (6+)
- ✅ Infrastructure as Code Templates
- ✅ API Specifications
- 📋 NICE-TO-HAVE consultation
- 📋 NOT-NECESSARY consultation

**Output:** Complete Architecture Package

**Gate:** ⏸️ USER APPROVAL REQUIRED
- Architect MUST explain design clearly
- User must understand and approve
- User must say: "bestätige" / "confirm" / "approved"
- ❌ Cannot proceed without explicit confirmation
- ⚠️ If user wants changes: Re-design → Re-present

**Location in Wissensdatenbank:**
```
/wissensdatenbank/projekte/[projekt]/00-inception/architect/
```

---

### Step 3: 🎨 DESIGNER (Complete UI/UX Design)

**Duration:** 10-15 days

**Purpose:** Create COMPLETE visual and functional design for ENTIRE project

**Input:** Approved Architecture from Architect

**Process:**
1. Analyze architecture for UI/UX needs
2. Create COMPLETE Design System:
   - Brand identity (colors, typography, logo)
   - Component library (all components, all states)
   - Layout system (grid, spacing, breakpoints)
   - Interaction patterns
   - Accessibility standards (WCAG 2.1 AA)
3. Design EVERY Screen:
   - All main screens
   - All modals/dialogs
   - All states (loading, empty, error, success)
   - All responsive breakpoints (mobile, tablet, desktop)
4. Document EVERY User Flow:
   - Step-by-step with designs
   - All edge cases
   - All error scenarios
5. Specify EVERY Component:
   - Visual designs
   - Technical specs (CSS, behavior)
   - All variants, sizes, states
   - Accessibility specs
6. Create Interactive Prototypes
7. Define all Animations/Interactions

**Documentation Created (MUST-HAVE + GOOD-TO-HAVE):**
- ✅ Design System Documentation
- ✅ All Screen Designs (23+ screens)
- ✅ All User Flows (9+ flows)
- ✅ Component Specifications (45+ components)
- ✅ Responsive Designs (all breakpoints)
- ✅ Accessibility Guidelines
- ✅ Interactive Prototypes
- ✅ Animation Specifications
- ✅ Loading & Empty States
- ✅ Style Guide PDF
- ✅ Icon Library
- ✅ UI Kit (Figma)

**User Consultation (REQUIRED):**

**NICE-TO-HAVE List:**
- Dark Mode Designs
- Onboarding Flow
- Advanced Animations
- Illustration Set
- Landing Page Design

**NOT-NECESSARILY-REQUIRED List:**
- 3D Assets
- Video Explainers
- Print Materials
- Social Media Assets
- Swag/Merchandise

User decides which to include.

**Output:** Complete Design Package

**Gate:** ⏸️ USER APPROVAL REQUIRED
- Designer presents complete design
- User reviews all screens, flows, components
- User must say: "bestätige Design" / "approve Design"
- ❌ Cannot proceed without explicit confirmation
- ⚠️ If user wants changes: Re-design → Re-present

**🔒 AFTER APPROVAL: DESIGN FREEZE ACTIVATED**
- No design changes allowed (except functionality broken)
- Enforced by ALL agents
- User is ALSO bound by this freeze!

**Location in Wissensdatenbank:**
```
/wissensdatenbank/projekte/[projekt]/00-inception/designer/
```

---

### Step 4: 📋 PLANNER (Execution Planning)

**Duration:** 3-5 days

**Purpose:** Create complete execution plan for entire project

**Input:** Approved Architecture + Approved Design

**Process:**
1. Analyze Architecture + Design
2. Break down into 7 Phases:
   - Phase 1: Foundation & Setup (Week 1-2)
   - Phase 2: Core Backend (Week 3-5)
   - Phase 3: Agent Service (Week 6-8)
   - Phase 4: Frontend & Real-time (Week 9-11)
   - Phase 5: Monitoring & Observability (Week 12-13)
   - Phase 6: Testing & Hardening (Week 14-15)
   - Phase 7: Production Deployment (Week 16)
3. Break each Phase into Tasks
4. Break each Task into Subtasks
5. Define Acceptance Criteria for each
6. Assign to Agent Modes:
   - 💻 Developer (42 tasks)
   - 🔧 DevOps (28 tasks)
   - 🧪 Tester (15 tasks)
   - 🎨 Designer (8 tasks - support)
   - 🔐 Security Engineer (6 tasks)
   - 🔗 Integration Specialist (5 tasks)
7. Create Dependency Graph
8. Create Timeline (Gantt)
9. Define Phase-Gate criteria (for each phase)
10. Define Daily Standup structure
11. Define Quality Gates

**Documentation Created:**
- ✅ Execution Plan (80+ pages)
- ✅ Task Breakdown (105 tasks)
- ✅ Agent Assignment Matrix
- ✅ Dependency Graph
- ✅ Timeline & Milestones (Gantt)
- ✅ Phase-Gate Definitions
- ✅ Daily Standup Templates
- 📋 NICE-TO-HAVE consultation
- 📋 NOT-NECESSARY consultation

**Output:** Complete Execution Plan

**Gate:** ⏸️ USER APPROVAL REQUIRED
- Planner presents complete plan
- User reviews timeline, resources, approach
- User must say: "bestätige Plan" / "approve Plan"
- ❌ Cannot proceed without explicit confirmation
- ⚠️ If user wants changes: Re-plan → Re-present

**🔒 AFTER APPROVAL: ABSOLUTE SCOPE FREEZE ACTIVATED**
- NOTHING can be changed, added, or removed
- ONLY exception: Functionality broken (with Change Request)
- User, Owner, ALL Agents bound to this freeze!
- **This is the MOST CRITICAL freeze point!**

**Location in Wissensdatenbank:**
```
/wissensdatenbank/projekte/[projekt]/00-inception/planner/
```

---

## PHASE 1-7: EXECUTION (Development)

Each phase follows the SAME structure (Phase-Gate Methodology):

### Phase Structure (Applied to ALL 7 Phases)

```
┌─────────────────────────────────────────────────────────┐
│ PHASE [N]: [Name]                                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Step 1: DEVELOPMENT                                     │
│ Step 2: COMPREHENSIVE TESTING                           │
│ Step 3: CODE REVIEW (100% Coverage)                    │
│ Step 4: BUG FIXING (Zero Tolerance)                    │
│ Step 5: DOCUMENTATION UPDATE                            │
│ Step 6: REVIEW MEETING                                  │
│ Step 7: PHASE SIGN-OFF                                 │
│                                                          │
│ ✅ Phase Gate: 100% Complete or BLOCKED                │
└─────────────────────────────────────────────────────────┘
```

---

#### Step 1: DEVELOPMENT

**Agents working in parallel (as per plan):**

**💻 DEVELOPER**
- Implements features EXACTLY as designed
- Follows OTOP standards
- Writes tests (80%+ coverage required)
- Documents code
- ❌ NO design decisions
- ❌ NO scope changes
- Daily: Task progress, blockers, documentation

**🔧 DEVOPS**
- Deploys infrastructure as designed
- Configures CI/CD
- Sets up monitoring
- Manages secrets/security
- ❌ NO architecture changes
- Daily: Infrastructure status, deployments, issues

**🎨 DESIGNER (Support)**
- Clarifies design questions
- Provides assets
- ❌ NO design changes (frozen!)
- Only: Critical bug fixes if functionality broken

**🔗 INTEGRATION SPECIALIST (when needed)**
- Implements integrations as designed
- API connections
- ❌ NO scope changes

**📋 PLANNER (Coordinator)**
- Daily standups
- Tracks progress
- Manages blockers
- Coordinates agents
- Enforces scope freeze
- Weekly reports

**Documentation During Development:**
- ✅ Task completion docs (after EACH task)
- ✅ Code commits log
- ✅ Progress updates
- ✅ Blocker documentation
- ✅ Daily standup notes

**Status:** All tasks for this phase COMPLETE

---

#### Step 2: COMPREHENSIVE TESTING

**🧪 TESTER**

Runs ALL test categories for this phase:
- ✅ Unit Tests (80%+ coverage)
- ✅ Integration Tests
- ✅ E2E Tests (if applicable)
- ✅ API Tests
- ✅ Performance Tests
- ✅ Security Tests
- ✅ Accessibility Tests (if UI)
- ✅ Load Tests (if applicable)
- ✅ Regression Tests

**Goal:** 100% Test Pass Rate

**Rules:**
- ❌ NO "design feedback" (design is frozen)
- ✅ ONLY functional bugs reported

**Documentation:**
- ✅ Test Plan
- ✅ Test Results (all categories)
- ✅ Test Coverage Report
- ✅ Bug Reports (if any found)

**Status:** All tests PASSED, Coverage >= 80%

---

#### Step 3: CODE REVIEW (100% Coverage)

**🔍 REVIEWER**

Reviews 100% of code for this phase:
- ✅ Repository Structure
- ✅ Code Quality
- ✅ Architecture Compliance
- ✅ Design Compliance
- ✅ OTOP Standards Compliance
- ✅ Security Checklist
- ✅ Performance Considerations
- ✅ Error Handling
- ✅ Documentation Quality

**🔐 SECURITY ENGINEER (if applicable)**

Security-focused review:
- ✅ Vulnerability Scan
- ✅ OWASP Top 10 Check
- ✅ Dependency Scan
- ✅ Security Best Practices

**Documentation:**
- ✅ Code Review Checklists (completed)
- ✅ Review Findings
- ✅ Review Issues (if any)

**Status:** All code reviewed, all issues addressed

---

#### Step 4: BUG FIXING (Zero Tolerance)

**💻 DEVELOPER + 🧪 TESTER**

Fix ALL bugs found:
- 🔴 Critical bugs MUST be fixed
- 🔴 Major bugs MUST be fixed
- 🟡 Minor bugs MUST be fixed OR documented/accepted

**🚫 Phase CANNOT proceed with open Critical/Major bugs**

**Documentation:**
- ✅ Bug Tracking Log
- ✅ Bug Reports (detailed)
- ✅ Bug Resolutions
- ✅ Regression tests added

**Status:** ZERO Critical/Major bugs

---

#### Step 5: DOCUMENTATION UPDATE

**ALL AGENTS update their documentation:**
- ✅ Architecture docs (if affected)
- ✅ Design docs (if affected)
- ✅ API documentation (current)
- ✅ Deployment guide (updated)
- ✅ Developer guide (updated)
- ✅ Lessons learned (documented)
- ✅ All links validated
- ✅ All examples tested

**Status:** All documentation CURRENT

---

#### Step 6: REVIEW MEETING

**📋 PLANNER facilitates meeting**

**Present:**
- Demo of completed functionality
- Test results (all passing)
- Code review results (all approved)
- Bug status (zero critical/major)
- Documentation updates
- Metrics:
  - Planned vs Actual time
  - Test coverage
  - Code quality metrics
  - Bugs found/fixed
- Lessons learned
- Risks for next phase

**Documentation:**
- ✅ Review Meeting Notes
- ✅ Demo Recording/Screenshots
- ✅ Stakeholder Feedback
- ✅ Metrics Report

**Status:** Meeting held, feedback received

---

#### Step 7: PHASE SIGN-OFF

**ALL Stakeholders must sign-off:**
- ✅ Developer Sign-Off
- ✅ DevOps Sign-Off
- ✅ Tester Sign-Off
- ✅ Reviewer Sign-Off
- ✅ Security Sign-Off (if applicable)
- ✅ USER/OWNER Sign-Off

**Documentation:**
- ✅ Sign-Off Document (all signatures)
- ✅ Phase Completion Certificate

---

### ⏸️ PHASE GATE: PROCEED TO NEXT PHASE?

**Checklist MUST be 100% complete:**
- ✅ All tasks complete
- ✅ All tests passed (100%)
- ✅ All code reviewed (100%)
- ✅ All bugs fixed (Critical/Major = 0)
- ✅ All docs updated
- ✅ Review meeting held
- ✅ All sign-offs obtained

**If ALL ✅:** Proceed to next phase
**If ANY 🔴:** BLOCKED - fix issues, re-gate

**🎯 PHASE [N] COMPLETE - PROCEED TO PHASE [N+1]**

---

## The 7 Execution Phases

### Phase 1: Foundation & Setup (Week 1-2)
**Focus:** Infrastructure, CI/CD, Development Environment

**Key Tasks:**
- Repository Setup
- CI/CD Pipeline
- Dev Environment
- Staging Infrastructure
- Basic Monitoring

**Agents:** Developer, DevOps

---

### Phase 2: Core Backend (Week 3-5)
**Focus:** Database, API, Core Business Logic

**Key Tasks:**
- Database Schema Implementation
- API Framework Setup
- Agent CRUD Operations
- Deployment Endpoints
- Log Streaming
- Metrics Collection

**Agents:** Developer, DevOps, Tester

---

### Phase 3: Agent Service (Week 6-8)
**Focus:** Agent Management, Docker, ECS Deployment

**Key Tasks:**
- Agent Management Service
- Docker Image Build
- ECS Deployment
- Status Monitoring
- Emir-Superman Integration

**Agents:** Developer, DevOps, Integration Specialist, Tester

---

### Phase 4: Frontend & Real-time (Week 9-11)
**Focus:** UI Implementation, WebSocket, Dashboard

**Key Tasks:**
- Frontend Framework Setup
- Component Implementation
- WebSocket Integration
- Dashboard Implementation
- Responsive Design Implementation

**Agents:** Developer, Designer (support), Tester

---

### Phase 5: Monitoring & Observability (Week 12-13)
**Focus:** Prometheus, Grafana, ELK, Alerts

**Key Tasks:**
- Prometheus Setup
- Grafana Dashboards
- ELK Stack Setup
- Alert Configuration
- Performance Monitoring

**Agents:** DevOps, Developer, Tester

---

### Phase 6: Testing & Hardening (Week 14-15)
**Focus:** Comprehensive Testing, Security, Performance

**Key Tasks:**
- Integration Testing (comprehensive)
- Load Testing
- Security Testing & Audit
- Performance Optimization
- Penetration Testing
- Bug Fixing (final)

**Agents:** Tester, Security Engineer, Developer, DevOps

---

### Phase 7: Production Deployment (Week 16)
**Focus:** Production Infrastructure, Go-Live

**Key Tasks:**
- Production Infrastructure (Terraform)
- Production Deployment
- Smoke Tests
- DNS & SSL Configuration
- Monitoring Validation
- Documentation (final)
- 🚀 GO LIVE!

**Agents:** DevOps, Developer, Tester, ALL (final checks)

---

## 🔒 CRITICAL FREEZE POINTS

### 🔒 FREEZE POINT 1: Design Freeze

**When:** User says "bestätige Design"

**What:** Design is LOCKED

**Locked:**
- ❌ No design changes
- ❌ No color changes
- ❌ No layout changes
- ❌ No component changes

**Exception:** Only if functionality broken

**Enforced By:** Designer, Planner, Developer, Tester, ALL

**Bound:** Everyone (incl. User/Owner)

---

### 🔒 FREEZE POINT 2: Scope Freeze (MOST CRITICAL!)

**When:** User says "bestätige Plan"

**What:** ABSOLUTE SCOPE FREEZE

**Locked:**
- ❌ NOTHING can be changed
- ❌ NOTHING can be added
- ❌ NOTHING can be removed
- ❌ NO exceptions (except functionality broken)

**Exception:** ONLY "Funktionalität verhindert" via Change Request

**Enforced By:** ALL Agents + Planner (Gatekeeper)

**Bound:** Everyone (incl. User/Owner!)

**Most Critical:** This prevents ALL scope creep

---

### 🔒 FREEZE POINT 3: Each Phase Gate

**When:** End of each phase

**What:** Phase cannot proceed until 100% complete

**Requirements:**
- ✅ All tasks complete
- ✅ All tests passed (100%)
- ✅ All code reviewed (100%)
- ✅ Zero Critical/Major bugs
- ✅ All docs updated
- ✅ Review meeting held
- ✅ All sign-offs obtained

**Enforced By:** Planner (Gate Keeper)

**Consequence:** If any ❌, phase BLOCKED until fixed

---

## Change Request & Restart Process

### When is Change Request allowed?

**ONLY when "Funktionalität verhindert":**
1. Implementation as planned is TECHNICALLY IMPOSSIBLE
2. Implementation would cause CRITICAL BUG
3. External dependency is not available

**NOT allowed for:**
- "Better performance"
- "Better design"
- "User would prefer"
- "Difficult to implement"
- "Taking longer than expected"

### Change Request Process

```
1. Problem discovered (e.g., in Phase 5)
   ↓
2. Create Change Request
   - Problem description
   - Why it prevents functionality
   - Alternatives evaluated
   ↓
3. Escalation Chain
   Developer → Planner → Architect → Designer → User
   ↓
4. Decision:
   - Minimal Change (if possible)
   - RESTART (if fundamental)
   - Reject (if not really necessary)
   ↓
5. IF RESTART:
   ↓
6. Project PAUSE
   ↓
7. Return to Architect/Designer/Planner
   - Re-design
   - Re-plan
   - User Approvals required
   ↓
8. CASCADE RE-VALIDATION (CRITICAL!)
   ⚠️ NOT back to Phase 5!
   ✅ Back to Phase 1!
   ↓
9. Phase 1: Assess & re-validate (if affected)
   - COMPLETE re-validation
   - All tests again
   - All reviews again
   - New sign-offs
   ↓
10. Phase 2: Assess & re-validate (if affected)
    ↓
11. Phase 3: Assess & re-validate (if affected)
    ↓
12. Phase 4: Assess & re-validate (if affected)
    ↓
13. Back to Phase 5 with validated foundation
    ↓
14. Continue Execution
```

### Why Cascade Re-Validation?

**Quality Guarantee:**
- ✅ No hidden bugs from old implementation
- ✅ Architecture change properly propagated
- ✅ All foundations re-validated
- ✅ Quality maintained throughout
- ✅ Future phases built on solid base

**Timeline Impact:**
- Significant additional time required
- But necessary for quality!
- User MUST accept realistic timeline

---

## Documentation Flow

**Everything is documented at EVERY step:**

```
/wissensdatenbank/projekte/[project-name]/
├── 00-inception/
│   ├── wingman/
│   ├── architect/
│   ├── designer/
│   └── planner/
│
├── 01-phase1-foundation/
│   ├── plan/
│   ├── development/ (after EACH task)
│   ├── testing/ (all test results)
│   ├── review/ (all reviews)
│   ├── bugs/ (bug tracking)
│   ├── documentation/ (updated docs)
│   ├── metrics/ (phase metrics)
│   └── sign-off/ (all approvals)
│
├── 02-phase2-backend/
│   └── [same structure]
│
├── [03-07 same structure]
│
├── daily-standups/ (EVERY DAY!)
├── weekly-reports/ (EVERY WEEK!)
├── incidents/ (if any)
│
├── restart-XXX/ (if restart happens)
│   ├── change-request.md
│   ├── impact-assessment-matrix.md
│   ├── cascade-plan.md
│   ├── phase-re-validations/
│   └── restart-completion.md
│
└── project-summary/ (at the end)
    ├── final-architecture.md
    ├── timeline-actual-vs-planned.md
    ├── lessons-learned-complete.md
    └── retrospective.md
```

---

## Timeline Example (16-Week MVP)

```
Week 1-2:   INCEPTION (Wingman, Architect)
Week 3-4:   INCEPTION (Designer, Planner)
            🔒 SCOPE FREEZE ACTIVATED

Week 5-6:   Phase 1 - Foundation & Setup
Week 7-9:   Phase 2 - Core Backend
Week 10-12: Phase 3 - Agent Service
Week 13-15: Phase 4 - Frontend & Real-time
Week 16-17: Phase 5 - Monitoring
Week 18-19: Phase 6 - Testing & Hardening
Week 20:    Phase 7 - Production Deployment
            🚀 GO LIVE!

Total: ~20 weeks (with buffers)
```

---

## Success Criteria

**Project is successful when:**
- ✅ All 7 phases completed with sign-offs
- ✅ Zero Critical/Major bugs in production
- ✅ All documentation current and complete
- ✅ All acceptance criteria met
- ✅ Production deployment successful
- ✅ Monitoring and alerts operational
- ✅ User/Owner satisfied with delivery

**Quality Metrics:**
- Test Coverage: >= 80%
- Code Review: 100%
- Documentation: Current
- Bugs in Production: 0 Critical/Major
- Downtime during deployment: 0

---

## Key Principles

1. **Quality First, Always**
   - Never compromise quality for speed
   - Scope reduction over quality reduction

2. **User Approval Gates are Sacred**
   - No phase transition without explicit "bestätige"
   - "ok" or "ja" is NOT sufficient

3. **Scope Freeze is Absolute**
   - After Planner approval: NO changes
   - Everyone is bound (including User/Owner)
   - Only exception: Functionality broken

4. **Documentation is NOT Optional**
   - After EVERY step
   - ALL categories (Standard, MUST-HAVE, GOOD-TO-HAVE, NICE-TO-HAVE, NOT-NECESSARY)
   - Long-term storage in Wissensdatenbank

5. **Phase Gates are Enforced**
   - 100% complete or BLOCKED
   - No shortcuts
   - Zero tolerance for Critical/Major bugs

6. **Cascade Re-Validation on Restart**
   - NOT back to current phase
   - Back to Phase 1
   - All affected phases COMPLETELY re-validated

7. **Production-Level Quality EVERY Phase**
   - Each phase treated as production-ready
   - No "we'll fix it later"
   - No technical debt

---

## When to Use This Workflow

**Use this workflow for:**
- ✅ All new software development projects
- ✅ Major feature additions (requiring Inception)
- ✅ Architecture changes
- ✅ Platform migrations

**Do NOT use for:**
- ❌ Minor bug fixes
- ❌ Small improvements
- ❌ Hotfixes
- ❌ Maintenance tasks

(These follow simplified processes)

---

## Related Skills

This workflow integrates with:
- **mandatory-rules.skill** - All 27 rules that govern this workflow
- **character-profiles.skill** - All agent roles and their responsibilities
- **skill-catalog.skill** - Overview of all available skills

---

## Questions?

If unclear about any step in the workflow:
1. Refer to mandatory-rules.skill for detailed rules
2. Refer to character-profiles.skill for agent-specific guidance
3. Ask the user for clarification
4. When in doubt: Follow the quality-first principle

**Remember:** This workflow exists to ensure ZERO bugs in production and maximum quality. Every step, gate, and rule has a purpose.
