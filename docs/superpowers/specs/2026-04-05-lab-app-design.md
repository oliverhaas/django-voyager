# Lab App Design

## Overview

Single Django app (`lab`) modeling a particle physics research platform. Provides the domain models, business logic, API, admin, and background tasks needed to exercise the full oliverhaas package stack plus all third-party integrations.

This is not meant to be a realistic physics application — it's a fun domain that naturally exercises webhooks, image processing, real-time data ingestion, large data volumes, tree hierarchies, audit logging, and admin-heavy workflows.

## Models

### Element

Periodic table reference data (~118 rows, essentially static).

**Fields:**
- `atomic_number` — PositiveSmallIntegerField, unique, primary key
- `symbol` — CharField(3), unique
- `name` — CharField(50), unique
- `atomic_mass` — DecimalField
- `category` — CharField(50) (e.g. "noble gas", "alkali metal", "transition metal")

**Package coverage:**
- **django-import-export** — bulk load periodic table from CSV in admin
- **django-cachex** — cache the full table (static data, rarely changes)

### Accelerator

Particle accelerators that generate collision data.

**Fields:**
- `name` — CharField(200), unique
- `location` — CharField(200)
- `max_energy_gev` — DecimalField
- `is_active` — BooleanField
- `commissioned_date` — DateField
- `webhook_url` — URLField(blank=True) — URL to POST notifications to

**Package coverage:**
- **httpx** — webhook dispatch to `webhook_url`
- **django-waffle** — feature flag `enable_webhook_notifications` gates webhook sending

### Experiment

Research experiments run at accelerators.

**Fields:**
- `name` — CharField(200)
- `description` — TextField(blank=True)
- `accelerator` — ForeignKey(Accelerator)
- `lead_researcher` — ForeignKey(User)
- `status` — CharField with choices: draft, active, completed, archived
- `category` — ForeignKey(ExperimentCategory, nullable) — tree hierarchy
- `started_at` — DateTimeField(nullable)
- `ended_at` — DateTimeField(nullable)
- `total_events` — PositiveIntegerField(default=0) — denormalized counter
- `avg_energy_gev` — DecimalField(nullable) — denormalized stat
- `created_at` — DateTimeField(auto_now_add)
- `updated_at` — DateTimeField(auto_now)

**Package coverage:**
- **django-tree-queries** — via ExperimentCategory model (see below)
- **django-pghistory** — audit trail on status changes
- **django-filthyfields** — dirty field tracking for conditional save logic (e.g. send notification only when status changes)
- **django-formwork** — create/edit experiment forms

### ExperimentCategory

Tree hierarchy for categorizing experiments (e.g. "High Energy Physics" > "Hadron Collisions" > "Higgs Searches").

**Fields:**
- `name` — CharField(200)
- `parent` — ForeignKey(self, nullable) — tree parent

**Package coverage:**
- **django-tree-queries** — TreeNode mixin for materialized path queries

### CollisionEvent

Individual collision events detected by accelerators. High-volume table.

**Fields:**
- `experiment` — ForeignKey(Experiment)
- `timestamp` — DateTimeField
- `energy_gev` — DecimalField
- `luminosity` — DecimalField
- `particle_count` — PositiveIntegerField
- `raw_data` — JSONField — arbitrary detector readings

**Package coverage:**
- **django-pgtrigger** — auto-update experiment stats (total_events, avg_energy_gev) on insert
- **django-ninja** — API endpoint for ingesting events
- Large data volume testing

### EventImage

Detector images attached to collision events.

**Fields:**
- `collision_event` — ForeignKey(CollisionEvent)
- `original_image` — ImageField
- `thumbnail` — ImageField(blank=True) — auto-generated
- `processed_image` — ImageField(blank=True) — auto-generated
- `processing_status` — CharField with choices: pending, processing, completed, failed
- `created_at` — DateTimeField(auto_now_add)

**Package coverage:**
- **pillow** — generate thumbnail (300px max) and processed version (edge detection)
- **celery-asyncio** — background image processing task
- **django-celery-beat** — periodic cleanup of failed/orphaned images

## Business Logic (services.py)

### ingest_collision_event(experiment_id, data)

Validates incoming event data, creates CollisionEvent record, queues image processing if images are attached. Called from the Ninja API endpoint. Dispatches webhook notification via Celery task.

### process_event_image(event_image_id) — Celery task

Reads the original image, generates a 300px thumbnail and a processed version (edge detection via Pillow's ImageFilter.FIND_EDGES), updates processing_status. Handles failures gracefully (sets status to "failed").

### dispatch_webhook(accelerator_id, event_type, payload) — Celery task

Sends POST request to accelerator.webhook_url via httpx with retry logic (tenacity). Gated behind waffle flag `enable_webhook_notifications`. Logs success/failure.

### cleanup_orphaned_images() — periodic Celery Beat task

Finds EventImage records with processing_status=failed older than 7 days. Retries processing or deletes them. Scheduled via django-celery-beat.

### refresh_experiment_stats(experiment_id)

Updates denormalized stats on Experiment (total_events, avg_energy_gev). Called via pgtrigger when CollisionEvent is inserted.

## API (Django Ninja)

Endpoints in `lab/api.py`, mounted at `/api/`:

- `POST /api/events/` — ingest collision events (simulates accelerator pushing data)
- `GET /api/events/` — list events with filtering (experiment, energy range, date range)
- `GET /api/experiments/` — list experiments with status filter
- `GET /api/elements/` — cached periodic table lookup

Pydantic schemas defined in `lab/schemas.py`.

## Admin

All models registered in `lab/admin.py`:

- **Element** — import/export enabled (CSV upload of periodic table)
- **Accelerator** — standard admin with list display
- **Experiment** — list filter by status/accelerator, search by name, pghistory audit trail visible in admin
- **ExperimentCategory** — tree display
- **CollisionEvent** — list filter by experiment, read-only (high volume, no manual editing)
- **EventImage** — inline on CollisionEvent detail, shows thumbnail preview

## File Structure

```
lab/
├── __init__.py
├── admin.py          # Admin registrations + import/export
├── api.py            # Ninja API endpoints
├── apps.py           # AppConfig
├── models.py         # All 6 models (Element, Accelerator, Experiment, ExperimentCategory, CollisionEvent, EventImage)
├── services.py       # Business logic functions
├── tasks.py          # Celery tasks (process_event_image, dispatch_webhook, cleanup)
├── triggers.py       # pgtrigger definitions
├── schemas.py        # Ninja/Pydantic schemas for API
└── migrations/
```

## Testing

```
tests/
├── conftest.py           # Shared fixtures (existing)
├── lab/
│   ├── __init__.py
│   ├── factories.py      # factory_boy factories for all models
│   ├── test_models.py    # Model validation, tree queries, dirty fields
│   ├── test_services.py  # Service logic, mocked Celery tasks
│   ├── test_api.py       # Ninja endpoint tests
│   ├── test_admin.py     # Admin smoke tests (pages load, import/export works)
│   └── test_tasks.py     # Celery task tests (image processing, webhooks)
```

Tests use test settings (locmem cache, MD5 hasher). Factory-boy for all test data. Small test image fixture for Pillow tests (generate a 1x1 PNG in the factory). Webhook tests mock httpx calls directly.
