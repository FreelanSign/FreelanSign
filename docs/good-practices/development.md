# Development Guide

## Backend (Django)

**Local dev** (from `/backend`):
```bash
python manage.py runserver         # Run server
pytest                              # Run tests with coverage
pytest apps/quote/tests/...        # Run specific test
python manage.py makemigrations    # Create migrations
python manage.py migrate           # Apply migrations
python manage.py shell             # Django shell
black . && isort .                 # Format
flake8 .                           # Lint
```

**Environment**: Uses `django-environ` to load `.env` from repo root.

## Frontend (React + Vite)

**Local dev** (from `/frontend`):
```bash
pnpm install        # Install dependencies
pnpm dev            # Dev server (http://localhost:3000)
pnpm test           # Run tests
pnpm test:coverage  # Tests with coverage
pnpm build          # Production build
pnpm lint           # Lint
pnpm format         # Format
pnpm type-check     # Type check
```

## Docker

```bash
make dev-docker        # Build and start all services
make logs              # View logs
make logs-backend      # Backend logs only
make logs-frontend     # Frontend logs only
make migrate           # Run migrations in Docker
make shell             # Django shell in Docker
make down              # Stop services
make clean             # Clean containers and volumes
```

**Services:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432

## Development

## Paradigms

- **Clean Architecture** : All business logic is isolated from external concerns (frameworks, databases, APIs). The application is structured into Domain / Application / Adapters / Interface layers. This ensures: Independence from frameworks, High testability, Easy replacement of infrastructure components (database, UI, etc.)
- **Clean Code**: Every module must be : Readable — names clearly reflect intent,Maintainable — single responsibility per file/class, Consistent — strict linting and formatting rules enforced, Self-documented — code should explain itself, comments only where logic isn’t obvious. The principle: “Code should read like well-written prose.”
- **TDD** : Each feature follows the Red → Green → Refactor cycle: 1- Write a failing test (specifying expected behavior), 2- Implement minimal code to make it pass, 3- Refactor for clarity and maintainability. This keeps logic testable, modular, and avoids regression. Unit tests (pytest, Jest) are mandatory on domain and application layers.
- **DDD** : Business logic drives the codebase structure.The Domain layer expresses the core rules and concepts of the business (quotes, clients, documents, templates). Ubiquitous language is shared between developers, domain experts, and documentation to avoid ambiguity. Bounded contexts are separated (e.g., User, Quote, Document, Branding) to maintain clear ownership and reduce coupling.
- **BDD** : Features are described from the user’s point of view using concrete examples (“Given / When / Then”). Gherkin scenarios define the expected behavior and business rules before any code is written. These scenarios drive TDD at the domain and application layers and serve as living documentation that non-technical stakeholders can understand and validate.


### Backend
- **Framework**: pytest with pytest-django, pytest-cov, pytest-mock
- **Coverage target**: Domain and application layers must be tested
- **Test structure**: Mirror app structure in `tests/`
- **TDD approach**: Red → Green → Refactor
- **BDD approach**: We need to write tests before writing the code when we are not sure about the implementation.
- **Config**: `backend/pytest.ini`

### Frontend
- **Framework**: Vitest with React Testing Library
- **Run**: `pnpm test` (from `/frontend`)

## Environment Variables

**Backend** (`.env` at repo root):
```
SECRET_KEY=...
DEBUG=True/False
DATABASE_*=...
```

**Frontend** (`.env.development.local`, `.env.prod`):
```
VITE_API_URL=http://localhost:8000
```

## Release Management

From repo root:
```bash
pnpm run release --release-as X.Y.Z
pnpm run release:patch
pnpm run release:minor
pnpm run release:major
```
