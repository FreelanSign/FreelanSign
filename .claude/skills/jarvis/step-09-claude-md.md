# Step 09: Update Claude MD

## Objective
Document new patterns, rules, and learnings for future AI sessions.

## What to Document

### Capture if NEW:

1. **Patterns** - Reusable solutions discovered
2. **Rules** - Constraints or conventions established
3. **Gotchas** - Non-obvious behaviors or workarounds
4. **Architecture** - Structural decisions made
5. **Dependencies** - New external integrations

### Skip if:
- Already documented elsewhere
- Obvious/standard practice
- One-time solution (not reusable)

## Documentation Locations

| Scope | File |
|-------|------|
| Project-wide | `/CLAUDE.md` |
| Directory-specific | `<dir>/CLAUDE.md` |
| Feature-specific | `<feature_dir>/CLAUDE.md` |

## Format Guidelines

**Be concise:**
- Max 5 lines per new item
- Bullet points preferred
- Code snippets only if essential
- No explanations of obvious things

**Use anchors:**
```markdown
<!-- AIDEV-NOTE: Brief explanation of non-obvious thing -->
```

## Review Checklist

Before updating, ask:
- [ ] Is this genuinely new information?
- [ ] Will this help future AI sessions?
- [ ] Is it specific enough to be actionable?
- [ ] Is it general enough to be reusable?

## Update Template

```markdown
## Updates from Feature: <name>

### New Patterns
- Pattern: `description` - See `path/file.ext`

### New Rules
- Rule: `description`

### Gotchas
- Issue: `description` - Fix: `solution`

### Architecture Notes
- Decision: `what` - Reason: `why`
```

## CLAUDE.md Update Examples

**Good:**
```markdown
### Avatar Upload
- Storage: Supabase Storage, bucket `avatars`
- Max size: 5MB, formats: jpg/png/webp
- Path pattern: `users/{user_id}/avatar.{ext}`
```

**Bad:**
```markdown
### Avatar Upload
We implemented avatar upload using Supabase Storage. The user can upload
their avatar and it gets stored in the cloud. We validate the file size
and format before uploading. The implementation follows best practices...
```

## Output

```markdown
## Claude MD Updates

### Files Modified
- `/CLAUDE.md` - Added: X
- `/apps/feature/CLAUDE.md` - Created/Updated

### Changes Made

#### /CLAUDE.md
```diff
+ ### New Section
+ - New item 1
+ - New item 2
```

#### /apps/feature/CLAUDE.md
```diff
+ # Feature CLAUDE.md
+ - Pattern: description
+ - Constraint: description
```

### No Updates Needed
- Reason: No new patterns/rules discovered

### Ready for PR: YES/NO
```

## Skip Conditions

Skip this step if:
- Only bug fixes (no new patterns)
- Trivial changes
- Already well-documented area

Output:
```markdown
## Claude MD Updates

No updates needed. Reason: <explanation>
```
