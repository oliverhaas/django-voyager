# django-voyager

Reference Django project that integrates all [oliverhaas](https://github.com/oliverhaas) packages into a real, deployed application. Serves as integration test bed, gap finder, and proving ground for the full stack.

**Domain:** A fictional particle physics research platform — experiments, collision data from accelerators, periodic table, organizations, and conferences.

## Why

Building packages in isolation makes it easy to miss friction between them. A real project that uses everything together surfaces integration issues, missing features, and rough edges that unit tests and standalone demos never catch. This project has already uncovered several — see [Issues found](#issues-found).

## Stack

### Our packages

| Package | Status | Purpose |
|---------|--------|---------|
| [django-admin-boost](https://github.com/oliverhaas/django-admin-boost) | alpha | Admin performance extensions + Jinja2 admin |
| [django-cachex](https://github.com/oliverhaas/django-cachex) | stable | Valkey/Redis cache backend |
| [django-celeryx](https://github.com/oliverhaas/django-celeryx) | alpha | Celery monitoring in Django admin |
| [django-formwork](https://github.com/oliverhaas/django-formwork) | alpha | Modern forms + HTMX widgets |
| [django-nplus1](https://github.com/oliverhaas/django-nplus1) | alpha | N+1 query detection (pytest plugin) |
| [django-filthyfields](https://github.com/oliverhaas/django-filthyfields) | beta | Dirty field tracking with async support |
| [django-iconx](https://github.com/oliverhaas/django-iconx) | alpha | CSS-only icon system (Lucide icons) |
| [celery-asyncio](https://github.com/oliverhaas/celery-asyncio) | alpha | Celery rewrite for asyncio |

### Architecture

- **Fully async** — async views, async API, async services, async middleware, async ORM via [django-async-backend](https://pypi.org/project/django-async-backend/)
- **Jinja2 everywhere** — Jinja2 as the primary template backend, [JinjaX](https://jinjax.scaletti.dev/) components
- **PostgreSQL 100%** — including tests and local dev (no SQLite, ever)
- **Python 3.14t** — free-threaded CPython
- **Django 6.0**
- **Valkey** as default cache (via django-cachex)
- **Granian** as ASGI server (with built-in static file serving)
- **Docker Compose** for local infrastructure (PostgreSQL, Valkey, Mailpit)

### Third-party Django packages

django-allauth, django-anymail, django-cachalot, django-celery-beat, django-import-export, django-ninja, django-pg-zero-downtime-migrations, django-pghistory, django-pgtrigger, django-syzygy, django-tree-queries, django-vite, django-waffle

### Frontend

Tailwind CSS + daisyUI, HTMX 4, Alpine.js — built with Vite

## Quick start

```bash
# Clone and install
git clone https://github.com/oliverhaas/django-voyager.git
cd django-voyager
uv sync --group dev

# Start infrastructure
docker compose up -d

# Run migrations and seed data
uv run python manage.py migrate
uv run python manage.py seed --full

# Build frontend
npm install
npm run build

# Collect static files and start server
uv run python manage.py collectstatic --noinput
uv run granian config.asgi:application --interface asgi --host 127.0.0.1 --port 8000 \
    --static-path-route /static --static-path-mount staticfiles
```

Admin login: `admin` / `admin`

### Key URLs

- `/` — Dashboard
- `/experiments/` — Experiment list
- `/elements/` — Periodic table (118 elements)
- `/accelerators/` — Accelerators
- `/admin/` — Django admin
- `/api/docs` — Swagger API docs

### Management commands

| Command | Description |
|---------|-------------|
| `manage.py seed` | Seed periodic table (118 elements) |
| `manage.py seed --full` | Seed everything: elements, accelerators, experiments, collisions, organizations, conferences, admin user |
| `manage.py seed --flush --full` | Wipe and re-seed |
| `manage.py export_all` | Export all data to `fixtures/` as JSON |
| `manage.py import_all` | Import all data from `fixtures/` |
| `manage.py setup_periodic_tasks` | Register Celery Beat tasks for the mock workload |

## What's working

- **107 tests passing** — models, views, API, services, admin, tasks, commands
- **Full CRUD API** via Django Ninja — all models with GET/POST/PUT/PATCH/DELETE + batch collision creation
- **Async end-to-end** — views, API endpoints, services, ORM, middleware, DB connections
- **Background tasks** — image processing, webhook dispatch, cleanup via Celery
- **Mock workload** — simulated collisions (~1/sec), image uploads, experiment lifecycle, table capping
- **Admin** — all models registered, Element import/export, audit trails via pghistory
- **JinjaX components** — Sidebar with Lucide icons, NotificationCenter with Alpine.js
- **Custom makemigrations** — combines pgtrigger and syzygy migration generation

## Issues found

Integration issues discovered by this project (the whole point):

| Issue | Status | Description |
|-------|--------|-------------|
| [django-admin-boost#14](https://github.com/oliverhaas/django-admin-boost/issues/14) | Open | Unfold incompatible — placeholder stubs don't populate attributes at import time |
| [django-formwork#23](https://github.com/oliverhaas/django-formwork/issues/23) | Open | Async form support needed (`ais_valid`, `afull_clean`, `asave`) |
| [django-formwork#24](https://github.com/oliverhaas/django-formwork/issues/24) | Open | Jinja2 template support |
| [django-waffle#441](https://github.com/django-waffle/django-waffle/issues/441) | PR submitted | Async `aflag_is_active` / `aswitch_is_active` |
| Jinja2 + APP_DIRS | Fixed here | `APP_DIRS: True` on Jinja2 backend picks up DTL admin templates — set to `False` |
| Cachalot + ValkeyCache | Fixed here | ValkeyCache not in cachalot's supported backends set — added at startup |
| pgtrigger + syzygy | Fixed here | Both patch `MigrationAutodetector` — custom makemigrations chains them |
| Celery `valkey://` scheme | Known | Kombu doesn't recognize `valkey://` transport — Celery broker error on startup (non-blocking) |
| Django async transactions | Worked around | `transaction.atomic()` is sync-only — using django-async-backend's `async_atomic` |

## Remaining work

### Package maturity

Our packages need to reach stable releases:
- **django-admin-boost** — fix unfold compatibility, publish stable
- **django-formwork** — async forms, Jinja2 support
- **django-celeryx** — stabilize API
- **django-iconx** — publish to PyPI
- **django-nplus1** — stabilize API

### Upstream contributions

- **django-waffle** — async support PR ([plan](https://github.com/oliverhaas/django-waffle/blob/master/ASYNC_PLAN.md))
- **Django core** — async forms (DEP needed), async `transaction.atomic` ([#33882](https://code.djangoproject.com/ticket/33882))

### Project enhancements

- Views and forms for Organization and Conference models
- Real-time collision dashboard (HTMX polling or SSE)
- E2E tests with Playwright
- Production deployment (cloud hosting)

## Development

```bash
# Run tests
uv run pytest

# Lint
uv run ruff check && uv run ruff format --check

# Type check
uv run mypy config/ lab/
uv run ty check config/ lab/

# Template lint
uv run djlint templates/ --check

# Pre-commit (runs all of the above)
uv run pre-commit run --all-files
```

## License

MIT
