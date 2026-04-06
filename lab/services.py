from __future__ import annotations

import logging
from datetime import timedelta
from io import BytesIO

import httpx
import waffle
from django.core.files.base import ContentFile
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from PIL import Image, ImageFilter
from tenacity import retry, stop_after_attempt, wait_exponential

from lab.models import Accelerator, Collision, EventImage, Experiment, ProcessingStatus

logger = logging.getLogger(__name__)


def ingest_collision(*, experiment_id: int, data: dict) -> Collision:
    """Validate and create a collision event for the given experiment."""
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    event = Collision.objects.create(experiment=experiment, **data)
    refresh_experiment_stats(experiment.pk)
    return event


def refresh_experiment_stats(experiment_id: int) -> None:
    """Update denormalized stats on an experiment from its collision events."""
    stats = Collision.objects.filter(experiment_id=experiment_id).aggregate(
        total=Count("id"),
        avg_energy=Avg("energy_gev"),
    )
    Experiment.objects.filter(pk=experiment_id).update(
        total_events=stats["total"],
        avg_energy_gev=stats["avg_energy"],
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def _send_webhook(url: str, payload: dict) -> None:
    """Send a webhook POST request with retry logic."""
    response = httpx.post(url, json=payload, timeout=10)
    response.raise_for_status()


def dispatch_webhook(*, accelerator_id: int, event_type: str, payload: dict) -> bool:
    """Send webhook notification if the feature flag is enabled."""
    if not waffle.switch_is_active("enable_webhook_notifications"):
        logger.info("Webhook notifications disabled via feature flag")
        return False

    accelerator = get_object_or_404(Accelerator, pk=accelerator_id)
    if not accelerator.webhook_url:
        logger.info("No webhook URL configured for accelerator %s", accelerator.name)
        return False

    webhook_payload = {
        "event_type": event_type,
        "accelerator": accelerator.name,
        "data": payload,
    }
    _send_webhook(accelerator.webhook_url, webhook_payload)
    logger.info("Webhook dispatched to %s for %s", accelerator.webhook_url, event_type)
    return True


def process_event_image(event_image_id: int) -> None:
    """Generate thumbnail and processed version of an event image."""
    image = get_object_or_404(EventImage, pk=event_image_id)
    image.processing_status = ProcessingStatus.PROCESSING
    image.save()

    try:
        img = Image.open(image.original_image)

        # Generate thumbnail (300px max dimension)
        thumb = img.copy()
        thumb.thumbnail((300, 300))
        thumb_io = BytesIO()
        thumb.save(thumb_io, format="PNG")
        image.thumbnail.save(
            f"thumb_{image.pk}.png",
            ContentFile(thumb_io.getvalue()),
            save=False,
        )

        # Generate edge-detected version
        processed = img.filter(ImageFilter.FIND_EDGES)
        proc_io = BytesIO()
        processed.save(proc_io, format="PNG")
        image.processed_image.save(
            f"processed_{image.pk}.png",
            ContentFile(proc_io.getvalue()),
            save=False,
        )

        image.processing_status = ProcessingStatus.COMPLETED
        image.save()
    except Exception:
        logger.exception("Failed to process image %s", event_image_id)
        image.processing_status = ProcessingStatus.FAILED
        image.save()


def cleanup_orphaned_images() -> int:
    """Delete failed images older than 7 days. Returns count of deleted images."""
    cutoff = timezone.now() - timedelta(days=7)
    images = EventImage.objects.filter(
        processing_status=ProcessingStatus.FAILED,
        created_at__lt=cutoff,
    )
    count, _ = images.delete()
    logger.info("Cleaned up %d orphaned images", count)
    return count
