from datetime import datetime
from decimal import Decimal

from django.shortcuts import aget_object_or_404
from ninja import Query, Router, Status

from lab.models import Accelerator, Collision, Element, EventImage, Experiment, ExperimentCategory
from lab.schemas import (
    AcceleratorIn,
    AcceleratorOut,
    AcceleratorPatch,
    CollisionBatchIn,
    CollisionBatchOut,
    CollisionIn,
    CollisionOut,
    CollisionPatch,
    ElementIn,
    ElementOut,
    ElementPatch,
    EventImageOut,
    EventImagePatch,
    ExperimentCategoryIn,
    ExperimentCategoryOut,
    ExperimentCategoryPatch,
    ExperimentIn,
    ExperimentOut,
    ExperimentPatch,
)
from lab.services import ingest_collision, refresh_experiment_stats

router = Router()


# ---------------------------------------------------------------------------
# Elements
# ---------------------------------------------------------------------------


@router.get("/elements/", response=list[ElementOut], tags=["Elements"])
async def list_elements(request):
    return [el async for el in Element.objects.all()]


@router.get("/elements/{atomic_number}/", response=ElementOut, tags=["Elements"])
async def get_element(request, atomic_number: int):
    return await aget_object_or_404(Element, atomic_number=atomic_number)


@router.post("/elements/", response={201: ElementOut}, tags=["Elements"])
async def create_element(request, payload: ElementIn):
    element = await Element.objects.acreate(**payload.dict())
    return Status(201, element)


@router.put("/elements/{atomic_number}/", response=ElementOut, tags=["Elements"])
async def update_element(request, atomic_number: int, payload: ElementIn):
    element = await aget_object_or_404(Element, atomic_number=atomic_number)
    for attr, value in payload.dict().items():
        setattr(element, attr, value)
    await element.asave()
    return element


@router.patch("/elements/{atomic_number}/", response=ElementOut, tags=["Elements"])
async def partial_update_element(request, atomic_number: int, payload: ElementPatch):
    element = await aget_object_or_404(Element, atomic_number=atomic_number)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(element, attr, value)
    await element.asave()
    return element


@router.delete("/elements/{atomic_number}/", response={204: None}, tags=["Elements"])
async def delete_element(request, atomic_number: int):
    element = await aget_object_or_404(Element, atomic_number=atomic_number)
    await element.adelete()
    return Status(204, None)


# ---------------------------------------------------------------------------
# Accelerators
# ---------------------------------------------------------------------------


@router.get("/accelerators/", response=list[AcceleratorOut], tags=["Accelerators"])
async def list_accelerators(request, is_active: bool | None = Query(None)):
    qs = Accelerator.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return [acc async for acc in qs]


@router.get("/accelerators/{id}/", response=AcceleratorOut, tags=["Accelerators"])
async def get_accelerator(request, id: int):
    return await aget_object_or_404(Accelerator, pk=id)


@router.post("/accelerators/", response={201: AcceleratorOut}, tags=["Accelerators"])
async def create_accelerator(request, payload: AcceleratorIn):
    accelerator = await Accelerator.objects.acreate(**payload.dict())
    return Status(201, accelerator)


@router.put("/accelerators/{id}/", response=AcceleratorOut, tags=["Accelerators"])
async def update_accelerator(request, id: int, payload: AcceleratorIn):
    accelerator = await aget_object_or_404(Accelerator, pk=id)
    for attr, value in payload.dict().items():
        setattr(accelerator, attr, value)
    await accelerator.asave()
    return accelerator


@router.patch("/accelerators/{id}/", response=AcceleratorOut, tags=["Accelerators"])
async def partial_update_accelerator(request, id: int, payload: AcceleratorPatch):
    accelerator = await aget_object_or_404(Accelerator, pk=id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(accelerator, attr, value)
    await accelerator.asave()
    return accelerator


@router.delete("/accelerators/{id}/", response={204: None}, tags=["Accelerators"])
async def delete_accelerator(request, id: int):
    accelerator = await aget_object_or_404(Accelerator, pk=id)
    await accelerator.adelete()
    return Status(204, None)


# ---------------------------------------------------------------------------
# Experiment Categories
# ---------------------------------------------------------------------------


@router.get("/categories/", response=list[ExperimentCategoryOut], tags=["Categories"])
async def list_categories(request):
    return [cat async for cat in ExperimentCategory.objects.all()]


@router.get("/categories/{id}/", response=ExperimentCategoryOut, tags=["Categories"])
async def get_category(request, id: int):
    return await aget_object_or_404(ExperimentCategory, pk=id)


@router.post("/categories/", response={201: ExperimentCategoryOut}, tags=["Categories"])
async def create_category(request, payload: ExperimentCategoryIn):
    category = await ExperimentCategory.objects.acreate(**payload.dict())
    return Status(201, category)


@router.put("/categories/{id}/", response=ExperimentCategoryOut, tags=["Categories"])
async def update_category(request, id: int, payload: ExperimentCategoryIn):
    category = await aget_object_or_404(ExperimentCategory, pk=id)
    for attr, value in payload.dict().items():
        setattr(category, attr, value)
    await category.asave()
    return category


@router.patch("/categories/{id}/", response=ExperimentCategoryOut, tags=["Categories"])
async def partial_update_category(request, id: int, payload: ExperimentCategoryPatch):
    category = await aget_object_or_404(ExperimentCategory, pk=id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(category, attr, value)
    await category.asave()
    return category


@router.delete("/categories/{id}/", response={204: None}, tags=["Categories"])
async def delete_category(request, id: int):
    category = await aget_object_or_404(ExperimentCategory, pk=id)
    await category.adelete()
    return Status(204, None)


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------


@router.get("/experiments/", response=list[ExperimentOut], tags=["Experiments"])
async def list_experiments(request, status: str | None = Query(None)):
    qs = Experiment.objects.all()
    if status:
        qs = qs.filter(status=status)
    return [exp async for exp in qs]


@router.get("/experiments/{id}/", response=ExperimentOut, tags=["Experiments"])
async def get_experiment(request, id: int):
    return await aget_object_or_404(Experiment, pk=id)


@router.post("/experiments/", response={201: ExperimentOut}, tags=["Experiments"])
async def create_experiment(request, payload: ExperimentIn):
    experiment = await Experiment.objects.acreate(**payload.dict())
    return Status(201, experiment)


@router.put("/experiments/{id}/", response=ExperimentOut, tags=["Experiments"])
async def update_experiment(request, id: int, payload: ExperimentIn):
    experiment = await aget_object_or_404(Experiment, pk=id)
    for attr, value in payload.dict().items():
        setattr(experiment, attr, value)
    await experiment.asave()
    return experiment


@router.patch("/experiments/{id}/", response=ExperimentOut, tags=["Experiments"])
async def partial_update_experiment(request, id: int, payload: ExperimentPatch):
    experiment = await aget_object_or_404(Experiment, pk=id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(experiment, attr, value)
    await experiment.asave()
    return experiment


@router.delete("/experiments/{id}/", response={204: None}, tags=["Experiments"])
async def delete_experiment(request, id: int):
    experiment = await aget_object_or_404(Experiment, pk=id)
    await experiment.adelete()
    return Status(204, None)


# ---------------------------------------------------------------------------
# Collisions
# ---------------------------------------------------------------------------


@router.get("/collisions/", response=list[CollisionOut], tags=["Collisions"])
async def list_collisions(
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
    return [col async for col in qs[:1000]]


@router.post("/collisions/batch/", response={201: CollisionBatchOut}, tags=["Collisions"])
async def create_collisions_batch(request, payload: CollisionBatchIn):
    objects = [
        Collision(
            experiment_id=item.experiment_id,
            timestamp=item.timestamp,
            energy_gev=item.energy_gev,
            luminosity=item.luminosity,
            particle_count=item.particle_count,
            raw_data=item.raw_data,
        )
        for item in payload.items
    ]
    created = await Collision.objects.abulk_create(objects)
    experiment_ids = {item.experiment_id for item in payload.items}
    for exp_id in experiment_ids:
        await refresh_experiment_stats(exp_id)
    return Status(201, CollisionBatchOut(created=len(created), items=created))


@router.get("/collisions/{id}/", response=CollisionOut, tags=["Collisions"])
async def get_collision(request, id: int):
    return await aget_object_or_404(Collision, pk=id)


@router.post("/collisions/", response={201: CollisionOut}, tags=["Collisions"])
async def create_collision(request, payload: CollisionIn):
    event = await ingest_collision(
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


@router.put("/collisions/{id}/", response=CollisionOut, tags=["Collisions"])
async def update_collision(request, id: int, payload: CollisionIn):
    collision = await aget_object_or_404(Collision, pk=id)
    for attr, value in payload.dict().items():
        setattr(collision, attr, value)
    await collision.asave()
    return collision


@router.patch("/collisions/{id}/", response=CollisionOut, tags=["Collisions"])
async def partial_update_collision(request, id: int, payload: CollisionPatch):
    collision = await aget_object_or_404(Collision, pk=id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(collision, attr, value)
    await collision.asave()
    return collision


@router.delete("/collisions/{id}/", response={204: None}, tags=["Collisions"])
async def delete_collision(request, id: int):
    collision = await aget_object_or_404(Collision, pk=id)
    await collision.adelete()
    return Status(204, None)


# ---------------------------------------------------------------------------
# Event Images
# ---------------------------------------------------------------------------


@router.get("/images/", response=list[EventImageOut], tags=["Images"])
async def list_images(request, collision_id: int | None = Query(None)):
    qs = EventImage.objects.all()
    if collision_id is not None:
        qs = qs.filter(collision_id=collision_id)
    return [img async for img in qs]


@router.get("/images/{id}/", response=EventImageOut, tags=["Images"])
async def get_image(request, id: int):
    return await aget_object_or_404(EventImage, pk=id)


@router.patch("/images/{id}/", response=EventImageOut, tags=["Images"])
async def partial_update_image(request, id: int, payload: EventImagePatch):
    image = await aget_object_or_404(EventImage, pk=id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(image, attr, value)
    await image.asave()
    return image


@router.delete("/images/{id}/", response={204: None}, tags=["Images"])
async def delete_image(request, id: int):
    image = await aget_object_or_404(EventImage, pk=id)
    await image.adelete()
    return Status(204, None)
