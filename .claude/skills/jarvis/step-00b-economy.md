# Step 00b: Economy Mode Overlay

## Purpose
Reduce token consumption during Jarvis execution. Inject these directives when `-b` or `--economy` flag is set.

## Global Economy Rules

### Communication
- Max 3 sentences per response
- No explanations unless asked
- Use bullet points only
- Skip "I will now..." preambles

### Tool Usage
- Batch file reads (max 3 per call)
- Use `head_limit` on grep/glob
- Prefer targeted searches over broad scans
- Skip redundant confirmations

### Code Output
- Show only changed lines + 2 context
- No full file reprints
- Diff format preferred

### Analysis
- Skip obvious observations
- Report only: issues, decisions, blockers
- No praise or validation

## Step-Specific Overrides

### Step 01 (Analyze)
- Max 5 files to read
- Skip test files unless directly relevant
- Use grep over full reads

### Step 02 (Plan)
- Max 10 bullet points
- No rationale unless critical
- Questions list only if blocking

### Step 03 (Execute)
- Write code directly, no drafts
- Single edit per file when possible
- Batch related changes

### Step 05 (Review)
- Checklist format only
- Issues list: max 10 items
- Severity tags required

### Step 09 (Claude MD)
- Only update if genuinely new info
- Max 5 lines added per file
- Skip if no significant learnings

## Token Budget Targets

| Step | Normal | Economy |
|------|--------|---------|
| Analyze | ~2000 | ~500 |
| Plan | ~1500 | ~400 |
| Execute | ~3000 | ~2000 |
| Review | ~1000 | ~300 |
| Total | ~15000 | ~5000 |

## Enforcement

Before each step output, check:
- [ ] Response under 500 tokens?
- [ ] No redundant information?
- [ ] Action-focused, not explanation-focused?
