"""Import all lab data from JSON fixtures via django-import-export."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from tablib import Dataset

from lab.resources import (
    AcceleratorResource,
    CollisionResource,
    ConferenceResource,
    ElementResource,
    EventImageResource,
    ExperimentCategoryResource,
    ExperimentResource,
    OrganizationResource,
)

# Import order: parents before children
RESOURCES = [
    ("element", ElementResource),
    ("accelerator", AcceleratorResource),
    ("experiment_category", ExperimentCategoryResource),
    ("experiment", ExperimentResource),
    ("collision", CollisionResource),
    ("event_image", EventImageResource),
    ("organization", OrganizationResource),
    ("conference", ConferenceResource),
]

DEFAULT_DIR = Path("fixtures")


class Command(BaseCommand):
    help = "Import all lab data from JSON files via django-import-export"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--dir",
            type=str,
            default=str(DEFAULT_DIR),
            help=f"Input directory (default: {DEFAULT_DIR})",
        )
        parser.add_argument(
            "--format",
            type=str,
            default="json",
            choices=["json", "csv", "yaml"],
            help="Import format (default: json)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate without saving",
        )

    def handle(self, **options: Any) -> None:
        input_dir = Path(options["dir"])
        fmt = options["format"]
        dry_run = options["dry_run"]

        if not input_dir.is_dir():
            self.stderr.write(self.style.ERROR(f"Directory not found: {input_dir}"))
            return

        for name, resource_cls in RESOURCES:
            filepath = input_dir / f"{name}.{fmt}"

            if not filepath.exists():
                self.stdout.write(self.style.WARNING(f"Skipping {name}: {filepath} not found"))
                continue

            resource = resource_cls()
            raw = filepath.read_text(encoding="utf-8")
            dataset = Dataset().load(raw, format=fmt)

            result = resource.import_data(dataset, dry_run=dry_run)

            if result.has_errors():
                self.stderr.write(self.style.ERROR(f"Errors importing {name}:"))
                for row_errors in result.row_errors():
                    for error in row_errors[1]:
                        self.stderr.write(f"  Row {row_errors[0]}: {error.error}")
            else:
                verb = "Would import" if dry_run else "Imported"
                self.stdout.write(self.style.SUCCESS(f"{verb} {result.total_rows} {name} from {filepath}"))
