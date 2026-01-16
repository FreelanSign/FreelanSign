# Step 01: Analyze Code

## Objective
Understand codebase context, patterns, and constraints before planning.

## Analysis Checklist

### 1. Project Structure
- [ ] Identify relevant directories
- [ ] Check for existing similar features
- [ ] Note architectural patterns (Clean Arch, etc.)

### 2. Existing Patterns
```
Search for:
- Similar components/modules
- Related domain entities
- Existing utilities that can be reused
- Test patterns in use
```

### 3. Dependencies
- [ ] External packages involved
- [ ] Internal module dependencies
- [ ] Database/API contracts

### 4. Constraints
- [ ] Check CLAUDE.md for project rules
- [ ] Identify non-negotiables
- [ ] Note tech debt or known issues

## Tools to Use

```bash
# Find related files
Glob: **/*<keyword>*

# Search for patterns
Grep: <pattern> in relevant dirs

# Read CLAUDE.md files
Read: CLAUDE.md, <dir>/CLAUDE.md

# Check existing tests
Glob: **/*test*<keyword>*
```

## Output Format

```markdown
## Analysis Summary

### Relevant Files
- `path/to/file.ts` - description
- `path/to/other.py` - description

### Existing Patterns
- Pattern 1: used in X, Y
- Pattern 2: applies to Z

### Reusable Components
- `ComponentName` - can be extended for this feature
- `utility_function` - handles related logic

### Constraints Identified
- Must use existing auth middleware
- Domain layer must stay pure (no Django imports)

### Risks/Concerns
- None / List specific concerns

### Ready for Planning: YES/NO
```

## Senior Mindset Check

Before proceeding, answer:
1. **Why?** - Is the feature value clear?
2. **Deletion?** - Can existing code solve this?
3. **Scope?** - Are boundaries defined?

If any unclear → Ask user for clarification before Step 02.
