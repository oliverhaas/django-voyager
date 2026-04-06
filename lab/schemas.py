from datetime import date, datetime
from decimal import Decimal

from ninja import Schema

# --- Element ---


class ElementOut(Schema):
    atomic_number: int
    symbol: str
    name: str
    atomic_mass: Decimal
    category: str


class ElementIn(Schema):
    atomic_number: int
    symbol: str
    name: str
    atomic_mass: Decimal
    category: str


class ElementPatch(Schema):
    symbol: str | None = None
    name: str | None = None
    atomic_mass: Decimal | None = None
    category: str | None = None


# --- Accelerator ---


class AcceleratorOut(Schema):
    id: int
    name: str
    location: str
    max_energy_gev: Decimal
    is_active: bool
    commissioned_date: date
    webhook_url: str


class AcceleratorIn(Schema):
    name: str
    location: str
    max_energy_gev: Decimal
    is_active: bool = True
    commissioned_date: date
    webhook_url: str = ""


class AcceleratorPatch(Schema):
    name: str | None = None
    location: str | None = None
    max_energy_gev: Decimal | None = None
    is_active: bool | None = None
    commissioned_date: date | None = None
    webhook_url: str | None = None


# --- ExperimentCategory ---


class ExperimentCategoryOut(Schema):
    id: int
    name: str
    parent_id: int | None


class ExperimentCategoryIn(Schema):
    name: str
    parent_id: int | None = None


class ExperimentCategoryPatch(Schema):
    name: str | None = None
    parent_id: int | None = None


# --- Experiment ---


class ExperimentOut(Schema):
    id: int
    name: str
    description: str
    accelerator_id: int
    lead_researcher_id: int
    status: str
    category_id: int | None
    started_at: datetime | None
    ended_at: datetime | None
    total_events: int
    avg_energy_gev: Decimal | None
    created_at: datetime


class ExperimentIn(Schema):
    name: str
    description: str = ""
    accelerator_id: int
    lead_researcher_id: int
    status: str = "draft"
    category_id: int | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None


class ExperimentPatch(Schema):
    name: str | None = None
    description: str | None = None
    accelerator_id: int | None = None
    lead_researcher_id: int | None = None
    status: str | None = None
    category_id: int | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None


# --- Collision ---


class CollisionIn(Schema):
    experiment_id: int
    timestamp: datetime
    energy_gev: Decimal
    luminosity: Decimal
    particle_count: int
    raw_data: dict = {}


class CollisionOut(Schema):
    id: int
    experiment_id: int
    timestamp: datetime
    energy_gev: Decimal
    luminosity: Decimal
    particle_count: int
    raw_data: dict


class CollisionPatch(Schema):
    timestamp: datetime | None = None
    energy_gev: Decimal | None = None
    luminosity: Decimal | None = None
    particle_count: int | None = None
    raw_data: dict | None = None


class CollisionBatchIn(Schema):
    items: list[CollisionIn]


class CollisionBatchOut(Schema):
    created: int
    items: list[CollisionOut]


# --- EventImage ---


class EventImageOut(Schema):
    id: int
    collision_id: int
    original_image: str
    thumbnail: str | None
    processed_image: str | None
    processing_status: str
    created_at: datetime


class EventImagePatch(Schema):
    processing_status: str | None = None
