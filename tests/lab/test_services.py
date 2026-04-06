from datetime import timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from asgiref.sync import sync_to_async
from django.utils import timezone

from lab.models import EventImage, ProcessingStatus
from lab.services import (
    cleanup_orphaned_images,
    dispatch_webhook,
    ingest_collision,
    process_event_image,
    refresh_experiment_stats,
)

from .factories import (
    AcceleratorFactory,
    CollisionFactory,
    EventImageFactory,
    ExperimentFactory,
)


@pytest.mark.django_db(transaction=True)
class TestIngestCollision:
    async def test_creates_event(self):
        exp = await sync_to_async(ExperimentFactory)()
        event = await ingest_collision(
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

    async def test_updates_experiment_stats(self):
        exp = await sync_to_async(ExperimentFactory)()
        await ingest_collision(
            experiment_id=exp.pk,
            data={
                "timestamp": timezone.now(),
                "energy_gev": Decimal("100.000"),
                "luminosity": Decimal("34.500"),
                "particle_count": 10,
                "raw_data": {},
            },
        )
        await exp.arefresh_from_db()
        assert exp.total_events == 1
        assert exp.avg_energy_gev == Decimal("100.000")


@pytest.mark.django_db(transaction=True)
class TestRefreshExperimentStats:
    async def test_updates_stats(self):
        exp = await sync_to_async(ExperimentFactory)()
        await sync_to_async(CollisionFactory)(experiment=exp, energy_gev=Decimal("100.000"))
        await sync_to_async(CollisionFactory)(experiment=exp, energy_gev=Decimal("200.000"))
        await refresh_experiment_stats(exp.pk)
        await exp.arefresh_from_db()
        assert exp.total_events == 2
        assert exp.avg_energy_gev == Decimal("150.000")

    async def test_no_events(self):
        exp = await sync_to_async(ExperimentFactory)()
        await refresh_experiment_stats(exp.pk)
        await exp.arefresh_from_db()
        assert exp.total_events == 0
        assert exp.avg_energy_gev is None


@pytest.mark.django_db(transaction=True)
class TestDispatchWebhook:
    async def test_disabled_by_switch(self):
        acc = await sync_to_async(AcceleratorFactory)(webhook_url="https://example.com/hook")
        result = await dispatch_webhook(
            accelerator_id=acc.pk,
            event_type="collision",
            payload={"count": 1},
        )
        assert result is False

    async def test_no_webhook_url(self):
        acc = await sync_to_async(AcceleratorFactory)(webhook_url="")
        with patch("waffle.switch_is_active", return_value=True):
            result = await dispatch_webhook(
                accelerator_id=acc.pk,
                event_type="collision",
                payload={"count": 1},
            )
        assert result is False

    async def test_sends_webhook(self):
        acc = await sync_to_async(AcceleratorFactory)(webhook_url="https://example.com/hook")
        mock_send = AsyncMock()
        with patch("lab.services._send_webhook", mock_send), patch("waffle.switch_is_active", return_value=True):
            result = await dispatch_webhook(
                accelerator_id=acc.pk,
                event_type="collision",
                payload={"count": 1},
            )
        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args[0][0] == "https://example.com/hook"
        assert call_args[0][1]["event_type"] == "collision"


@pytest.mark.django_db(transaction=True)
class TestProcessEventImage:
    async def test_generates_thumbnail_and_processed(self):
        image = await sync_to_async(EventImageFactory)()
        await process_event_image(image.pk)
        await image.arefresh_from_db()
        assert image.processing_status == ProcessingStatus.COMPLETED
        assert image.thumbnail.name != ""
        assert image.processed_image.name != ""

    async def test_handles_failure(self):
        image = await sync_to_async(EventImageFactory)()
        await sync_to_async(image.original_image.delete)()
        await process_event_image(image.pk)
        await image.arefresh_from_db()
        assert image.processing_status == ProcessingStatus.FAILED


@pytest.mark.django_db(transaction=True)
class TestCleanupOrphanedImages:
    async def test_deletes_old_failed_images(self):
        image = await sync_to_async(EventImageFactory)(processing_status=ProcessingStatus.FAILED)
        await EventImage.objects.filter(pk=image.pk).aupdate(
            created_at=timezone.now() - timedelta(days=8),
        )
        count = await cleanup_orphaned_images()
        assert count == 1
        assert not await EventImage.objects.filter(pk=image.pk).aexists()

    async def test_keeps_recent_failed_images(self):
        image = await sync_to_async(EventImageFactory)(processing_status=ProcessingStatus.FAILED)
        count = await cleanup_orphaned_images()
        assert count == 0
        assert await EventImage.objects.filter(pk=image.pk).aexists()

    async def test_keeps_completed_images(self):
        image = await sync_to_async(EventImageFactory)(processing_status=ProcessingStatus.COMPLETED)
        await EventImage.objects.filter(pk=image.pk).aupdate(
            created_at=timezone.now() - timedelta(days=8),
        )
        count = await cleanup_orphaned_images()
        assert count == 0
