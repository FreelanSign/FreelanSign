# Step 00: Initialize Branch

## Objective
Create feature branch following git conventions and project standards.

## Pre-checks

1. **Verify clean state**
   ```bash
   git status
   ```
   - If uncommitted changes exist → stash or commit first
   - If untracked files → ask user what to do

2. **Identify base branch**
   - Default: `dev` (from CLAUDE.md)
   - Fetch latest: `git fetch origin`

## Branch Naming Convention

Pattern: `<type>/<short-description>`

| Type | Usage |
|------|-------|
| `feat/` | New feature |
| `fix/` | Bug fix |
| `refactor/` | Code restructure |
| `docs/` | Documentation only |
| `test/` | Test additions |
| `chore/` | Maintenance tasks |

### Rules
- Lowercase only
- Hyphens for spaces
- Max 50 chars
- No special chars except `/` and `-`

## Execution

```bash
# 1. Ensure on latest dev
git checkout dev
git pull origin dev

# 2. Create feature branch
git checkout -b <type>/<feature-name>

# 3. Verify
git branch --show-current
```

## Output

Report to user:
```
Branch created: feat/user-avatar-upload
Base: dev (commit abc123)
Ready for step 01: Analyze
```

## Skip Conditions

If `--skip-init` flag:
- Use current branch
- Warn if on `main` or `dev`
- Continue to next step
