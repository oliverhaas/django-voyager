import pytest
from django.core.management import call_command

from lab.models import Accelerator, Element, Experiment


@pytest.mark.django_db
class TestSeedCommand:
    def test_seed_elements(self):
        call_command("seed")
        assert Element.objects.count() >= 20

    def test_seed_full(self):
        call_command("seed", "--full")
        assert Element.objects.count() >= 20
        assert Accelerator.objects.count() >= 2
        assert Experiment.objects.count() >= 5

    def test_seed_idempotent(self):
        call_command("seed")
        count = Element.objects.count()
        call_command("seed")
        assert Element.objects.count() == count
