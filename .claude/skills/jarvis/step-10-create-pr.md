# Step 10: Create PR

## Objective
Create a well-structured pull request for review.

## Pre-PR Checklist

- [ ] All tests pass
- [ ] No linting errors
- [ ] Build succeeds
- [ ] Branch is up to date with base

```bash
# Ensure latest base
git fetch origin dev
git rebase origin/dev

# Verify clean state
git status
```

## Commit Strategy

### If multiple logical changes:
```bash
# Stage and commit separately
git add <related_files>
git commit -m "<type>: <description>"
```

### Commit Message Format (Conventional Commits)

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:** feat, fix, refactor, test, docs, chore, style

**Examples:**
```
feat(quote): Add PDF export functionality
fix(auth): Handle expired token refresh
refactor(user): Extract validation logic to domain
```

## Push Branch

```bash
git push -u origin <branch-name>
```

## PR Creation

```bash
gh pr create \
  --base dev \
  --title "<type>(<scope>): <short description>" \
  --body "$(cat <<'EOF'
## Summary
<1-3 bullet points describing what this PR does>

## Changes
- `path/file.ext` - Change description
- `path/file.ext` - Change description

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if UI changes)
<Add screenshots or remove section>

## Checklist
- [ ] Code follows project style
- [ ] Tests cover new behavior
- [ ] No console.logs committed
- [ ] CLAUDE.md updated (if applicable)

## Related
- Closes #<issue_number> (if applicable)
- Related to #<PR_number> (if applicable)
EOF
)"
```

## PR Title Format

```
<type>(<scope>): <imperative description>

Examples:
- feat(quote): Add line item reordering
- fix(invoice): Correct tax calculation rounding
- refactor(auth): Simplify token refresh logic
```

## PR Description Sections

| Section | Required | Content |
|---------|----------|---------|
| Summary | Yes | 1-3 bullets, what & why |
| Changes | Yes | File-level breakdown |
| Testing | Yes | Test coverage details |
| Screenshots | If UI | Before/after images |
| Checklist | Yes | Quality gates |
| Related | If exists | Issues/PRs links |

## Output

```markdown
## PR Created

**Title:** feat(feature): Description

**URL:** https://github.com/owner/repo/pull/XXX

**Base:** dev ← **Head:** feat/feature-name

### Summary
- Point 1
- Point 2

### Files Changed
- X files changed
- +Y insertions, -Z deletions

### Review Requested
- @reviewer1
- @reviewer2

### Next Steps
1. Wait for CI checks
2. Address review comments
3. Merge when approved

---
✅ Jarvis workflow complete!
```

## Post-PR Actions

1. **Monitor CI** - Watch for failures
2. **Respond to reviews** - Address feedback promptly
3. **Keep branch updated** - Rebase if conflicts arise

## Error Handling

### If push fails:
```bash
# Force push only if rebased
git push --force-with-lease
```

### If PR creation fails:
- Check gh auth: `gh auth status`
- Verify remote: `git remote -v`
- Manual fallback: Create via GitHub UI
