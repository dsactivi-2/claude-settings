# Claude Rules - .claude/rules/ Structure & Conventions

## Overview
This skill provides comprehensive guidance on organizing and implementing Claude Code rules through the `.claude/rules/` directory structure, following established conventions and best practices.

## Directory Structure

### Base Layout
```
.claude/
├── rules/
│   ├── README.md (rules index)
│   ├── core/
│   │   ├── mandatory-rules.md
│   │   ├── safety-guardrails.md
│   │   └── error-handling.md
│   ├── code-quality/
│   │   ├── formatting.md
│   │   ├── naming-conventions.md
│   │   ├── patterns.md
│   │   └── anti-patterns.md
│   ├── security/
│   │   ├── secrets-management.md
│   │   ├── input-validation.md
│   │   ├── authentication.md
│   │   └── authorization.md
│   ├── performance/
│   │   ├── optimization-rules.md
│   │   ├── caching-strategy.md
│   │   └── resource-limits.md
│   ├── testing/
│   │   ├── test-structure.md
│   │   ├── coverage-requirements.md
│   │   └── test-naming.md
│   ├── documentation/
│   │   ├── doc-standards.md
│   │   ├── comment-conventions.md
│   │   └── api-documentation.md
│   └── git/
│       ├── commit-conventions.md
│       ├── branch-strategy.md
│       └── pr-standards.md
```

## Naming Conventions

### File Naming
```
Rule files: [domain]-[purpose].md
Examples:
- mandatory-rules.md
- secrets-management.md
- commit-conventions.md
```

### Directory Naming
```
Use lowercase hyphenated names:
- core/
- code-quality/
- security/
- performance/
- testing/
- documentation/
- git/
```

### Rule Identifiers
```
Format: [CATEGORY].[NUMBER] or [CATEGORY].[SUBCATEGORY]
Examples:
- CORE.001 - Mandatory safety check
- SEC.001 - Secrets never committed
- PERF.001 - Cache optimization
```

## Rule File Format

### Header Section
```markdown
# Rule Title: [Descriptive Name]

**Category:** [Category]
**Priority:** [Critical|High|Medium|Low]
**Version:** [version]
**Last Updated:** [date]
**Status:** [Active|Deprecated|Draft]

## Quick Reference
[One-line summary]
```

### Full Structure
```markdown
# Rule Title

**Category:** core
**Priority:** Critical
**Status:** Active

## Description
Clear explanation of the rule and its purpose.

## Application
When and where this rule applies:
- [ ] Development phase
- [ ] Review phase
- [ ] Pre-commit
- [ ] Pre-deployment

## Specifications

### Requirement
Specific requirement or constraint.

### Examples
```code
// Good
[example]

// Bad
[counter-example]
```

## Implementation

### Automated Enforcement
- Tool: [e.g., linter, hook]
- Command: [how to run]
- Fix: [how to fix]

### Manual Check
- Review process
- Verification steps

## Related Rules
- RULE.001
- RULE.002

## References
- [Link to docs]
```

## Core Rules Categories

### 1. Mandatory Rules (core/)

**CORE.001 - Secrets Protection**
```markdown
# Rule: Never Commit Secrets
Priority: Critical

Secrets (API keys, passwords, tokens) must NEVER be committed.

Application:
- Pre-commit hook (block-secrets-in-code.sh)
- Code review
- Repository scanning

Detection Pattern:
- Private keys: -----BEGIN PRIVATE KEY-----
- AWS keys: AKIA[0-9A-Z]{16}
- API keys: [service]_[key_pattern]
- Tokens: Bearer|token=

Automated: ✅ Pre-commit hook enforces
Manual: ✅ Code review verification
```

**CORE.002 - Error Handling**
```markdown
# Rule: Explicit Error Handling
Priority: High

All operations must have explicit error handling.

Requirements:
- Try-catch for async operations
- Error logging
- User-friendly messages
- Proper error propagation
```

**CORE.003 - Code Review**
```markdown
# Rule: Pre-merge Code Review
Priority: High

All code changes require review before merge.

Requirements:
- Minimum 1 reviewer
- Tests pass
- No conflicts
- CI/CD green
```

### 2. Code Quality Rules (code-quality/)

**CQ.001 - Naming Conventions**
```markdown
# Rule: Consistent Naming
Priority: Medium

Components: PascalCase (React, classes)
Functions: camelCase
Constants: UPPER_SNAKE_CASE
Files: kebab-case

Examples:
✓ UserProfile.tsx
✓ getUserData()
✓ API_KEY
✓ user-service.ts
```

**CQ.002 - File Organization**
```markdown
# Rule: File Structure Pattern
Priority: Medium

Pattern:
├── domain/
│   ├── types/
│   ├── services/
│   ├── components/
│   ├── hooks/
│   ├── utils/
│   └── __tests__/
```

**CQ.003 - Import Organization**
```markdown
# Rule: Import Sorting
Priority: Low

Order:
1. External packages
2. Relative paths
3. Type imports

Use eslint-plugin-import for automation.
```

### 3. Security Rules (security/)

**SEC.001 - Input Validation**
```markdown
# Rule: Validate All Inputs
Priority: Critical

Every external input must be validated:
- API parameters
- User input
- File uploads
- Environment variables

Use schema validation (Zod, Joi)
```

**SEC.002 - Authentication**
```markdown
# Rule: Require Auth for Protected Routes
Priority: Critical

Protected resources need authentication:
- Session tokens verified
- JWT signature validated
- Token expiration checked
- CSRF protection enabled
```

**SEC.003 - Authorization**
```markdown
# Rule: Role-Based Access Control
Priority: High

User permissions must be checked:
- Route level
- Service level
- Data level

Use middleware for consistent enforcement.
```

### 4. Performance Rules (performance/)

**PERF.001 - Caching Strategy**
```markdown
# Rule: Implement Appropriate Caching
Priority: Medium

Cache decisions:
- HTTP requests: Browser/CDN cache
- Database queries: Redis
- Computed values: In-memory
- Static assets: Long expiry

Invalidation rules documented per endpoint.
```

**PERF.002 - Bundle Size**
```markdown
# Rule: Monitor Bundle Size
Priority: Medium

Limits:
- Main bundle: <150KB
- Vendor: <100KB
- Routes: <50KB each

Tooling: webpack-bundle-analyzer
```

### 5. Testing Rules (testing/)

**TEST.001 - Coverage Requirements**
```markdown
# Rule: Minimum Test Coverage
Priority: High

Coverage targets:
- Functions: 80%
- Lines: 75%
- Branches: 70%
- Critical paths: 100%

Tool: istanbul/nyc for enforcement
```

**TEST.002 - Test Naming**
```markdown
# Rule: Descriptive Test Names
Priority: Medium

Format: describe('Component', () => {
  it('should [action] when [condition]')
})

Example:
✓ should display error when email invalid
✗ should work
```

### 6. Documentation Rules (documentation/)

**DOC.001 - README Requirements**
```markdown
# Rule: Complete README Standards
Priority: Medium

Required sections:
- Overview
- Installation
- Usage
- Configuration
- Testing
- Contributing
- License
```

**DOC.002 - Code Comments**
```markdown
# Rule: Strategic Comments
Priority: Low

Comments for:
- Complex logic (why, not what)
- Workarounds (references issue)
- Non-obvious assumptions

Tools: JSDoc for API documentation
```

### 7. Git Rules (git/)

**GIT.001 - Commit Messages**
```markdown
# Rule: Semantic Commit Format
Priority: High

Format: [type]([scope]): [subject]

Types: feat, fix, docs, style, refactor, test, chore
Scope: Feature/component name
Subject: Imperative mood, lowercase

Example:
✓ feat(auth): add oauth2 integration
✗ fixed authentication
```

**GIT.002 - Branch Naming**
```markdown
# Rule: Consistent Branch Names
Priority: Medium

Format: [type]/[ticket]/[description]

Types: feature, fix, docs, refactor
Ticket: JIRA-123 or GH-456
Description: kebab-case

Example:
✓ feature/GH-123/oauth-integration
✓ fix/GH-456/session-timeout
```

**GIT.003 - Pull Request Standards**
```markdown
# Rule: PR Quality Standards
Priority: High

Requirements:
- Descriptive title
- Detailed description
- Links to issues
- Testing instructions
- Screenshots (UI changes)
- No merge conflicts
- CI/CD passing
```

## Implementation Patterns

### Pre-commit Hook Pattern
```bash
# ~/.claude/hooks/enforce-rule.sh
#!/bin/bash

# RULE: SEC.001 - Secrets Protection
grep -qE "-----BEGIN|AKIA[0-9A-Z]{16}|token=" && {
  echo "ERROR: Potential secret detected"
  exit 1
}

# RULE: CQ.001 - File naming
for file in $(git diff --cached --name-only); do
  [[ $file =~ [A-Z].*\.ts$ ]] && [[ ! $file =~ \.types\.ts$ ]] && {
    echo "ERROR: Use kebab-case for filenames"
    exit 1
  }
done
```

### CI/CD Integration Pattern
```yaml
# .github/workflows/enforce-rules.yml
name: Enforce Rules

on: [pull_request]

jobs:
  rules:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # TEST.001 - Coverage
      - name: Check Coverage
        run: npm run test:coverage

      # CQ.001 - Linting
      - name: Lint Code
        run: npm run lint

      # GIT.001 - Commit Messages
      - name: Validate Commits
        run: npx commitlint --from ${{ github.base_ref }}
```

## Rule Versioning

### Semantic Versioning for Rules
```
Format: MAJOR.MINOR.PATCH

MAJOR: Enforcement method changed
MINOR: New requirement added
PATCH: Clarification only

Example: SEC.001 v2.1.0
```

## Automatic Rule Enforcement

### Hook-Based Enforcement
```bash
When: git commit
File: ~/.claude/hooks/managed-rules-inject.sh
Runs: Before commit created
Action: Block/warn on violations
```

### Pre-Push Enforcement
```bash
When: git push
File: ~/.claude/hooks/pre-push-rules
Runs: Before push to remote
Action: Block/warn on rule violations
```

### CI/CD Enforcement
```bash
When: Pull request created
Service: GitHub Actions / GitLab CI
Runs: Automated checks
Action: Block merge if rules fail
```

## Rule Discovery

### Finding Applicable Rules
```bash
# Search by keyword
grep -r "authentication" ~/.claude/rules/

# List by category
ls ~/.claude/rules/security/

# Show active rules
grep -r "Status: Active" ~/.claude/rules/
```

### Documentation Generation
```bash
# Generate rules report
./scripts/generate-rules-report.sh

# Output: rules-report.md
# Includes: All rules, status, enforcement
```

## Inheritance & Specialization

### Project-Specific Rules
```
project-root/
├── .claude/
│   └── rules/
│       └── [project-specific rules]
└── .git/

Loaded:
1. Global: ~/.claude/rules/
2. Project: ./.claude/rules/ (override)
```

### Team vs Individual
```
Team rules: ~/.claude/rules/ (shared)
Personal: ~/.claude/private-rules/ (local only)

Conflict resolution: Project > Team > Global
```

## Maintenance & Evolution

### Rule Deprecation Process
```markdown
1. Mark as "Deprecated" in header
2. Add migration guide
3. Support both old and new for 3 months
4. Remove from enforcement
5. Archive to rules/deprecated/
```

### Rule Review Cycle
```
Quarterly review of rules:
- Remove obsolete rules
- Update based on learnings
- Add new patterns
- Version bump
- Communicate changes
```

## Related Skills
- agent-config
- optimize-agents-md
- typescript-quality-hooks
