"""Export all lab data to JSON fixtures via django-import-export."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from lab.resources import (
    AcceleratorResource,
    CollisionResource,
    ElementResource,
    EventImageResource,
    ExperimentCategoryResource,
    ExperimentResource,
)

# Export order: parents before children
RESOURCES = [
    ("element", ElementResource),
    ("accelerator", AcceleratorResource),
    ("experiment_category", ExperimentCategoryResource),
    ("experiment", ExperimentResource),
    ("collision", CollisionResource),
    ("event_image", EventImageResource),
]

DEFAULT_DIR = Path("fixtures")


class Command(BaseCommand):
    help = "Export all lab data to JSON files via django-import-export"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--dir",
            type=str,
            default=str(DEFAULT_DIR),
            help=f"Output directory (default: {DEFAULT_DIR})",
        )
        parser.add_argument(
            "--format",
            type=str,
            default="json",
            choices=["json", "csv", "yaml"],
            help="Export format (default: json)",
        )

    def handle(self, **options: Any) -> None:
        output_dir = Path(options["dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        fmt = options["format"]

        for name, resource_cls in RESOURCES:
            resource = resource_cls()
            dataset = resource.export()

            filepath = output_dir / f"{name}.{fmt}"
            export_data = getattr(dataset, fmt)
            filepath.write_text(export_data, encoding="utf-8")

            count = len(dataset)
            self.stdout.write(self.style.SUCCESS(f"Exported {count} {name} to {filepath}"))
