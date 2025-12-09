# CLAUDE.md

**Be extremely concise. Sacrifice grammar for concision.**

## Project

**FreelanSign**: SaaS for quotes/invoices (freelancers). Monorepo: Django backend + React/TS frontend.
**Version**: 0.2.0 | **Main branch**: `dev`

## Non-Negotiable

1. **Clean Architecture**: Never import Django models in domain layer
2. **Absolute imports**: Always `from apps.quote.domain import ...`
3. **DTOs**: Use for input/output, not Django models in use cases
4. **Conventional commits**: Required for changelog/versioning
5. **Type safety**: Strict TS, type-check before commit
6. **TDD**: Domain/application layers must have tests

## Code Style Rules

### Code Formatting

- No semicolons (enforced)
- Single quotes (enforced)
- No unnecessary curly braces (enforced)
- 2-space indentation
- Import order: external → internal → types

## Plan

End each plan with concise unresolved questions.
