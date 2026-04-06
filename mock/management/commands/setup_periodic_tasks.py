from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = "Create or update django-celery-beat PeriodicTask entries for mock workload simulation"

    def handle(self, *_args: Any, **_options: Any) -> None:
        every_2s, _ = IntervalSchedule.objects.get_or_create(every=2, period=IntervalSchedule.SECONDS)
        every_30s, _ = IntervalSchedule.objects.get_or_create(every=30, period=IntervalSchedule.SECONDS)
        every_5m, _ = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.MINUTES)
        every_15m, _ = IntervalSchedule.objects.get_or_create(every=15, period=IntervalSchedule.MINUTES)

        tasks = [
            {
                "name": "simulate_collisions",
                "task": "mock.tasks.simulate_collisions",
                "interval": every_2s,
            },
            {
                "name": "simulate_image_upload",
                "task": "mock.tasks.simulate_image_upload",
                "interval": every_30s,
            },
            {
                "name": "cap_table_rows",
                "task": "mock.tasks.cap_table_rows",
                "interval": every_15m,
            },
            {
                "name": "simulate_experiment_lifecycle",
                "task": "mock.tasks.simulate_experiment_lifecycle",
                "interval": every_5m,
            },
        ]

        for entry in tasks:
            _, created = PeriodicTask.objects.update_or_create(
                name=entry["name"],
                defaults={
                    "task": entry["task"],
                    "interval": entry["interval"],
                    "enabled": True,
                },
            )
            status = "created" if created else "updated"
            self.stdout.write(self.style.SUCCESS(f"PeriodicTask '{entry['name']}' {status}."))
