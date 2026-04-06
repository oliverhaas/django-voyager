import pytest

from lab.models import ExperimentStatus

from .factories import (
    AcceleratorFactory,
    CollisionFactory,
    ElementFactory,
    ExperimentCategoryFactory,
    ExperimentFactory,
)


@pytest.mark.django_db
class TestElement:
    def test_str(self):
        element = ElementFactory(symbol="H", name="Hydrogen")
        assert str(element) == "H (Hydrogen)"

    def test_ordering(self):
        e2 = ElementFactory(atomic_number=2, symbol="He", name="Helium")
        e1 = ElementFactory(atomic_number=1, symbol="H", name="Hydrogen")
        from lab.models import Element

        elements = list(Element.objects.all())
        assert elements == [e1, e2]


@pytest.mark.django_db
class TestAccelerator:
    def test_str(self):
        acc = AcceleratorFactory(name="LHC")
        assert str(acc) == "LHC"


@pytest.mark.django_db
class TestExperimentCategory:
    def test_str(self):
        cat = ExperimentCategoryFactory(name="High Energy Physics")
        assert str(cat) == "High Energy Physics"

    def test_tree_hierarchy(self):
        parent = ExperimentCategoryFactory(name="Physics")
        child = ExperimentCategoryFactory(name="Particle Physics", parent=parent)
        grandchild = ExperimentCategoryFactory(name="Higgs", parent=child)

        descendants = list(parent.descendants())
        assert child in descendants
        assert grandchild in descendants

    def test_ancestors(self):
        parent = ExperimentCategoryFactory(name="Physics")
        child = ExperimentCategoryFactory(name="Particle Physics", parent=parent)

        ancestors = list(child.ancestors())
        assert parent in ancestors


@pytest.mark.django_db
class TestExperiment:
    def test_str(self):
        exp = ExperimentFactory(name="ATLAS")
        assert str(exp) == "ATLAS"

    def test_dirty_field_tracking(self):
        exp = ExperimentFactory(status=ExperimentStatus.DRAFT)
        exp.status = ExperimentStatus.ACTIVE
        assert exp.is_dirty()
        assert "status" in exp.get_dirty_fields()

    def test_status_changed_flag_on_save(self):
        exp = ExperimentFactory(status=ExperimentStatus.DRAFT)
        exp.status = ExperimentStatus.ACTIVE
        exp.save()
        assert exp._status_changed is True

    def test_status_unchanged_flag_on_save(self):
        exp = ExperimentFactory(status=ExperimentStatus.DRAFT)
        exp.name = "Updated Name"
        exp.save()
        assert exp._status_changed is False

    def test_default_stats(self):
        exp = ExperimentFactory()
        assert exp.total_events == 0
        assert exp.avg_energy_gev is None


@pytest.mark.django_db
class TestCollision:
    def test_str(self):
        event = CollisionFactory()
        assert "Collision" in str(event)

    def test_ordering(self):
        from django.utils import timezone

        exp = ExperimentFactory()
        e1 = CollisionFactory(experiment=exp, timestamp=timezone.now())
        e2 = CollisionFactory(experiment=exp, timestamp=timezone.now())

        from lab.models import Collision

        events = list(Collision.objects.filter(experiment=exp))
        assert events[0] == e2  # newest first
