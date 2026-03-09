# Auto-Test-QA System
**Automatisches Testing + Quality Assurance für alle Build Agents**

## Übersicht

Dieses System stellt sicher dass **NIE WIEDER** ungetesteter oder fehlerhafter Code shipped wird.

**Workflow:**
```
Build Agent baut Code
     ↓
Hook triggert Auto-Test-QA
     ↓
Test Agent testet ALLES (honesty mode)
     ↓ PASS          ↓ FAIL
QA Review      Feedback → Build Agent (fix & retry)
     ↓ APPROVE      ↓ REJECT
   DONE ✅     Feedback → Build Agent (fix & retry)
```

**Maximale Iterationen:** 3 (verhindert endlose Loops)

---

## Komponenten

### 1. Build Agents
**Location:** `~/.claude/agents/build-agent-template.yaml`
**Types:** backend-developer, frontend-developer, etc
**Model:** Sonnet (speed)
**Skills:** tdd, autopilot, honesty, code-review

**Responsibilities:**
- Build code mit Tests
- Self-review vor Completion
- Niemals TODO/placeholders in "finished" code
- Erstelle BUILD_REPORT.md

**Output:**
- Working code (all tests pass)
- Tests (coverage ≥ 80%)
- Documentation
- BUILD_REPORT.md

---

### 2. Test Agent
**Location:** `~/.claude/agents/test-agent.yaml`
**Type:** test-automator
**Model:** Opus (thoroughness)
**Skills:** tdd, honesty, security-review, code-review

**Responsibilities:**
- Test ALLES was Build Agent gebaut hat
- Schreibe neue Tests für neue Features
- Test edge cases + error handling
- Security testing (SQL injection, XSS, secrets)
- Verify documentation accuracy

**Output:**
- TEST_REPORT.md mit Grade (PASS/FAIL)
- Neue test files
- Coverage report
- Issues list (if any)

**Grading:**
- ✅ PASS: Ready for QA, coverage ≥ 80%, no critical issues
- ❌ FAIL: Critical issues found, return to build agent

---

### 3. QA Review Agent
**Location:** `~/.claude/agents/qa-reviewer.yaml`
**Type:** code-reviewer
**Model:** Opus (thoroughness)
**Skills:** honesty, code-review, security-review, review

**Responsibilities:**
- Final quality gate review
- Code quality (architecture, readability, maintainability)
- Security analysis (deep dive)
- Production readiness check
- Integration impact assessment

**Output:**
- QA_REVIEW.md mit Grade (A+ to F)
- Critical/Major/Minor issues
- Final verdict (APPROVE/APPROVE_WITH_NOTES/REJECT)

**Grading:**
- ✅ APPROVE: Production-ready, deploy now
- ⚠️  APPROVE WITH NOTES: OK to deploy, create follow-up tasks
- ❌ REJECT: Critical issues, return to build agent

---

### 4. Orchestration Script
**Location:** `~/.claude/scripts/orchestrate-test-qa.py`
**Language:** Python 3
**Responsibilities:**
- Spawn Test Agent → wait → check result
- If PASS → Spawn QA Agent → wait → check result
- If FAIL/REJECT → Send feedback to Build Agent
- Manage state (max 3 iterations)
- Prevent infinite loops

**State File:** `~/.claude/logs/test-qa-state.json`
**Feedback Files:** `~/.claude/logs/feedback-{agent_id}.json`

---

### 5. Auto-Trigger Hook
**Location:** `~/.claude/hooks/auto-test-qa.sh`
**Trigger:** PostToolUse (Write, Edit, MultiEdit)
**Conditions:** Only on code files (not tests, docs, configs)

**Workflow:**
1. Check if file is code (`.py`, `.ts`, `.js`, `.go`, `.rs`, `.sh`)
2. Skip if test file itself
3. Skip if non-build script
4. Trigger orchestration script
5. Run in background
6. Log to `~/.claude/logs/auto-test-qa.log`

---

## Verwendung

### Für Build Agents

```yaml
# In deiner agent definition:
name: my-build-agent
type: backend-developer
model: sonnet

skills:
  - tdd
  - autopilot
  - honesty
  - code-review

# When you claim you're done:
# 1. Save BUILD_REPORT.md
# 2. Auto-Test-QA wird AUTOMATISCH triggered
# 3. Du bekommst Feedback wenn Tests/QA fehlschlagen
# 4. Fix issues und re-submit
```

### Für Manuelle Trigger

```bash
# Trigger orchestration manually
python3 ~/.claude/scripts/orchestrate-test-qa.py \
  --build-agent "my-agent-id" \
  --changed-files "src/file1.ts" "src/file2.ts"
```

### Monitoring

```bash
# Watch orchestration log
tail -f ~/.claude/logs/auto-test-qa.log

# Check current state
cat ~/.claude/logs/test-qa-state.json | jq

# Check feedback for agent
cat ~/.claude/logs/feedback-{agent_id}.txt
```

---

## Feedback Loop

Wenn Test Agent oder QA Agent Fehler findet:

1. **Feedback File erstellt:**
   - `~/.claude/logs/feedback-{agent_id}.json` (structured)
   - `~/.claude/logs/feedback-{agent_id}.txt` (human-readable)

2. **Build Agent Task updated:**
   - Status → "feedback_received"
   - Feedback embedded in task file

3. **Build Agent Workflow:**
   - Read feedback file
   - Read report (TEST_REPORT.md oder QA_REVIEW.md)
   - Fix ALL issues listed
   - Re-run own tests
   - Re-submit (triggers new iteration)

4. **Max 3 Iterations:**
   - Verhindert endlose Feedback-Loops
   - Nach 3 Fehlschlägen → Manual intervention nötig

---

## Reports

### BUILD_REPORT.md (Build Agent Output)
```markdown
# Build Report
**Agent:** my-build-agent
**Task:** Add user authentication
**Status:** ✅ COMPLETE

## What Was Built
- src/auth.ts: JWT authentication
- src/middleware/auth.ts: Auth middleware

## Tests
- Unit: 12/12 passing ✅
- Integration: 5/5 passing ✅
- Coverage: 87%

## Manual Testing
- [x] Login with valid credentials ✅
- [x] Login with invalid credentials ✅
- [x] JWT token expiry ✅
```

### TEST_REPORT.md (Test Agent Output)
```markdown
# Test Report
**Build Agent:** my-build-agent
**Files Changed:** 2
**Test Result:** ✅ PASS

## Tests Run
- [x] Unit tests: 12/12 passed
- [x] Integration tests: 5/5 passed
- [x] Edge cases: 8/8 passed
- [x] Security tests: 3/3 passed
- [x] Documentation verified: YES

## Issues Found
None — all tests pass.

## Verdict
✅ PASS — Ready for QA Review
```

### QA_REVIEW.md (QA Agent Output)
```markdown
# QA Review Report
**Final Grade:** A-

## Code Quality (Grade: A)
- Architecture: Clean, follows best practices
- Readability: Excellent comments, clear naming
- Maintainability: Easy to modify
- Performance: No obvious bottlenecks

## Security Analysis (Grade: A-)
- Input validation: ✅ All inputs sanitized
- JWT: ✅ Secure implementation
- Minor: Consider adding rate limiting

## Final Verdict
✅ APPROVED — Ready for production

## Recommendation
Deploy to production. Create follow-up task for rate limiting.
```

---

## Skills für Agents

### Build Agent Skills
- **tdd:** Test-driven development
- **autopilot:** Auto-completion mode
- **honesty:** Never fake success
- **code-review:** Self-review before claiming done

### Test Agent Skills
- **tdd:** Test-driven development
- **honesty:** Brutal honesty mode
- **security-review:** Security testing
- **code-review:** Code quality checks

### QA Agent Skills
- **honesty:** Brutal honesty mode
- **code-review:** Code quality patterns
- **security-review:** Security analysis
- **review:** Review planning

---

## File Structure

```
~/.claude/
├── agents/
│   ├── build-agent-template.yaml      # Template für Build Agents
│   ├── test-agent.yaml                # Test Agent Definition
│   └── qa-reviewer.yaml               # QA Reviewer Definition
├── hooks/
│   └── auto-test-qa.sh                # Auto-trigger hook
├── scripts/
│   └── orchestrate-test-qa.py         # Orchestration script
├── logs/
│   ├── auto-test-qa.log               # Orchestration log
│   ├── test-qa-state.json             # Current state
│   ├── feedback-{agent_id}.json       # Structured feedback
│   ├── feedback-{agent_id}.txt        # Human-readable feedback
│   └── task-{agent_id}.json           # Agent task files
└── skills-db/
    ├── BUILD_REPORT.md                # Build agent output
    ├── TEST_REPORT.md                 # Test agent output
    └── QA_REVIEW.md                   # QA agent output
```

---

## Hook Installation

Hook ist bereits aktiv in:
`~/.claude/hooks/auto-test-qa.sh`

Registered in hooks config (if using hooks system).

**Manual trigger:** Uncomment in CLAUDE.md

---

## Testing the System

### Test 1: Simple Build
```bash
# Create a simple Python file
echo "def add(a, b): return a + b" > test_add.py

# Manually trigger (simulates build agent completion)
python3 ~/.claude/scripts/orchestrate-test-qa.py \
  --build-agent "test-build" \
  --changed-files "test_add.py"

# Check reports
cat TEST_REPORT.md
cat QA_REVIEW.md
```

### Test 2: Build with Issues
```bash
# Create code with TODO
echo "def broken(): pass  # TODO: implement" > test_broken.py

# Trigger
python3 ~/.claude/scripts/orchestrate-test-qa.py \
  --build-agent "test-build-2" \
  --changed-files "test_broken.py"

# Should FAIL and create feedback
cat ~/.claude/logs/feedback-test-build-2.txt
```

---

## Configuration

### Max Iterations
Edit `orchestrate-test-qa.py`:
```python
"max_iterations": 3,  # Change to desired max
```

### Timeout
Edit agent yaml files:
```yaml
timeout: 1800  # 30 minutes (seconds)
```

### Test Coverage Threshold
Edit `test-agent.yaml`:
```yaml
# In briefing section:
- **FAIL if test coverage < 80%**  # Change 80 to desired %
```

---

## Troubleshooting

### Agents not spawning
**Problem:** Task files created but no agents running
**Solution:** Ensure Claude CLI is available or implement agent spawning in your environment

### Infinite loops
**Problem:** Agents keep failing and retrying
**Solution:** Check max_iterations (default: 3), review feedback files to understand why

### Hook not triggering
**Problem:** Code changes don't trigger orchestration
**Solution:**
- Check hook is executable: `chmod +x ~/.claude/hooks/auto-test-qa.sh`
- Check file extension matches code filters
- Check logs: `tail -f ~/.claude/logs/auto-test-qa.log`

### Reports not found
**Problem:** Orchestration complains about missing reports
**Solution:**
- Check agents are writing to correct location
- Check file permissions
- Check agent completion status

---

## Next Steps

1. **Test the system** mit einem einfachen Build
2. **Tune thresholds** (coverage, max iterations, timeouts)
3. **Add more build agent types** (frontend, mobile, etc)
4. **Integrate with CI/CD** (run on every PR)
5. **Add metrics** (track pass/fail rates, iteration counts)

---

## Kontakt

Bei Fragen oder Issues:
- Check logs: `~/.claude/logs/auto-test-qa.log`
- Check state: `~/.claude/logs/test-qa-state.json`
- Review feedback files for agent-specific issues
