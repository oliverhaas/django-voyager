from django.shortcuts import get_object_or_404

from lab.models import CollisionEvent, Experiment


def ingest_collision_event(*, experiment_id: int, data: dict) -> CollisionEvent:
    """Validate and create a collision event for the given experiment."""
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    return CollisionEvent.objects.create(experiment=experiment, **data)
