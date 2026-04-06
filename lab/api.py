from datetime import datetime
from decimal import Decimal

from ninja import Query, Router, Status

from lab.models import Collision, Element, Experiment
from lab.schemas import CollisionIn, CollisionOut, ElementOut, ExperimentOut
from lab.services import ingest_collision

router = Router()


@router.get("/elements/", response=list[ElementOut], tags=["Elements"])
def list_elements(request):
    return list(Element.objects.all())


@router.get("/experiments/", response=list[ExperimentOut], tags=["Experiments"])
def list_experiments(request, status: str | None = Query(None)):
    qs = Experiment.objects.all()
    if status:
        qs = qs.filter(status=status)
    return list(qs)


@router.post("/collisions/", response={201: CollisionOut}, tags=["Collisions"])
def create_collision(request, payload: CollisionIn):
    event = ingest_collision(
        experiment_id=payload.experiment_id,
        data={
            "timestamp": payload.timestamp,
            "energy_gev": payload.energy_gev,
            "luminosity": payload.luminosity,
            "particle_count": payload.particle_count,
            "raw_data": payload.raw_data,
        },
    )
    return Status(201, event)


@router.get("/collisions/", response=list[CollisionOut], tags=["Collisions"])
def list_collisions(
    request,
    experiment_id: int | None = Query(None),
    min_energy: Decimal | None = Query(None),
    max_energy: Decimal | None = Query(None),
    since: datetime | None = Query(None),
    until: datetime | None = Query(None),
):
    qs = Collision.objects.all()
    if experiment_id is not None:
        qs = qs.filter(experiment_id=experiment_id)
    if min_energy is not None:
        qs = qs.filter(energy_gev__gte=min_energy)
    if max_energy is not None:
        qs = qs.filter(energy_gev__lte=max_energy)
    if since is not None:
        qs = qs.filter(timestamp__gte=since)
    if until is not None:
        qs = qs.filter(timestamp__lte=until)
    return list(qs[:1000])
