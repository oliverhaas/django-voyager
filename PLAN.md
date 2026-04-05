---
status: idea
effort: medium
impact: high
---

# django-voyager

Reference Django project that integrates all oliverhaas packages into a real, deployed application. Serves as integration test bed, gap finder, and proving ground for the full stack.

## Problem

Building packages in isolation makes it easy to miss friction between them. A real project that uses everything together surfaces integration issues, missing features, and rough edges that unit tests and standalone demos never catch.

## Goals

1. **Integration testing** — do all the packages play nicely together?
2. **Gap finding** — what's still missing or awkward in the stack?
3. **Real deployment** — deployed somewhere to test under real conditions (caching behavior, query performance, admin UX, etc.)
4. **Future template potential** — could eventually become a project template if the stack matures

## Stack

### Our packages

- [django-admin-boost](https://github.com/oliverhaas/django-admin-boost) — admin performance extensions + Jinja2 admin
- [django-cachex](https://github.com/oliverhaas/django-cachex) — Valkey/Redis cache backend
- [django-celeryx](https://github.com/oliverhaas/django-celeryx) — Celery monitoring in Django admin (replaces Flower)
- [django-formwork](https://github.com/oliverhaas/django-formwork) — modern forms + HTMX
- [django-nplus1](https://github.com/oliverhaas/django-nplus1) — N+1 query detection
- [django-filthyfields](https://github.com/oliverhaas/django-filthyfields) — dirty field tracking
- [celery-asyncio](https://github.com/oliverhaas/celery-asyncio) — Celery rewrite for asyncio

### Architecture & approach

- **Fully async** — async views, async middlewares (custom where needed), async ORM
- **Jinja2 everywhere** — Jinja2 as the primary template backend, push as far as possible (admin included via django-admin-boost)
- **PostgreSQL 100%** — including tests and local dev (no sqlite, ever)
- **Valkey** as default cache (via django-cachex)
- **Granian** as ASGI server
- **Static files** — granian directly if possible, whitenoise as fallback
- **Docker Compose** for local dev (maybe something better later)

### Third-party: Django ecosystem

- django-cachalot — queryset caching
- django-import-export — data import/export in admin
- django-ninja — API layer
- django-unfold — admin theme (needs investigation: Jinja2 compatibility with django-admin-boost)
- django-celery-beat — periodic task scheduling
- django-jinjax — Jinja2 components (probably)
- django-allauth — authentication
- django-anymail — transactional email
- django-waffle — feature flags
- django-tree-queries — tree/hierarchy queries
- django-pgtrigger — PostgreSQL triggers
- django-pghistory — audit logging via triggers
- django-syzygy — pre/post-deploy migration splitting
- django-pg-zero-downtime-migrations — lock-safe schema changes (needs compatibility patch with syzygy)
- django-vite — frontend asset integration

### Third-party: Frontend

- Tailwind CSS
- daisyUI — Tailwind component library
- HTMX + Alpine.js

### Third-party: Testing & QA

- pytest
- pytest-django
- pytest-xdist — parallel tests
- pytest-playwright — E2E browser tests
- pytest-flakefinder — flaky test detection
- pytest-cov — coverage
- factory-boy — test data factories
- testcontainers — containers for tests (postgres, valkey)
- beautifulsoup4 — HTML assertions

### Third-party: Tooling

- ruff — linting + formatting
- ty — type checking (goal: replace mypy fully)
- mypy + django-stubs — type checking (for now, until ty catches up)
- djlint — template linting
- pre-commit
- httpx — HTTP client (NO requests library)
- pillow — image processing
- tenacity — retry logic
- debugpy — remote debugging
- psycopg[c] — PostgreSQL adapter (C-accelerated)

## Open questions

- **django-unfold + Jinja2** — does unfold work with Jinja2 templates? May need django-admin-boost to handle the conversion, or unfold may need to be dropped/replaced
- **django-jinjax vs django-components-lite** — both do components, jinjax is Jinja2-native. Pick one.
- **Static files** — can granian serve static files directly in production, or do we need whitenoise?
- **syzygy + pg-zero-downtime-migrations** — need to verify compatibility and write patches if needed
- **What app to build?** — needs to be non-trivial enough to exercise everything but not so complex that it becomes its own project

## Notes

Not a package — a deployed project. May evolve into a cookiecutter/copier template later if the stack proves itself.
