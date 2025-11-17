# CLAUDE.md

**Be extremely concise. Sacrifice grammar for concision.**

## Project

**FreelanSign**: SaaS for quotes/invoices (freelancers). Monorepo: Django backend + React/TS frontend.
**Version**: 0.1.1 | **Main branch**: `dev`

## Architecture

### Clean Architecture + DDD (Backend)

```
apps/<domain>/
├── domain/       # Pure business logic (no framework deps)
├── application/  # Use cases, DTOs, ports
├── adapters/     # Infrastructure (ORM, email, PDF)
└── interface/    # API (views, serializers)
```

**Backend bounded contexts**: user, client, quote, branding, catalog, core, email

**Frontend structure**: domain/ (types), infrastructure/ (repos, API), interface/ (UI, pages, hooks), app/ (router)


## Non-Negotiable

1. **Clean Architecture**: Never import Django models in domain layer
2. **Absolute imports**: Always `from apps.quote.domain import ...`
3. **DTOs**: Use for input/output, not Django models in use cases
4. **Conventional commits**: Required for changelog/versioning
5. **Type safety**: Strict TS, type-check before commit
6. **TDD**: Domain/application layers must have tests

## Plan

End each plan with concise unresolved questions.
- Do not mention Claude Code in any Commit message, PR description or Github issues