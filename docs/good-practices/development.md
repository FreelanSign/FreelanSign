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

## Testing

### Backend
- **Framework**: pytest with pytest-django, pytest-cov, pytest-mock
- **Coverage target**: Domain and application layers must be tested
- **Test structure**: Mirror app structure in `tests/`
- **TDD approach**: Red → Green → Refactor
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
