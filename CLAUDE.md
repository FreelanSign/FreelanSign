# CLAUDE.md - FreelanSign

**CRITICAL: Be extremely concise. Sacrifice grammar for concision. No yapping.**

## 🎯 Context (WHY/WHAT)

- **FreelanSign**: SaaS for freelancer quotes/invoices.
- **Architecture**: Monorepo. Django (Backend) + React/TS (Frontend).
- **Stack**: Django, React, TS, venv, pytest, pnpm.
- **Version**: v0.3.0-SNAPSHOT | **Branch**: `dev`

## 🛠 Workflow (HOW)

### Commands

- **Backend**: `source venv/bin/activate`, `pytest`, `python manage.py runserver`
- **Frontend**: `pnpm dev`, `pnpm test`, `pnpm build`, `pnpm check` (types)
- **Linting**: `pnpm lint` (Front), `black .` (Back)

### Non-Negotiable Rules

1. **Clean Arch**: Domain layer = Pure Python. NEVER import Django models here.
2. **Data Flow**: Use DTOs for Use Cases. No Django models in/out.
3. **Imports**: Absolute only (`from apps.quote.domain import ...`).
4. **Logic**: Keep it simple. One file if possible. No unasked abstractions.
5. **Commits**: Strictly Conventional Commits.

## 📝 Code Style

- **Python**: PEP8, Black formatting.
- **JS/TS**: No semicolons, single quotes, no unnecessary braces, 2-space indent.
- **Imports**: External → Internal → Types.
- **TDD**: Domain/Application layers must have 100% test coverage.

## 📄 PDF Templates

- **Conditional logic**: Add flags in `pdf_context_presenter.py:preview_context()` (e.g., `has_uniform_tax`)
- **Template width**: Always sum to 100% (use conditional widths if needed)
- **Signature box**: 120px height for stamps/digital signatures
