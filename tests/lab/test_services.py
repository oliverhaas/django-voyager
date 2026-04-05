from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone

from lab.models import EventImage, ProcessingStatus
from lab.services import (
    cleanup_orphaned_images,
    dispatch_webhook,
    ingest_collision_event,
    process_event_image,
    refresh_experiment_stats,
)

from .factories import (
    AcceleratorFactory,
    CollisionEventFactory,
    EventImageFactory,
    ExperimentFactory,
)


@pytest.mark.django_db
class TestIngestCollisionEvent:
    def test_creates_event(self):
        exp = ExperimentFactory()
        event = ingest_collision_event(
            experiment_id=exp.pk,
            data={
                "timestamp": timezone.now(),
                "energy_gev": Decimal("125.300"),
                "luminosity": Decimal("34.500"),
                "particle_count": 42,
                "raw_data": {},
            },
        )
        assert event.pk is not None
        assert event.experiment == exp

    def test_updates_experiment_stats(self):
        exp = ExperimentFactory()
        ingest_collision_event(
            experiment_id=exp.pk,
            data={
                "timestamp": timezone.now(),
                "energy_gev": Decimal("100.000"),
                "luminosity": Decimal("34.500"),
                "particle_count": 10,
                "raw_data": {},
            },
        )
        exp.refresh_from_db()
        assert exp.total_events == 1
        assert exp.avg_energy_gev == Decimal("100.000")


@pytest.mark.django_db
class TestRefreshExperimentStats:
    def test_updates_stats(self):
        exp = ExperimentFactory()
        CollisionEventFactory(experiment=exp, energy_gev=Decimal("100.000"))
        CollisionEventFactory(experiment=exp, energy_gev=Decimal("200.000"))
        refresh_experiment_stats(exp.pk)
        exp.refresh_from_db()
        assert exp.total_events == 2
        assert exp.avg_energy_gev == Decimal("150.000")

    def test_no_events(self):
        exp = ExperimentFactory()
        refresh_experiment_stats(exp.pk)
        exp.refresh_from_db()
        assert exp.total_events == 0
        assert exp.avg_energy_gev is None


@pytest.mark.django_db
class TestDispatchWebhook:
    def test_disabled_by_switch(self):
        acc = AcceleratorFactory(webhook_url="https://example.com/hook")
        result = dispatch_webhook(
            accelerator_id=acc.pk,
            event_type="collision",
            payload={"count": 1},
        )
        assert result is False

    def test_no_webhook_url(self):
        acc = AcceleratorFactory(webhook_url="")
        with patch("waffle.switch_is_active", return_value=True):
            result = dispatch_webhook(
                accelerator_id=acc.pk,
                event_type="collision",
                payload={"count": 1},
            )
        assert result is False

    @patch("lab.services._send_webhook")
    def test_sends_webhook(self, mock_send):
        acc = AcceleratorFactory(webhook_url="https://example.com/hook")
        with patch("waffle.switch_is_active", return_value=True):
            result = dispatch_webhook(
                accelerator_id=acc.pk,
                event_type="collision",
                payload={"count": 1},
            )
        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args[0][0] == "https://example.com/hook"
        assert call_args[0][1]["event_type"] == "collision"


@pytest.mark.django_db
class TestProcessEventImage:
    def test_generates_thumbnail_and_processed(self):
        image = EventImageFactory()
        process_event_image(image.pk)
        image.refresh_from_db()
        assert image.processing_status == ProcessingStatus.COMPLETED
        assert image.thumbnail.name != ""
        assert image.processed_image.name != ""

    def test_handles_failure(self):
        image = EventImageFactory()
        image.original_image.delete()
        process_event_image(image.pk)
        image.refresh_from_db()
        assert image.processing_status == ProcessingStatus.FAILED


@pytest.mark.django_db
class TestCleanupOrphanedImages:
    def test_deletes_old_failed_images(self):
        image = EventImageFactory(processing_status=ProcessingStatus.FAILED)
        EventImage.objects.filter(pk=image.pk).update(
            created_at=timezone.now() - timedelta(days=8),
        )
        count = cleanup_orphaned_images()
        assert count == 1
        assert not EventImage.objects.filter(pk=image.pk).exists()

    def test_keeps_recent_failed_images(self):
        image = EventImageFactory(processing_status=ProcessingStatus.FAILED)
        count = cleanup_orphaned_images()
        assert count == 0
        assert EventImage.objects.filter(pk=image.pk).exists()

    def test_keeps_completed_images(self):
        image = EventImageFactory(processing_status=ProcessingStatus.COMPLETED)
        EventImage.objects.filter(pk=image.pk).update(
            created_at=timezone.now() - timedelta(days=8),
        )
        count = cleanup_orphaned_images()
        assert count == 0
