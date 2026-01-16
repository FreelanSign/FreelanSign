---
description: Autonomous 10-step workflow from feature to PR (init → analyze → plan → execute → validate → review → fix → test → verify → PR)
argument-hint: "[--auto|--review|--fix|--create-pr|-b] <feature description>"
---

# Jarvis - Feature-to-PR Workflow

You are executing the Jarvis autonomous workflow. Parse the arguments and execute accordingly.

## Argument Parsing

```
Input: $ARGUMENTS

Parse:
- --auto      → auto_mode = true (skip confirmations)
- --review    → review_mode = true (steps: 01, 05 only)
- --fix       → fix_mode = true (steps: 06, 07, 08 only)
- --create-pr → pr_mode = true (step: 10 only)
- -b/--economy → economy_mode = true (reduce token usage)
- --skip-init → skip_init = true (use current branch)
- --dry-run   → dry_run = true (steps: 00, 01, 02 only)
- Everything else → feature_description
```

## Mode Selection

Execute steps based on mode:

| Mode | Steps |
|------|-------|
| default | 00 → 10 (confirm at step 02) |
| --auto | 00 → 10 (no confirmations) |
| --review | 01, 05 |
| --fix | 06, 07, 08 |
| --create-pr | 10 |
| --dry-run | 00, 01, 02 |

## Step Execution

For each step, load and execute instructions from:
`.claude/skills/jarvis/step-XX-*.md`

If economy_mode: Also inject `.claude/skills/jarvis/step-00b-economy.md`

### Step 00: Init Branch
Read: `.claude/skills/jarvis/step-00-init.md`
- Create feature branch from dev
- Branch naming: `<type>/<feature-name>`
- Skip if --skip-init

### Step 01: Analyze Code
Read: `.claude/skills/jarvis/step-01-analyze.md`
- Identify relevant files and patterns
- Check CLAUDE.md files for context
- List reusable components

### Step 02: Plan Feature
Read: `.claude/skills/jarvis/step-02-plan.md`
- Design implementation following Senior Mindset
- Create concise task list
- List unresolved questions
- **STOP and ask for confirmation unless --auto**

### Step 03: Execute
Read: `.claude/skills/jarvis/step-03-execute.md`
- TDD: Write tests first
- Implement tasks in order
- Check cyclomatic complexity (warn if >5)
- For UI tasks: invoke /frontend-design

### Step 04: Validate
Read: `.claude/skills/jarvis/step-04-validate.md`
- Run linting (black, pnpm lint)
- Type checking (pnpm check)
- Build verification
- Quick test run

### Step 05: Review
Read: `.claude/skills/jarvis/step-05-review.md`
- Self-review against style guide
- Security checklist
- Architecture compliance
- Categorize issues: Critical/Important/Suggestion

### Step 06: Fix Issues
Read: `.claude/skills/jarvis/step-06-fix.md`
- Fix all Critical issues
- Fix Important issues
- Address quick Suggestions
- Re-validate after fixes

### Step 07: Add Tests
Read: `.claude/skills/jarvis/step-07-tests.md`
- Ensure coverage for new behaviors
- Test happy path, errors, edge cases
- Follow test naming conventions

### Step 08: Verify Tests
Read: `.claude/skills/jarvis/step-08-verify.md`
- Run full test suite
- Analyze any failures
- Check coverage report

### Step 09: Claude MD
Read: `.claude/skills/jarvis/step-09-claude-md.md`
- Document new patterns/rules
- Update relevant CLAUDE.md files
- Keep updates concise (<5 lines each)

### Step 10: Create PR
Read: `.claude/skills/jarvis/step-10-create-pr.md`
- Commit with conventional format
- Push branch
- Create PR with structured description

## Senior Engineering Mindset (Apply Throughout)

**Before coding:**
1. WHY? - What problem does this solve?
2. RETIREMENT? - Understandable in 6 months?
3. DELETION? - Can we remove code instead?

**Red flags → STOP:**
- "Small change, won't break" → Add tests
- "We'll need this later" → YAGNI violation
- "Complex but elegant" → Choose simple

## Quality Gates

- No `any` in TypeScript
- No console.logs in commits
- No hardcoded secrets
- Error handling at boundaries
- Tests for new behaviors

## Output Format

After each step, report:
```
✅ Step XX: <name> - Complete
   Summary: <1-line summary>
   Next: Step YY
```

On workflow completion:
```
🎯 Jarvis Complete!
   Branch: feat/feature-name
   PR: https://github.com/.../pull/XXX
   Changes: X files, +Y/-Z lines
```
