from datetime import datetime
from decimal import Decimal

from ninja import Query, Router, Status

from lab.models import CollisionEvent, Element, Experiment
from lab.schemas import CollisionEventIn, CollisionEventOut, ElementOut, ExperimentOut
from lab.services import ingest_collision_event

router = Router()


@router.get("/elements/", response=list[ElementOut])
def list_elements(request):
    return list(Element.objects.all())


@router.get("/experiments/", response=list[ExperimentOut])
def list_experiments(request, status: str | None = Query(None)):
    qs = Experiment.objects.all()
    if status:
        qs = qs.filter(status=status)
    return list(qs)


@router.post("/events/", response={201: CollisionEventOut})
def create_event(request, payload: CollisionEventIn):
    event = ingest_collision_event(
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


@router.get("/events/", response=list[CollisionEventOut])
def list_events(
    request,
    experiment_id: int | None = Query(None),
    min_energy: Decimal | None = Query(None),
    max_energy: Decimal | None = Query(None),
    since: datetime | None = Query(None),
    until: datetime | None = Query(None),
):
    qs = CollisionEvent.objects.all()
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
