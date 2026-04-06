from __future__ import annotations

import logging
import random
from decimal import Decimal
from io import BytesIO

from asgiref.sync import async_to_sync
from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image

from lab.models import Collision, EventImage, Experiment, ExperimentStatus
from lab.services import refresh_experiment_stats
from lab.tasks import process_event_image_task

logger = logging.getLogger(__name__)


@shared_task
def simulate_collisions() -> int:
    """Create 1-5 random collisions for random active experiments."""
    active_experiments = list(Experiment.objects.filter(status=ExperimentStatus.ACTIVE))
    if not active_experiments:
        logger.debug("No active experiments found, skipping collision simulation")
        return 0

    sample_size = min(random.randint(1, 3), len(active_experiments))
    chosen = random.sample(active_experiments, sample_size)
    collisions = []

    for experiment in chosen:
        count = random.randint(1, 5)
        now = timezone.now()
        for _ in range(count):
            energy = Decimal(str(round(random.uniform(100.0, 14000.0), 3)))
            luminosity = Decimal(str(round(random.uniform(1.0, 100.0), 3)))
            particle_count = random.randint(50, 10000)
            collisions.append(
                Collision(
                    experiment=experiment,
                    timestamp=now,
                    energy_gev=energy,
                    luminosity=luminosity,
                    particle_count=particle_count,
                    raw_data={
                        "detector": experiment.name,
                        "run_number": random.randint(1000, 99999),
                        "tracks": random.randint(10, 500),
                        "vertex_x": round(random.uniform(-0.1, 0.1), 6),
                        "vertex_y": round(random.uniform(-0.1, 0.1), 6),
                    },
                ),
            )

    Collision.objects.bulk_create(collisions)

    experiment_ids = {c.experiment_id for c in collisions}
    for experiment_id in experiment_ids:
        async_to_sync(refresh_experiment_stats)(experiment_id)

    total = len(collisions)
    logger.debug("Simulated %d collision(s) across %d experiment(s)", total, len(experiment_ids))
    return total


@shared_task
def simulate_image_upload() -> int:
    """Create an EventImage for a recent collision using a randomly colored test image."""
    recent_collision = Collision.objects.order_by("-timestamp").first()
    if recent_collision is None:
        logger.debug("No collisions found, skipping image upload simulation")
        return 0

    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    img = Image.new("RGB", (256, 256), color=(r, g, b))
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    event_image = EventImage(collision=recent_collision)
    filename = f"mock_{recent_collision.pk}_{timezone.now().strftime('%Y%m%d%H%M%S%f')}.png"
    event_image.original_image.save(filename, ContentFile(buf.read()), save=True)

    process_event_image_task.delay(event_image.pk)

    logger.debug("Created mock EventImage %d for collision %d", event_image.pk, recent_collision.pk)
    return event_image.pk


@shared_task
def cap_table_rows() -> dict[str, int]:
    """Cap large tables to prevent unbounded growth. Returns counts of deleted rows."""
    collision_limit = 1_000_000
    image_limit = 100_000

    _, collision_details = Collision.objects.filter(
        pk__in=Collision.objects.order_by("-pk").values("pk")[collision_limit:],
    ).delete()
    collisions_deleted = collision_details.get("lab.Collision", 0)

    _, image_details = EventImage.objects.filter(
        pk__in=EventImage.objects.order_by("-pk").values("pk")[image_limit:],
    ).delete()
    images_deleted = image_details.get("lab.EventImage", 0)

    if collisions_deleted:
        logger.info("cap_table_rows: deleted %d old Collision rows", collisions_deleted)
    if images_deleted:
        logger.info("cap_table_rows: deleted %d old EventImage rows", images_deleted)

    return {"collisions_deleted": collisions_deleted, "images_deleted": images_deleted}


@shared_task
def simulate_experiment_lifecycle() -> str | None:
    """Occasionally transition an experiment status to simulate the lifecycle."""
    # Try draft -> active first
    draft_experiment = Experiment.objects.filter(status=ExperimentStatus.DRAFT).order_by("?").first()
    if draft_experiment is not None:
        draft_experiment.status = ExperimentStatus.ACTIVE
        draft_experiment.started_at = timezone.now()
        draft_experiment.save()
        logger.info(
            "simulate_experiment_lifecycle: experiment %d (%s) draft -> active",
            draft_experiment.pk,
            draft_experiment.name,
        )
        return f"activated:{draft_experiment.pk}"

    # Otherwise complete an active experiment
    active_experiment = Experiment.objects.filter(status=ExperimentStatus.ACTIVE).order_by("?").first()
    if active_experiment is not None:
        active_experiment.status = ExperimentStatus.COMPLETED
        active_experiment.ended_at = timezone.now()
        active_experiment.save()
        logger.info(
            "simulate_experiment_lifecycle: experiment %d (%s) active -> completed",
            active_experiment.pk,
            active_experiment.name,
        )
        return f"completed:{active_experiment.pk}"

    logger.debug("simulate_experiment_lifecycle: no experiments to transition")
    return None
