# Jarvis - Autonomous Feature-to-PR Workflow

**Skill**: jarvis
**Description**: Execute a 10-step autonomous workflow from feature request to PR creation.
**Usage**: `/jarvis [args] <feature_description>`

## Arguments

| Arg | Description |
|-----|-------------|
| `--auto` | Execute all steps without user confirmation |
| `--review` | Run only: analyze + review (feedback mode) |
| `--fix` | Run only: fix issues + add tests + verify |
| `--create-pr` | Run only: create PR step |
| `--economy` or `-b` | Inject economy prompts to reduce token usage |
| `--skip-init` | Skip branch initialization (use current branch) |
| `--dry-run` | Plan only, no execution |

## Workflow Steps

```
[00] Init Branch      → Create feature branch following git conventions
[01] Analyze Code     → Understand codebase context and patterns
[02] Plan Feature     → Design implementation with senior mindset
[03] Execute          → Implement with TDD, check complexity
[04] Validate         → Run linters, type checks, builds
[05] Review           → Self-review following style guide
[06] Fix Issues       → Address review findings
[07] Add Tests        → Ensure coverage for new behaviors
[08] Verify Tests     → Run full test suite
[09] Claude MD        → Update documentation for AI memory
[10] Create PR        → Generate PR with structured description
```

## Mode Mapping

| Mode | Steps Executed |
|------|----------------|
| (default) | 00 → 10 (full workflow, asks confirmation at step 02) |
| `--auto` | 00 → 10 (no confirmations) |
| `--review` | 01, 05 |
| `--fix` | 06, 07, 08 |
| `--create-pr` | 10 |
| `--dry-run` | 00, 01, 02 |

## Execution Protocol

### Parse Arguments
```
args = parse_args(user_input)
feature_desc = extract_feature_description(user_input)

if args.review:
    steps = [01, 05]
elif args.fix:
    steps = [06, 07, 08]
elif args.create_pr:
    steps = [10]
elif args.dry_run:
    steps = [00, 01, 02]
else:
    steps = [00, 01, 02, 03, 04, 05, 06, 07, 08, 09, 10]

economy_mode = args.economy or args.b
auto_mode = args.auto
```

### Step Execution Loop
```
for step in steps:
    load_step_file(f"step-{step:02d}-*.md")
    if economy_mode:
        inject_economy_prompt()

    execute_step()

    # Confirmation checkpoint (step 02 only, unless --auto)
    if step == 02 and not auto_mode:
        ask_user_confirmation("Proceed with this plan?")
```

## Core Principles (Injected into all steps)

### Senior Engineering Mindset
- **WHY test**: What problem does this solve?
- **RETIREMENT test**: Understandable in 6 months?
- **DELETION test**: Can we remove code instead?

### Red Flags → STOP
- "Small change, won't break" → Add tests
- "We'll need this later" → YAGNI violation
- "Complex but elegant" → Choose simple

### Quality Gates
- No `any` in TypeScript
- No console.logs in commits
- No hardcoded secrets
- No skipped error handling

---

## Step Files Reference

Load step instructions dynamically:
- `step-00-init.md` - Branch initialization
- `step-00b-economy.md` - Token optimization overlay
- `step-01-analyze.md` - Code analysis
- `step-02-plan.md` - Feature planning
- `step-03-execute.md` - Implementation
- `step-04-validate.md` - Validation checks
- `step-05-review.md` - Code review
- `step-06-fix.md` - Issue fixes
- `step-07-tests.md` - Test creation
- `step-08-verify.md` - Test verification
- `step-09-claude-md.md` - Documentation update
- `step-10-create-pr.md` - PR creation

---

## Invocation Examples

```bash
# Full workflow with confirmation
/jarvis Add user avatar upload feature

# Full autonomous mode
/jarvis --auto Implement password reset flow

# Review only (get feedback)
/jarvis --review

# Fix current issues and add tests
/jarvis --fix

# Create PR for current work
/jarvis --create-pr

# Economy mode (reduced tokens)
/jarvis -b Add dark mode toggle

# Plan without executing
/jarvis --dry-run Refactor auth module
```
