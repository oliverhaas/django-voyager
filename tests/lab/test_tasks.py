from unittest.mock import patch

import pytest

from lab.tasks import (
    cleanup_orphaned_images_task,
    dispatch_webhook_task,
    process_event_image_task,
)

from .factories import AcceleratorFactory, EventImageFactory


@pytest.mark.django_db
class TestProcessEventImageTask:
    def test_calls_service(self):
        image = EventImageFactory()
        with patch("lab.tasks.process_event_image") as mock:
            process_event_image_task(image.pk)
        mock.assert_called_once_with(image.pk)


@pytest.mark.django_db
class TestDispatchWebhookTask:
    def test_calls_service(self):
        acc = AcceleratorFactory()
        with patch("lab.tasks.dispatch_webhook") as mock:
            dispatch_webhook_task(
                accelerator_id=acc.pk,
                event_type="collision",
                payload={"count": 1},
            )
        mock.assert_called_once_with(
            accelerator_id=acc.pk,
            event_type="collision",
            payload={"count": 1},
        )


class TestCleanupOrphanedImagesTask:
    def test_calls_service(self):
        with patch("lab.tasks.cleanup_orphaned_images", return_value=0) as mock:
            result = cleanup_orphaned_images_task()
        mock.assert_called_once()
        assert result == 0
