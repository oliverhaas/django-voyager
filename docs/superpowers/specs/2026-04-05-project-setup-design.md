# Project Setup Design

## Overview

Initial project scaffolding for django-voyager: a reference Django project that integrates all oliverhaas packages into a real, deployed application. The project models a fun, fictional particle physics research platform ("Voyager") as its domain — experiments, collision events from accelerators, periodic table elements — chosen to exercise webhooks, image processing, real-time updates, large data volumes, and admin-heavy features.

This spec covers **setup only**: pyproject.toml, uv, tooling, Docker Compose, and the directory skeleton. No Django apps or domain code yet.

## Project identity

- **Repo / project name**: `django-voyager`
- **Python**: 3.14t (free-threaded)
- **Django**: 6.0
- **Build system**: hatchling
- **Package manager**: uv
- **Not a distributable package** — no PyPI publishing, no `py.typed`, no `[project.scripts]`

## Directory structure

```
django-voyager/
├── config/                    # Django project config
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py            # Shared settings
│   │   ├── local.py           # Local dev overrides
│   │   ├── test.py            # Test overrides
│   │   └── production.py      # Production settings
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── templates/                 # Jinja2 templates (global)
│   └── base.html
├── static/                    # Static files (global)
├── tests/                     # All tests
│   ├── conftest.py
│   └── __init__.py
├── .github/
│   └── workflows/
│       └── ci.yml             # Lint + test
├── .pre-commit-config.yaml
├── .python-version            # 3.14t
├── .gitignore
├── pyproject.toml
├── docker-compose.yml
├── manage.py
├── LICENSE
└── PLAN.md
```

Rationale: `config/` for Django scaffolding, apps at root level. Clean separation of config vs domain. Standard Two Scoops / cookiecutter-django convention for deployed projects.

No Django apps in this phase — elements, experiments, collisions, etc. come later.

## Dependencies

### Core runtime

- `Django>=6.0,<7`
- `psycopg[c]` — PostgreSQL adapter (C-accelerated)
- `granian` — ASGI server
- `pillow` — image processing
- `httpx` — HTTP client
- `tenacity` — retry logic

### Our packages

- `django-adminx`
- `django-cachex`
- `django-celeryx`
- `django-formwork`
- `django-nplus1`
- `django-filthyfields`
- `celery-asyncio`

### Third-party Django

- `django-cachalot` — queryset caching
- `django-import-export` — admin import/export
- `django-ninja` — API layer
- `django-unfold` — admin theme
- `django-celery-beat` — periodic tasks
- `django-jinjax` — Jinja2 components
- `django-allauth` — authentication
- `django-anymail` — transactional email
- `django-waffle` — feature flags
- `django-tree-queries` — tree/hierarchy queries
- `django-pgtrigger` — PostgreSQL triggers
- `django-pghistory` — audit logging
- `django-syzygy` — migration splitting
- `django-pg-zero-downtime-migrations` — lock-safe migrations
- `django-vite` — frontend assets

### Frontend (outside Python)

Tailwind CSS, daisyUI, HTMX, Alpine.js — handled via django-vite/npm in a later phase.

### Dev dependency group

- **Linting/types**: `ruff`, `mypy`, `django-stubs`, `ty`, `djlint`
- **Testing**: `pytest`, `pytest-django`, `pytest-xdist`, `pytest-playwright`, `pytest-flakefinder`, `pytest-cov`, `pytest-asyncio`
- **Test utilities**: `factory-boy`, `testcontainers`, `beautifulsoup4`
- **Tooling**: `pre-commit`, `debugpy`

No docs dependency group — this is a deployed project, not a library.

## Tooling configuration

All configured in `pyproject.toml`.

### Ruff

- Target: Python 3.14
- Line length: 120
- Select ALL rules, ignore selectively (same philosophy as django-cachex)
- Per-file ignores for `tests/` — relaxed type annotations, magic values, etc.
- Per-file ignores for `config/settings/` — wildcard imports, unused imports (settings splitting pattern)

### MyPy

- Python 3.12 target (mypy doesn't support 3.14 yet)
- Plugin: `mypy_django_plugin.main`
- Django settings: `config.settings.base`
- Strict: warn on redundant casts, unused ignores

### ty

- Python 3.14
- Selective rule overrides as needed

### Pytest

- Django settings: `config.settings.test`
- Test paths: `tests/`
- Coverage on all app directories
- `--cov-report=term-missing --no-cov-on-fail`

### djlint

- Profile: `jinja` (Jinja2 everywhere)
- Indent: 2
- Max line length: 120

## Pre-commit configuration

Two stages, mirroring django-cachex:

### Pre-commit stage

- `pre-commit-hooks` (v5.0.0) — AST check, case conflicts, JSON/YAML/TOML validation, merge conflicts, private key detection, line ending fixes
- `taplo` — TOML formatting (2-space indent, key reordering)
- `add-trailing-comma` — trailing comma enforcement
- `uv-sync-check` (local) — ensure lock is synced
- `ruff-check` (local) — lint with auto-fix
- `ruff-format` (local) — formatting
- `djlint` (local) — template linting

### Pre-push stage

- `mypy` (local) — type check app code
- `ty` (local) — type check app code

## Docker Compose (local dev)

Three services:

- **postgres** — PostgreSQL 17, port 5432, persistent volume, healthcheck
- **valkey** — Valkey 8, port 6379, persistent volume, healthcheck
- **mailpit** — local email testing (SMTP 1025, web UI 8025)

No Django/granian container — app runs directly via `uv run granian` for faster dev iteration.

## CI (GitHub Actions)

Single `ci.yml` workflow:

- **Lint job**: Python 3.14 — ruff check/format, mypy, ty, djlint
- **Test job**: Python 3.14 + Django 6.0 — pytest with PostgreSQL + Valkey services

No publish, docs, or tagging workflows — this is a deployed project, not a package.
