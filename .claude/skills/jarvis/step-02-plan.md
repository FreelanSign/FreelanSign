# Step 02: Plan Feature

## Objective
Design implementation with senior engineering mindset. Concise. Actionable.

## Planning Protocol

### 1. Pre-Planning Questions (Answer internally)
- [ ] What's the simplest solution that works?
- [ ] Can this be done by modifying existing code?
- [ ] What's the minimum scope to deliver value?

### 2. Decision Framework
```
Feature request
├─> Existing code handles it? → Extend/modify
├─> New code needed?
│   ├─> < 3 files? → Direct implementation
│   └─> ≥ 3 files? → Consider if abstraction truly needed
└─> Complex?
    ├─> Break into smaller steps
    └─> Flag for TDD approach
```

## Plan Template

```markdown
## Feature: <name>

### Goal
<1 sentence: what problem this solves>

### Approach
<1-2 sentences: high-level strategy>

### Tasks
1. [ ] Task description → `file/path.ext`
2. [ ] Task description → `file/path.ext`
3. [ ] ...

### Files to Modify
- `path/file.ext` - change description
- `path/new.ext` - NEW: purpose

### Files to Create
- `path/new.ext` - purpose (only if truly needed)

### Tests Required
- [ ] Test case 1
- [ ] Test case 2

### Dependencies
- None / List external needs

### Risks
- None / List concerns

### Unresolved Questions
- None / List blocking questions

### Claude MD Updates
- None / List new patterns/rules to document
```

## Quality Gates

Plan MUST:
- [ ] Have < 15 tasks (break down if more)
- [ ] No "future-proofing" tasks
- [ ] No unnecessary abstractions
- [ ] Each task is independently testable
- [ ] Clear file → task mapping

## User Confirmation

**Unless `--auto` flag is set:**

```
Plan complete. Review above.

Proceed with implementation? [Y/n]
- Y: Continue to Step 03
- n: Revise plan based on feedback
```

Wait for explicit user confirmation before Step 03.

## Red Flags (Revise plan if present)

- [ ] "In case we need later" → Remove
- [ ] Generic utility creation → Make specific
- [ ] > 5 new files → Simplify
- [ ] No tests listed → Add tests
- [ ] Unclear task descriptions → Be specific
