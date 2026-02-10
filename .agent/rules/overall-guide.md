---
trigger: always_on
---

**Be extremely concise. Sacrifice grammar for concision.**

## Project

**FreelanSign**: SaaS for quotes/invoices (freelancers). Monorepo: Django backend + React/TS frontend.
**Version**: 0.2.0 | **Main branch**: `dev`

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

## Implementation Strategy (CRITICAL)

1.  **Interface Layer (DRF)**:
    * **Be Idiomatic**: Use standard DRF features (Permissions, Generic Views, Mixins) inside `interface/`. Don't reinvent logic (e.g., merging partial updates) if DRF handles it.
    * **Serialization**: Serializers are the bridge. Pass UseCase results (DTOs or Entities) directly to Serializers. Do NOT manually map dicts in Views.
    * **Permissions**: Use `permission_classes` for access control. Do not duplicate permission logic inside the view method body.

2.  **Application Layer**:
    * Orchestrates flow. Accepts InputDTO, returns OutputDTO or Entity.
    * Must handle business errors that the Interface layer catches and converts to HTTP responses.

3.  **Domain Layer**:
    * Pure Python. No Django imports.

## Non-Negotiable Rules

1. **TDD & BDD**: Always suggest to the user a `BDD` then a `TDD` approach when it fit to the context.
2. **Dependencies**: `Domain` imports nothing. `Application` imports `Domain`. `Interface` & `Adapters` import `Application` & `Domain`.
3.  **No Leaks**: Never import Django models in `domain` or `application` layers.
4.  **DTO Pattern**: Use DTOs to cross boundaries, BUT use DRF Serializers to map these DTOs to JSON in the Interface layer.
5.  **DRY & KISS**: Do not over-engineer. If a DRF feature (like `partial=True`) exists, use it instead of custom code in the View.
6.  **Type Safety**: Strict TS / Python Type Hints.
7.  **Testing**: Unit tests for Domain/UseCases are mandatory.

## Plan

End each plan with concise unresolved questions.
