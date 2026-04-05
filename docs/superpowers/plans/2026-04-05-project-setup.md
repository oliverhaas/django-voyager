# Project Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the django-voyager project with all dependencies, tooling, Docker Compose, pre-commit, and CI — ready for app development.

**Architecture:** `config/` directory for Django project settings/routing, apps at root level, `tests/` for all tests. Jinja2 as primary template backend, PostgreSQL via psycopg, Valkey cache via django-cachex, granian as ASGI server.

**Tech Stack:** Python 3.14t (free-threaded), Django 6.0, uv, hatchling, ruff, mypy, ty, pytest, pre-commit, Docker Compose (PostgreSQL 17, Valkey 8, Mailpit).

---

## File Map

**Create:**
- `.python-version` — uv Python version pin (3.14t free-threaded)
- `pyproject.toml` — all dependencies + tool config (ruff, mypy, ty, pytest, djlint, coverage)
- `.gitignore` — Python/Django/tooling ignores
- `manage.py` — Django management script
- `config/__init__.py` — package marker
- `config/asgi.py` — ASGI entrypoint
- `config/wsgi.py` — WSGI entrypoint (fallback)
- `config/urls.py` — root URL configuration
- `config/jinja2.py` — Jinja2 template environment
- `config/settings/__init__.py` — package marker
- `config/settings/base.py` — shared settings (all package wiring)
- `config/settings/local.py` — local dev overrides
- `config/settings/test.py` — test overrides
- `config/settings/production.py` — production overrides
- `templates/base.html` — minimal Jinja2 base template
- `static/.gitkeep` — static files directory placeholder
- `tests/__init__.py` — package marker
- `tests/conftest.py` — shared pytest fixtures
- `docker-compose.yml` — PostgreSQL + Valkey + Mailpit
- `.pre-commit-config.yaml` — pre-commit + pre-push hooks
- `.github/workflows/ci.yml` — lint + test pipeline

**Modify:**
- None (greenfield project)

---

### Task 1: Project Foundation

**Files:**
- Create: `.python-version`
- Create: `pyproject.toml`
- Create: `.gitignore`

- [ ] **Step 1: Create `.python-version`**

```
3.14t
```

- [ ] **Step 2: Create `pyproject.toml`**

```toml
[project]
name = "django-voyager"
version = "0.1.0"
description = "Reference Django project integrating the full oliverhaas package stack"
license = { text = "MIT" }
requires-python = ">=3.14"
authors = [{ name = "Oliver Haas", email = "ohaas@e1plus.de" }]
dependencies = [
  # Core
  "Django>=6.0,<7",
  "granian>=2",
  "httpx>=0.28",
  "pillow>=11",
  "psycopg[c]>=3.2",
  "tenacity>=9",
  # Our packages
  "django-adminx",
  "django-cachex[valkey]",
  "django-celeryx",
  "django-formwork",
  "django-nplus1",
  # "django-filthyfields",  # not yet published
  # "celery-asyncio",       # not yet published
  # Third-party Django
  "django-allauth",
  "django-anymail",
  "django-cachalot",
  "django-celery-beat",
  "django-import-export",
  "django-ninja",
  "django-pg-zero-downtime-migrations",
  "django-pghistory",
  "django-pgtrigger",
  "django-syzygy",
  "django-tree-queries",
  "django-unfold",
  "django-vite",
  "django-waffle",
  "jinjax",
]

[dependency-groups]
dev = [
  "beautifulsoup4==4.14.3",
  "debugpy==1.8.14",
  "django-stubs==6.0.1",
  "djlint==1.36.4",
  "factory-boy==3.3.3",
  "mypy==1.19.1",
  "pre-commit==4.5.1",
  "pytest==9.0.2",
  "pytest-asyncio==1.3.0",
  "pytest-cov==7.1.0",
  "pytest-django==4.12.0",
  "pytest-flakefinder==1.1.0",
  "pytest-playwright==0.7.0",
  "pytest-xdist==3.8.0",
  "ruff==0.15.7",
  "testcontainers==4.14.2",
  "ty==0.0.24",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["config"]

# --- Ruff ---

[tool.ruff]
target-version = "py314"
line-length = 120
fix = true

[tool.ruff.lint]
select = ["ALL"]
ignore = [
  "COM812", # Conflicts with ruff-format
  "D",      # Docstrings - will add incrementally
  "E501",   # Line length handled by config
  "EM",     # Exception strings inline are fine
  "TRY003", # Long exception messages are helpful for debugging
  "SIM108", # Ternary not always clearer
]

[tool.ruff.lint.flake8-annotations]
allow-star-arg-any = true
suppress-none-returning = true

[tool.ruff.lint.per-file-ignores]
"tests/**" = [
  "ANN",    # Type annotations not required in tests
  "ARG",    # Unused arguments common in fixtures
  "DTZ005", # Timezone-naive datetime okay in tests
  "F841",   # Unused variables okay in tests
  "FBT",    # Boolean args fine in test fixtures
  "PT006",  # Parametrize tuple style is preference
  "PT011",  # Broad pytest.raises okay in some tests
  "PT013",  # pytest import style is preference
  "PT018",  # Compound assertions okay in tests
  "RUF002", # Unicode in docstrings is fine
  "RUF015", # next(iter()) vs slice is preference
  "S101",   # assert in tests
  "S105",   # Hardcoded passwords in test settings
  "S311",   # random is fine for tests
]
"config/settings/**" = [
  "F403",   # Wildcard imports for settings splitting
  "F405",   # Undefined names from wildcard imports
]

# --- MyPy ---

[tool.mypy]
python_version = "3.12"
plugins = ["mypy_django_plugin.main"]
pretty = true
show_error_codes = true
show_error_context = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_unreachable = false

[tool.django-stubs]
django_settings_module = "config.settings.base"

[[tool.mypy.overrides]]
module = "testcontainers.*"
ignore_missing_imports = true

# --- ty ---

[tool.ty.environment]
python-version = "3.14"

[tool.ty.analysis]
respect-type-ignore-comments = false

[[tool.ty.overrides]]
include = ["tests/**"]

[tool.ty.overrides.rules]
unresolved-attribute = "ignore"
invalid-argument-type = "ignore"

# --- Pytest ---

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
addopts = "--cov=config --cov-report=term-missing --no-cov-on-fail"
pythonpath = ["."]
testpaths = ["tests"]
xfail_strict = true
asyncio_mode = "auto"

[tool.coverage.run]
omit = ["tests/*", "config/settings/production.py"]

[tool.coverage.report]
precision = 2
skip_covered = true

# --- djlint ---

[tool.djlint]
profile = "jinja"
indent = 2
max_line_length = 120
```

- [ ] **Step 3: Create `.gitignore`**

```gitignore
# Python
*.py[cod]
__pycache__/
*.egg-info/

# Virtual environment
.venv/

# IDE
.idea/
.vscode/
*.swp
\#*
.\#*
*~

# OS
.DS_Store

# Django
*.sqlite3
local_settings.py
media/

# Testing
.coverage
coverage.xml
htmlcov/

# Build
/build/
/dist/

# uv
# uv.lock is committed for reproducibility

# Node (for frontend tooling)
node_modules/

# Docker
dump.rdb

# Misc
*.log
CLAUDE.md
```

- [ ] **Step 4: Run `uv sync`**

Run: `uv sync --group dev`

Expected: dependencies resolve and install. Some of our packages may fail to resolve if not yet published — comment them out in pyproject.toml and retry if needed.

- [ ] **Step 5: Verify ruff loads config**

Run: `uv run ruff check --show-settings 2>&1 | head -5`

Expected: shows ruff configuration without errors.

- [ ] **Step 6: Commit**

```bash
git add .python-version pyproject.toml uv.lock .gitignore
git commit -m "feat: add project foundation (pyproject.toml, uv, gitignore)"
```

---

### Task 2: Django Project Config

**Files:**
- Create: `manage.py`
- Create: `config/__init__.py`
- Create: `config/asgi.py`
- Create: `config/wsgi.py`
- Create: `config/urls.py`
- Create: `config/jinja2.py`
- Create: `config/settings/__init__.py`
- Create: `config/settings/base.py`
- Create: `config/settings/local.py`
- Create: `config/settings/test.py`
- Create: `config/settings/production.py`

- [ ] **Step 1: Create `manage.py`**

```python
#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create `config/__init__.py`**

Empty file.

- [ ] **Step 3: Create `config/asgi.py`**

```python
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_asgi_application()
```

- [ ] **Step 4: Create `config/wsgi.py`**

```python
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
```

- [ ] **Step 5: Create `config/urls.py`**

```python
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
```

- [ ] **Step 6: Create `config/jinja2.py`**

```python
from django.templatetags.static import static
from django.urls import reverse

from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
        },
    )
    return env
```

- [ ] **Step 7: Create `config/settings/__init__.py`**

Empty file.

- [ ] **Step 8: Create `config/settings/base.py`**

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insecure-dev-key-change-in-production")

DEBUG = False

ALLOWED_HOSTS: list[str] = []

# --- Apps ---

INSTALLED_APPS = [
    # Admin theme (must be before admin)
    "unfold",
    "unfold.contrib.import_export",
    # Django admin (via django-adminx)
    "django_adminx.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Our packages
    "django_cachex",
    "django_celeryx.unfold",
    "django_formwork",
    # Third-party
    "allauth",
    "allauth.account",
    "cachalot",
    "django_celery_beat",
    "django_vite",
    "import_export",
    "pghistory",
    "pgtrigger",
    "waffle",
]

# --- Middleware ---

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "waffle.middleware.WaffleMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

# --- Templates ---

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "config.jinja2.environment",
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Database ---

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "voyager"),
        "USER": os.environ.get("POSTGRES_USER", "voyager"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "voyager"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Cache (Valkey via django-cachex) ---

CACHES = {
    "default": {
        "BACKEND": "django_cachex.cache.ValkeyCache",
        "LOCATION": os.environ.get("VALKEY_URL", "valkey://localhost:6379/0"),
    },
}

# --- Auth ---

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalization ---

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static files ---

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# --- Email ---

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# --- Celery ---

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "valkey://localhost:6379/1")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "valkey://localhost:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
```

- [ ] **Step 9: Create `config/settings/local.py`**

```python
from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Mailpit for local email testing
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
```

- [ ] **Step 10: Create `config/settings/test.py`**

```python
from .base import *  # noqa: F403

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use locmem cache in tests (no Valkey dependency)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

# Disable cachalot in tests to avoid cache interference
CACHALOT_ENABLED = False
```

- [ ] **Step 11: Create `config/settings/production.py`**

```python
import os

from .base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

- [ ] **Step 12: Verify Django loads**

Run: `DJANGO_SETTINGS_MODULE=config.settings.test uv run python manage.py check`

Expected: `System check identified no issues.` (or warnings about unapplied migrations, which is fine — no database yet).

If any package fails to import, comment it out in `INSTALLED_APPS` and retry. The goal is a bootable Django project.

- [ ] **Step 13: Commit**

```bash
git add manage.py config/
git commit -m "feat: add Django project config with full package wiring"
```

---

### Task 3: Templates, Static, Tests Scaffold

**Files:**
- Create: `templates/base.html`
- Create: `static/.gitkeep`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create `templates/base.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Voyager{% endblock %}</title>
  {% block head %}{% endblock %}
</head>
<body>
  {% block content %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: Create `static/.gitkeep`**

Empty file.

- [ ] **Step 3: Create `tests/__init__.py`**

Empty file.

- [ ] **Step 4: Create `tests/conftest.py`**

```python
import pytest


@pytest.fixture
def _db_access(db):
    """Shortcut fixture for tests that need database access."""
```

- [ ] **Step 5: Run pytest to verify scaffold**

Run: `uv run pytest --co -q`

Expected: `no tests ran` (or similar — no test files with test functions yet). No import errors.

- [ ] **Step 6: Commit**

```bash
git add templates/ static/ tests/
git commit -m "feat: add templates, static, and test scaffold"
```

---

### Task 4: Docker Compose

**Files:**
- Create: `docker-compose.yml`

- [ ] **Step 1: Create `docker-compose.yml`**

```yaml
services:
  postgres:
    image: postgres:17
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: voyager
      POSTGRES_USER: voyager
      POSTGRES_PASSWORD: voyager
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U voyager"]
      interval: 5s
      timeout: 5s
      retries: 5

  valkey:
    image: valkey/valkey:8
    ports:
      - "6379:6379"
    volumes:
      - valkey_data:/data
    healthcheck:
      test: ["CMD", "valkey-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  mailpit:
    image: axllent/mailpit
    ports:
      - "1025:1025"
      - "8025:8025"

volumes:
  postgres_data:
  valkey_data:
```

- [ ] **Step 2: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add Docker Compose for local dev (postgres, valkey, mailpit)"
```

---

### Task 5: Pre-commit Config

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: Create `.pre-commit-config.yaml`**

```yaml
default_stages: [pre-commit]
default_install_hook_types:
  - pre-commit
  - pre-push
fail_fast: false

default_language_version:
  python: python3.14

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-ast
      - id: check-case-conflict
      - id: check-json
      - id: check-merge-conflict
      - id: check-symlinks
      - id: check-toml
      - id: check-yaml
      - id: debug-statements
      - id: detect-private-key
      - id: end-of-file-fixer
        stages: [pre-commit]
      - id: mixed-line-ending
        args: ["--fix=lf"]

  - repo: https://github.com/ComPWA/taplo-pre-commit
    rev: v0.9.3
    hooks:
      - id: taplo-format
        args:
          ["--", "--indent-string", "  ", "--reorder-arrays", "--reorder-keys"]

  - repo: https://github.com/asottile/add-trailing-comma
    rev: v3.1.0
    hooks:
      - id: add-trailing-comma

  - repo: local
    hooks:
      - id: uv-sync-check
        name: uv-sync-check
        language: system
        entry: uv sync
        pass_filenames: false
      - id: ruff-check
        name: ruff-check
        entry: uv run ruff check --fix
        language: system
        pass_filenames: false
      - id: ruff-format
        name: ruff-format
        entry: uv run ruff format
        language: system
        pass_filenames: false
      - id: djlint-check
        name: djlint-check
        entry: uv run djlint templates/ --check
        language: system
        pass_filenames: false

  - repo: local
    hooks:
      - id: mypy
        name: mypy
        language: system
        entry: uv run mypy config/
        pass_filenames: false
        always_run: true
        stages: [pre-push]
      - id: ty
        name: ty
        language: system
        entry: uv run ty check config/
        pass_filenames: false
        always_run: true
        stages: [pre-push]
```

- [ ] **Step 2: Install pre-commit hooks**

Run: `uv run pre-commit install`

Expected: `pre-commit installed at .git/hooks/pre-commit`

- [ ] **Step 3: Run hooks on all files**

Run: `uv run pre-commit run --all-files`

Expected: all hooks pass (or minor auto-fixes applied). Fix any issues before proceeding.

- [ ] **Step 4: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "feat: add pre-commit config (ruff, mypy, ty, djlint, taplo)"
```

---

### Task 6: CI Workflow

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Install uv
        uses: astral-sh/setup-uv@v7

      - name: Set up Python
        run: uv python install 3.14t

      - name: Install dependencies
        run: uv sync --group dev

      - name: Run ruff check
        run: uv run ruff check

      - name: Run ruff format check
        run: uv run ruff format --check

      - name: Run djlint check
        run: uv run djlint templates/ --check

      - name: Run mypy
        run: uv run mypy config/

      - name: Run ty
        run: uv run ty check config/

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_DB: voyager
          POSTGRES_USER: voyager
          POSTGRES_PASSWORD: voyager
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U voyager"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
      valkey:
        image: valkey/valkey:8
        ports:
          - 6379:6379
        options: >-
          --health-cmd "valkey-cli ping"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v6

      - name: Install uv
        uses: astral-sh/setup-uv@v7

      - name: Set up Python
        run: uv python install 3.14t

      - name: Install dependencies
        run: uv sync --group dev

      - name: Run tests
        run: uv run pytest -n auto
```

- [ ] **Step 2: Commit**

```bash
git add .github/
git commit -m "feat: add CI workflow (lint + test with postgres and valkey)"
```

---

### Task 7: Final Verification

- [ ] **Step 1: Run full lint suite**

Run: `uv run ruff check && uv run ruff format --check`

Expected: no errors, no formatting issues.

- [ ] **Step 2: Run type checks**

Run: `uv run mypy config/`

Expected: no errors (or only expected ignores).

Run: `uv run ty check config/`

Expected: no errors.

- [ ] **Step 3: Run Django system check**

Run: `DJANGO_SETTINGS_MODULE=config.settings.test uv run python manage.py check`

Expected: `System check identified no issues.`

- [ ] **Step 4: Run pytest**

Run: `uv run pytest -v`

Expected: passes with 0 tests collected (no test functions yet), no import errors.

- [ ] **Step 5: Verify Docker Compose**

Run: `docker compose config --quiet`

Expected: no output (valid config).

- [ ] **Step 6: Commit any remaining fixes**

If any verification step required fixes, commit them:

```bash
git add -A
git commit -m "fix: address lint/type/check issues from final verification"
```

Skip this step if no fixes were needed.
