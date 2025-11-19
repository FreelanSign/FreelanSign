# Git Workflow

## Branch Strategy

- **main**: Production-ready code
- **dev**: Integration branch (default PR target)
- **feature/\<ticket-id\>-\<description\>**: New features
- **bugfix/\<ticket-id\>-\<description\>**: Bug fixes
- **hotfix/\<ticket-id\>-\<description\>**: Urgent fixes
- **release/v\<version\>**: Release preparation

## Commit Messages

**Conventional Commits** format:
```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `perf`, `chore`

**Examples**:
```
feat(quote): add PDF download endpoint
fix(auth): resolve token refresh issue
refactor(catalog): simplify prestation calculator
test(client): add unit tests for client policy
```

**Breaking changes**: Use `!` after type (e.g., `feat!:`) or add `BREAKING CHANGE:` in footer.

## Release Process

1. Create release branch from `dev`: `git checkout -b release/vX.Y.Z`
2. Generate changelog: `pnpm run release --release-as X.Y.Z`
3. Push and create PR to `main`
4. After merge, tag: `git tag freelansign/vX.Y.Z && git push --tags`
5. Create GitHub release with content from `/docs/RELEASE_PLAN_vX.Y.Z.md`
6. Back-merge to `dev`: `git checkout dev && git merge main`

## Code Quality

### Pre-commit Hooks

Install: `pre-commit install`

Hooks (`.pre-commit-config.yaml`):
- **Python**: black, isort, flake8
- **JavaScript/TypeScript**: eslint, prettier
- **Generic**: trailing whitespace, YAML/JSON checks, large file checks

### Formatting Rules

**Backend (Python)**:
- Line length: 127 characters
- Formatter: black
- Import sorting: isort with black profile
- Skip: migrations, `__pycache__`

**Frontend (TypeScript)**:
- Formatter: prettier
- Linter: eslint with TypeScript and React plugins
