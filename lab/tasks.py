from asgiref.sync import async_to_sync
from celery import shared_task

from lab.services import cleanup_orphaned_images, dispatch_webhook, process_event_image


@shared_task
def process_event_image_task(event_image_id: int) -> None:
    """Background task to generate thumbnail and processed image."""
    async_to_sync(process_event_image)(event_image_id)


@shared_task
def dispatch_webhook_task(*, accelerator_id: int, event_type: str, payload: dict) -> bool:
    """Background task to send webhook notification."""
    return async_to_sync(dispatch_webhook)(
        accelerator_id=accelerator_id,
        event_type=event_type,
        payload=payload,
    )


@shared_task
def cleanup_orphaned_images_task() -> int:
    """Periodic task to clean up failed images older than 7 days."""
    return async_to_sync(cleanup_orphaned_images)()
