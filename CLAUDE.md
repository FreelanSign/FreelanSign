# CLAUDE.md

**Be extremely concise. Sacrifice grammar for concision.**

## Project

**FreelanSign**: SaaS for quotes/invoices (freelancers). Monorepo: Django backend + React/TS frontend.
**Version**: v0.3.0-SNAPSHOT | **Main branch**: `dev`

## Non-Negotiable

- Read the file `docs/good-practices/senior_mindset.md` before anything.

1. **Clean Architecture**: Never import Django models in domain layer
2. **Keep it simple**: Don't add abstractions I didn't ask for. One file if possible.
3. **Absolute imports**: Always `from apps.quote.domain import ...`
4. **DTOs**: Use for input/output, not Django models in use cases
5. **Conventional commits**: Required for changelog/versioning
6. **Type safety**: Strict TS, type-check before commit
7. **TDD**: Domain/application layers must have tests

## Code Style Rules

### Code Formatting

- No semicolons (enforced)
- Single quotes (enforced)
- No unnecessary curly braces (enforced)
- 2-space indentation
- Import order: external → internal → types

## Plan

End each plan with concise unresolved questions.
