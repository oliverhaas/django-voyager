from __future__ import annotations

import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from argparse import ArgumentParser

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from lab.models import (
    Accelerator,
    Collision,
    Conference,
    Element,
    Experiment,
    ExperimentCategory,
    ExperimentStatus,
    Organization,
    OrgType,
)
from lab.services import refresh_experiment_stats as _async_refresh_experiment_stats

refresh_experiment_stats = async_to_sync(_async_refresh_experiment_stats)

User = get_user_model()

ELEMENTS = [
    # Period 1
    (1, "H", "Hydrogen", Decimal("1.008000"), "nonmetal"),
    (2, "He", "Helium", Decimal("4.002602"), "noble gas"),
    # Period 2
    (3, "Li", "Lithium", Decimal("6.941000"), "alkali metal"),
    (4, "Be", "Beryllium", Decimal("9.012182"), "alkaline earth metal"),
    (5, "B", "Boron", Decimal("10.811000"), "metalloid"),
    (6, "C", "Carbon", Decimal("12.011000"), "nonmetal"),
    (7, "N", "Nitrogen", Decimal("14.007000"), "nonmetal"),
    (8, "O", "Oxygen", Decimal("15.999000"), "nonmetal"),
    (9, "F", "Fluorine", Decimal("18.998403"), "halogen"),
    (10, "Ne", "Neon", Decimal("20.179700"), "noble gas"),
    # Period 3
    (11, "Na", "Sodium", Decimal("22.989769"), "alkali metal"),
    (12, "Mg", "Magnesium", Decimal("24.305000"), "alkaline earth metal"),
    (13, "Al", "Aluminium", Decimal("26.981538"), "post-transition metal"),
    (14, "Si", "Silicon", Decimal("28.085000"), "metalloid"),
    (15, "P", "Phosphorus", Decimal("30.973762"), "nonmetal"),
    (16, "S", "Sulfur", Decimal("32.060000"), "nonmetal"),
    (17, "Cl", "Chlorine", Decimal("35.450000"), "halogen"),
    (18, "Ar", "Argon", Decimal("39.948000"), "noble gas"),
    # Period 4
    (19, "K", "Potassium", Decimal("39.098300"), "alkali metal"),
    (20, "Ca", "Calcium", Decimal("40.078000"), "alkaline earth metal"),
    (21, "Sc", "Scandium", Decimal("44.955908"), "transition metal"),
    (22, "Ti", "Titanium", Decimal("47.867000"), "transition metal"),
    (23, "V", "Vanadium", Decimal("50.941500"), "transition metal"),
    (24, "Cr", "Chromium", Decimal("51.996100"), "transition metal"),
    (25, "Mn", "Manganese", Decimal("54.938044"), "transition metal"),
    (26, "Fe", "Iron", Decimal("55.845000"), "transition metal"),
    (27, "Co", "Cobalt", Decimal("58.933194"), "transition metal"),
    (28, "Ni", "Nickel", Decimal("58.693400"), "transition metal"),
    (29, "Cu", "Copper", Decimal("63.546000"), "transition metal"),
    (30, "Zn", "Zinc", Decimal("65.380000"), "transition metal"),
    (31, "Ga", "Gallium", Decimal("69.723000"), "post-transition metal"),
    (32, "Ge", "Germanium", Decimal("72.630000"), "metalloid"),
    (33, "As", "Arsenic", Decimal("74.921595"), "metalloid"),
    (34, "Se", "Selenium", Decimal("78.971000"), "nonmetal"),
    (35, "Br", "Bromine", Decimal("79.904000"), "halogen"),
    (36, "Kr", "Krypton", Decimal("83.798000"), "noble gas"),
    # Period 5
    (37, "Rb", "Rubidium", Decimal("85.467800"), "alkali metal"),
    (38, "Sr", "Strontium", Decimal("87.620000"), "alkaline earth metal"),
    (39, "Y", "Yttrium", Decimal("88.905840"), "transition metal"),
    (40, "Zr", "Zirconium", Decimal("91.224000"), "transition metal"),
    (41, "Nb", "Niobium", Decimal("92.906370"), "transition metal"),
    (42, "Mo", "Molybdenum", Decimal("95.950000"), "transition metal"),
    (43, "Tc", "Technetium", Decimal("97.000000"), "transition metal"),
    (44, "Ru", "Ruthenium", Decimal("101.070000"), "transition metal"),
    (45, "Rh", "Rhodium", Decimal("102.905500"), "transition metal"),
    (46, "Pd", "Palladium", Decimal("106.420000"), "transition metal"),
    (47, "Ag", "Silver", Decimal("107.868200"), "transition metal"),
    (48, "Cd", "Cadmium", Decimal("112.414000"), "transition metal"),
    (49, "In", "Indium", Decimal("114.818000"), "post-transition metal"),
    (50, "Sn", "Tin", Decimal("118.710000"), "post-transition metal"),
    (51, "Sb", "Antimony", Decimal("121.760000"), "metalloid"),
    (52, "Te", "Tellurium", Decimal("127.600000"), "metalloid"),
    (53, "I", "Iodine", Decimal("126.904470"), "halogen"),
    (54, "Xe", "Xenon", Decimal("131.293000"), "noble gas"),
    # Period 6
    (55, "Cs", "Caesium", Decimal("132.905452"), "alkali metal"),
    (56, "Ba", "Barium", Decimal("137.327000"), "alkaline earth metal"),
    (57, "La", "Lanthanum", Decimal("138.905470"), "lanthanide"),
    (58, "Ce", "Cerium", Decimal("140.116000"), "lanthanide"),
    (59, "Pr", "Praseodymium", Decimal("140.907660"), "lanthanide"),
    (60, "Nd", "Neodymium", Decimal("144.242000"), "lanthanide"),
    (61, "Pm", "Promethium", Decimal("145.000000"), "lanthanide"),
    (62, "Sm", "Samarium", Decimal("150.360000"), "lanthanide"),
    (63, "Eu", "Europium", Decimal("151.964000"), "lanthanide"),
    (64, "Gd", "Gadolinium", Decimal("157.250000"), "lanthanide"),
    (65, "Tb", "Terbium", Decimal("158.925350"), "lanthanide"),
    (66, "Dy", "Dysprosium", Decimal("162.500000"), "lanthanide"),
    (67, "Ho", "Holmium", Decimal("164.930330"), "lanthanide"),
    (68, "Er", "Erbium", Decimal("167.259000"), "lanthanide"),
    (69, "Tm", "Thulium", Decimal("168.934220"), "lanthanide"),
    (70, "Yb", "Ytterbium", Decimal("173.045000"), "lanthanide"),
    (71, "Lu", "Lutetium", Decimal("174.966800"), "lanthanide"),
    (72, "Hf", "Hafnium", Decimal("178.490000"), "transition metal"),
    (73, "Ta", "Tantalum", Decimal("180.947880"), "transition metal"),
    (74, "W", "Tungsten", Decimal("183.840000"), "transition metal"),
    (75, "Re", "Rhenium", Decimal("186.207000"), "transition metal"),
    (76, "Os", "Osmium", Decimal("190.230000"), "transition metal"),
    (77, "Ir", "Iridium", Decimal("192.217000"), "transition metal"),
    (78, "Pt", "Platinum", Decimal("195.084000"), "transition metal"),
    (79, "Au", "Gold", Decimal("196.966569"), "transition metal"),
    (80, "Hg", "Mercury", Decimal("200.592000"), "transition metal"),
    (81, "Tl", "Thallium", Decimal("204.380000"), "post-transition metal"),
    (82, "Pb", "Lead", Decimal("207.200000"), "post-transition metal"),
    (83, "Bi", "Bismuth", Decimal("208.980400"), "post-transition metal"),
    (84, "Po", "Polonium", Decimal("209.000000"), "post-transition metal"),
    (85, "At", "Astatine", Decimal("210.000000"), "halogen"),
    (86, "Rn", "Radon", Decimal("222.000000"), "noble gas"),
    # Period 7
    (87, "Fr", "Francium", Decimal("223.000000"), "alkali metal"),
    (88, "Ra", "Radium", Decimal("226.000000"), "alkaline earth metal"),
    (89, "Ac", "Actinium", Decimal("227.000000"), "actinide"),
    (90, "Th", "Thorium", Decimal("232.038060"), "actinide"),
    (91, "Pa", "Protactinium", Decimal("231.035880"), "actinide"),
    (92, "U", "Uranium", Decimal("238.028910"), "actinide"),
    (93, "Np", "Neptunium", Decimal("237.000000"), "actinide"),
    (94, "Pu", "Plutonium", Decimal("244.000000"), "actinide"),
    (95, "Am", "Americium", Decimal("243.000000"), "actinide"),
    (96, "Cm", "Curium", Decimal("247.000000"), "actinide"),
    (97, "Bk", "Berkelium", Decimal("247.000000"), "actinide"),
    (98, "Cf", "Californium", Decimal("251.000000"), "actinide"),
    (99, "Es", "Einsteinium", Decimal("252.000000"), "actinide"),
    (100, "Fm", "Fermium", Decimal("257.000000"), "actinide"),
    (101, "Md", "Mendelevium", Decimal("258.000000"), "actinide"),
    (102, "No", "Nobelium", Decimal("259.000000"), "actinide"),
    (103, "Lr", "Lawrencium", Decimal("262.000000"), "actinide"),
    (104, "Rf", "Rutherfordium", Decimal("267.000000"), "transition metal"),
    (105, "Db", "Dubnium", Decimal("268.000000"), "transition metal"),
    (106, "Sg", "Seaborgium", Decimal("271.000000"), "transition metal"),
    (107, "Bh", "Bohrium", Decimal("272.000000"), "transition metal"),
    (108, "Hs", "Hassium", Decimal("270.000000"), "transition metal"),
    (109, "Mt", "Meitnerium", Decimal("278.000000"), "transition metal"),
    (110, "Ds", "Darmstadtium", Decimal("281.000000"), "transition metal"),
    (111, "Rg", "Roentgenium", Decimal("282.000000"), "transition metal"),
    (112, "Cn", "Copernicium", Decimal("285.000000"), "transition metal"),
    (113, "Nh", "Nihonium", Decimal("286.000000"), "post-transition metal"),
    (114, "Fl", "Flerovium", Decimal("289.000000"), "post-transition metal"),
    (115, "Mc", "Moscovium", Decimal("290.000000"), "post-transition metal"),
    (116, "Lv", "Livermorium", Decimal("293.000000"), "post-transition metal"),
    (117, "Ts", "Tennessine", Decimal("294.000000"), "halogen"),
    (118, "Og", "Oganesson", Decimal("294.000000"), "noble gas"),
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
        Collision.objects.all().delete()
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
        self._seed_organizations()
        self._seed_conferences()
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
        categories_data: list[dict[str, str | None]] = [
            {"name": "High Energy Physics", "parent_name": None},
            {"name": "Hadron Collider Experiments", "parent_name": "High Energy Physics"},
            {"name": "Lepton Collider Experiments", "parent_name": "High Energy Physics"},
            {"name": "Neutrino Physics", "parent_name": "High Energy Physics"},
        ]

        name_to_obj: dict[str, ExperimentCategory] = {}
        count = 0
        for data in categories_data:
            parent_name = data["parent_name"]
            name = data["name"] or ""
            parent = name_to_obj.get(parent_name) if parent_name else None
            obj, created = ExperimentCategory.objects.get_or_create(
                name=name,
                defaults={"parent": parent},
            )
            name_to_obj[name] = obj
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

        self._seed_collisions(experiments)

    def _seed_collisions(self, experiments: list[Experiment]) -> None:
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

            existing_count = Collision.objects.filter(experiment=experiment).count()
            if existing_count >= events_to_create:
                continue

            for j in range(events_to_create - existing_count):
                energy_variation = Decimal(str(j % 5)) * Decimal("10.000")
                Collision.objects.create(
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

        # Update denormalized stats
        for experiment in experiments:
            refresh_experiment_stats(experiment.pk)

    def _seed_organizations(self) -> None:
        organizations_data = [
            {
                "name": "European Organization for Nuclear Research",
                "abbreviation": "CERN",
                "location": "Geneva, Switzerland",
                "website": "https://home.cern",
                "org_type": OrgType.LABORATORY,
            },
            {
                "name": "Fermi National Accelerator Laboratory",
                "abbreviation": "Fermilab",
                "location": "Batavia, Illinois, USA",
                "website": "https://www.fnal.gov",
                "org_type": OrgType.LABORATORY,
            },
            {
                "name": "High Energy Accelerator Research Organization",
                "abbreviation": "KEK",
                "location": "Tsukuba, Japan",
                "website": "https://www.kek.jp",
                "org_type": OrgType.LABORATORY,
            },
            {
                "name": "Massachusetts Institute of Technology",
                "abbreviation": "MIT",
                "location": "Cambridge, Massachusetts, USA",
                "website": "https://www.mit.edu",
                "org_type": OrgType.UNIVERSITY,
            },
        ]
        count = 0
        for data in organizations_data:
            _, created = Organization.objects.update_or_create(
                name=data["name"],
                defaults={k: v for k, v in data.items() if k != "name"},
            )
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(organizations_data)} organizations ({count} created)."))

    def _seed_conferences(self) -> None:
        try:
            cern = Organization.objects.get(abbreviation="CERN")
            fermilab = Organization.objects.get(abbreviation="Fermilab")
        except Organization.DoesNotExist:
            cern = None
            fermilab = None

        atlas = Experiment.objects.filter(name="ATLAS").first()
        cms = Experiment.objects.filter(name="CMS").first()
        alice = Experiment.objects.filter(name="ALICE").first()
        d0 = Experiment.objects.filter(name="D0").first()

        conferences_data = [
            {
                "name": "International Conference on High Energy Physics 2026",
                "abbreviation": "ICHEP 2026",
                "location": "Prague, Czech Republic",
                "start_date": datetime.date(2026, 7, 18),
                "end_date": datetime.date(2026, 7, 25),
                "website": "https://ichep2026.cz",
                "description": "Biennial conference covering the latest results in high energy physics.",
                "organizer": cern,
                "experiments": [e for e in [atlas, cms, alice] if e is not None],
            },
            {
                "name": "Large Hadron Collider Physics Conference 2025",
                "abbreviation": "LHCP 2025",
                "location": "Split, Croatia",
                "start_date": datetime.date(2025, 6, 2),
                "end_date": datetime.date(2025, 6, 7),
                "website": "",
                "description": "Annual conference on physics results from the LHC experiments.",
                "organizer": cern,
                "experiments": [e for e in [atlas, cms] if e is not None],
            },
            {
                "name": "Moriond Electroweak 2025",
                "abbreviation": "Moriond EW 2025",
                "location": "La Thuile, Italy",
                "start_date": datetime.date(2025, 3, 15),
                "end_date": datetime.date(2025, 3, 22),
                "website": "",
                "description": "Rencontres de Moriond — electroweak interactions and unified theories.",
                "organizer": fermilab,
                "experiments": [e for e in [d0, cms] if e is not None],
            },
        ]
        count = 0
        for data in conferences_data:
            experiments = data.pop("experiments")
            obj, created = Conference.objects.get_or_create(
                name=data["name"],
                defaults={k: v for k, v in data.items() if k != "name"},
            )
            if experiments:
                obj.experiments.set(experiments)
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(conferences_data)} conferences ({count} created)."))

    def _seed_superuser(self) -> None:
        if User.objects.filter(username="admin").exists():
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' already exists."))
            return
        User.objects.create_superuser("admin", "admin@voyager.local", "admin")
        self.stdout.write(self.style.SUCCESS("Created superuser admin/admin."))
