from __future__ import annotations

import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from argparse import ArgumentParser

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from lab.models import (
    Accelerator,
    CollisionEvent,
    Element,
    Experiment,
    ExperimentCategory,
    ExperimentStatus,
)

User = get_user_model()

ELEMENTS = [
    (1, "H", "Hydrogen", Decimal("1.008000"), "nonmetal"),
    (2, "He", "Helium", Decimal("4.003000"), "noble gas"),
    (3, "Li", "Lithium", Decimal("6.941000"), "alkali metal"),
    (4, "Be", "Beryllium", Decimal("9.012000"), "alkaline earth metal"),
    (5, "B", "Boron", Decimal("10.811000"), "metalloid"),
    (6, "C", "Carbon", Decimal("12.011000"), "nonmetal"),
    (7, "N", "Nitrogen", Decimal("14.007000"), "nonmetal"),
    (8, "O", "Oxygen", Decimal("15.999000"), "nonmetal"),
    (9, "F", "Fluorine", Decimal("18.998000"), "halogen"),
    (10, "Ne", "Neon", Decimal("20.180000"), "noble gas"),
    (11, "Na", "Sodium", Decimal("22.990000"), "alkali metal"),
    (12, "Mg", "Magnesium", Decimal("24.305000"), "alkaline earth metal"),
    (13, "Al", "Aluminium", Decimal("26.982000"), "post-transition metal"),
    (14, "Si", "Silicon", Decimal("28.086000"), "metalloid"),
    (15, "P", "Phosphorus", Decimal("30.974000"), "nonmetal"),
    (16, "S", "Sulfur", Decimal("32.065000"), "nonmetal"),
    (17, "Cl", "Chlorine", Decimal("35.453000"), "halogen"),
    (18, "Ar", "Argon", Decimal("39.948000"), "noble gas"),
    (19, "K", "Potassium", Decimal("39.098000"), "alkali metal"),
    (20, "Ca", "Calcium", Decimal("40.078000"), "alkaline earth metal"),
]


class Command(BaseCommand):
    help = "Seed the database with initial and test data"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--full",
            action="store_true",
            help="Seed everything: elements + test data (accelerators, experiments, events)",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all data before seeding",
        )

    def handle(self, *_args: Any, **options: Any) -> None:
        if options["flush"]:
            self._flush()

        self._seed_elements()

        if options["full"]:
            self._seed_test_data()

    def _flush(self) -> None:
        CollisionEvent.objects.all().delete()
        Experiment.objects.all().delete()
        ExperimentCategory.objects.all().delete()
        Accelerator.objects.all().delete()
        Element.objects.all().delete()
        User.objects.filter(is_superuser=True).delete()
        self.stdout.write(self.style.WARNING("Flushed all lab data."))

    def _seed_elements(self) -> None:
        count = 0
        for atomic_number, symbol, name, atomic_mass, category in ELEMENTS:
            _, created = Element.objects.update_or_create(
                atomic_number=atomic_number,
                defaults={
                    "symbol": symbol,
                    "name": name,
                    "atomic_mass": atomic_mass,
                    "category": category,
                },
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(ELEMENTS)} elements ({count} created)."))

    def _seed_test_data(self) -> None:
        self._seed_accelerators()
        self._seed_categories()
        self._seed_experiments()
        self._seed_superuser()

    def _seed_accelerators(self) -> None:
        accelerators_data = [
            {
                "name": "LHC",
                "location": "Geneva, Switzerland",
                "max_energy_gev": Decimal("13000.000"),
                "is_active": True,
                "commissioned_date": datetime.date(2008, 9, 10),
                "webhook_url": "",
            },
            {
                "name": "Tevatron",
                "location": "Batavia, Illinois, USA",
                "max_energy_gev": Decimal("1960.000"),
                "is_active": False,
                "commissioned_date": datetime.date(1983, 10, 13),
                "webhook_url": "",
            },
            {
                "name": "SuperKEKB",
                "location": "Tsukuba, Japan",
                "max_energy_gev": Decimal("10.580"),
                "is_active": True,
                "commissioned_date": datetime.date(2019, 3, 25),
                "webhook_url": "",
            },
        ]
        count = 0
        for data in accelerators_data:
            _, created = Accelerator.objects.update_or_create(
                name=data["name"],
                defaults={k: v for k, v in data.items() if k != "name"},
            )
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(accelerators_data)} accelerators ({count} created)."))

    def _seed_categories(self) -> None:
        categories_data = [
            {"name": "High Energy Physics", "parent_name": None},
            {"name": "Hadron Collider Experiments", "parent_name": "High Energy Physics"},
            {"name": "Lepton Collider Experiments", "parent_name": "High Energy Physics"},
            {"name": "Neutrino Physics", "parent_name": "High Energy Physics"},
        ]

        name_to_obj: dict[str, ExperimentCategory] = {}
        count = 0
        for data in categories_data:
            parent = name_to_obj.get(data["parent_name"]) if data["parent_name"] else None
            obj, created = ExperimentCategory.objects.get_or_create(
                name=data["name"],
                defaults={"parent": parent},
            )
            name_to_obj[data["name"]] = obj
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(categories_data)} experiment categories ({count} created)."))

    def _seed_experiments(self) -> None:
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@voyager.local",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if not admin_user.has_usable_password():
            admin_user.set_password("admin")
            admin_user.save()

        lhc = Accelerator.objects.get(name="LHC")
        tevatron = Accelerator.objects.get(name="Tevatron")
        superkekb = Accelerator.objects.get(name="SuperKEKB")

        try:
            hadron_cat = ExperimentCategory.objects.get(name="Hadron Collider Experiments")
            lepton_cat = ExperimentCategory.objects.get(name="Lepton Collider Experiments")
        except ExperimentCategory.DoesNotExist:
            hadron_cat = None
            lepton_cat = None

        now = timezone.now()

        experiments_data = [
            {
                "name": "ATLAS",
                "description": "A Toroidal LHC Apparatus — general-purpose particle physics detector at the LHC.",
                "accelerator": lhc,
                "lead_researcher": admin_user,
                "status": ExperimentStatus.ACTIVE,
                "category": hadron_cat,
                "started_at": now - datetime.timedelta(days=365 * 5),
                "ended_at": None,
                "avg_energy_gev": Decimal("6500.000"),
            },
            {
                "name": "CMS",
                "description": "Compact Muon Solenoid — general-purpose detector at the LHC.",
                "accelerator": lhc,
                "lead_researcher": admin_user,
                "status": ExperimentStatus.ACTIVE,
                "category": hadron_cat,
                "started_at": now - datetime.timedelta(days=365 * 5),
                "ended_at": None,
                "avg_energy_gev": Decimal("6500.000"),
            },
            {
                "name": "ALICE",
                "description": "A Large Ion Collider Experiment — heavy-ion detector at the LHC.",
                "accelerator": lhc,
                "lead_researcher": admin_user,
                "status": ExperimentStatus.ACTIVE,
                "category": hadron_cat,
                "started_at": now - datetime.timedelta(days=365 * 4),
                "ended_at": None,
                "avg_energy_gev": Decimal("2760.000"),
            },
            {
                "name": "D0",
                "description": "D-Zero experiment at the Tevatron proton-antiproton collider.",
                "accelerator": tevatron,
                "lead_researcher": admin_user,
                "status": ExperimentStatus.COMPLETED,
                "category": hadron_cat,
                "started_at": now - datetime.timedelta(days=365 * 20),
                "ended_at": now - datetime.timedelta(days=365 * 11),
                "avg_energy_gev": Decimal("980.000"),
            },
            {
                "name": "Belle II",
                "description": "B-physics experiment at the SuperKEKB electron-positron collider.",
                "accelerator": superkekb,
                "lead_researcher": admin_user,
                "status": ExperimentStatus.ACTIVE,
                "category": lepton_cat,
                "started_at": now - datetime.timedelta(days=365 * 3),
                "ended_at": None,
                "avg_energy_gev": Decimal("5.290"),
            },
            {
                "name": "LHCb",
                "description": "LHC beauty — experiment dedicated to b-physics at the LHC.",
                "accelerator": lhc,
                "lead_researcher": admin_user,
                "status": ExperimentStatus.DRAFT,
                "category": hadron_cat,
                "started_at": None,
                "ended_at": None,
                "avg_energy_gev": None,
            },
        ]

        count = 0
        experiments = []
        for data in experiments_data:
            obj, created = Experiment.objects.get_or_create(
                name=data["name"],
                defaults={k: v for k, v in data.items() if k != "name"},
            )
            experiments.append(obj)
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(experiments_data)} experiments ({count} created)."))

        self._seed_collision_events(experiments)

    def _seed_collision_events(self, experiments: list[Experiment]) -> None:
        active_experiments = [e for e in experiments if e.status == ExperimentStatus.ACTIVE]

        total_created = 0
        base_time = timezone.now() - datetime.timedelta(days=30)

        energy_by_experiment = {
            "ATLAS": Decimal("6500.000"),
            "CMS": Decimal("6500.000"),
            "ALICE": Decimal("2760.000"),
            "Belle II": Decimal("5.290"),
        }

        for i, experiment in enumerate(active_experiments):
            base_energy = energy_by_experiment.get(experiment.name, Decimal("1000.000"))
            events_to_create = 20 if i == 0 else 15

            existing_count = CollisionEvent.objects.filter(experiment=experiment).count()
            if existing_count >= events_to_create:
                continue

            for j in range(events_to_create - existing_count):
                energy_variation = Decimal(str(j % 5)) * Decimal("10.000")
                CollisionEvent.objects.create(
                    experiment=experiment,
                    timestamp=base_time + datetime.timedelta(hours=j * 6 + i * 24),
                    energy_gev=base_energy + energy_variation,
                    luminosity=Decimal("34.500") + Decimal(str(j % 3)) * Decimal("0.100"),
                    particle_count=100 + j * 10 + i * 5,
                    raw_data={
                        "detector": experiment.name,
                        "run_number": 1000 + j,
                        "tracks": 50 + j * 2,
                        "vertex_x": 0.001 * j,
                        "vertex_y": -0.001 * j,
                    },
                )
                total_created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {total_created} collision events."))

    def _seed_superuser(self) -> None:
        if User.objects.filter(username="admin").exists():
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' already exists."))
            return
        User.objects.create_superuser("admin", "admin@voyager.local", "admin")
        self.stdout.write(self.style.SUCCESS("Created superuser admin/admin."))
