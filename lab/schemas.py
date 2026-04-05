from datetime import datetime
from decimal import Decimal

from ninja import Schema


class ElementOut(Schema):
    atomic_number: int
    symbol: str
    name: str
    atomic_mass: Decimal
    category: str


class ExperimentOut(Schema):
    id: int
    name: str
    description: str
    accelerator_id: int
    lead_researcher_id: int
    status: str
    total_events: int
    avg_energy_gev: Decimal | None
    created_at: datetime


class CollisionEventIn(Schema):
    experiment_id: int
    timestamp: datetime
    energy_gev: Decimal
    luminosity: Decimal
    particle_count: int
    raw_data: dict = {}


class CollisionEventOut(Schema):
    id: int
    experiment_id: int
    timestamp: datetime
    energy_gev: Decimal
    luminosity: Decimal
    particle_count: int
    raw_data: dict
