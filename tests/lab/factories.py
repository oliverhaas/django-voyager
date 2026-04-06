import io
from decimal import Decimal

import factory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image

from lab.models import (
    Accelerator,
    Collision,
    Element,
    EventImage,
    Experiment,
    ExperimentCategory,
    ExperimentStatus,
    ProcessingStatus,
)

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"researcher_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@cern.ch")


class ElementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Element

    atomic_number = factory.Sequence(lambda n: n + 1)
    symbol = factory.Sequence(lambda n: f"X{n}")
    name = factory.Sequence(lambda n: f"Element {n}")
    atomic_mass = factory.LazyFunction(lambda: Decimal("1.008"))
    category = "test element"


class AcceleratorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Accelerator

    name = factory.Sequence(lambda n: f"Accelerator {n}")
    location = "Geneva, Switzerland"
    max_energy_gev = Decimal("13000.000")
    is_active = True
    commissioned_date = factory.LazyFunction(lambda: timezone.now().date())
    webhook_url = ""


class ExperimentCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExperimentCategory

    name = factory.Sequence(lambda n: f"Category {n}")
    parent = None


class ExperimentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Experiment

    name = factory.Sequence(lambda n: f"Experiment {n}")
    description = "Test experiment"
    accelerator = factory.SubFactory(AcceleratorFactory)
    lead_researcher = factory.SubFactory(UserFactory)
    status = ExperimentStatus.DRAFT
    category = None
    started_at = None
    ended_at = None


class CollisionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collision

    experiment = factory.SubFactory(ExperimentFactory)
    timestamp = factory.LazyFunction(timezone.now)
    energy_gev = Decimal("125.300")
    luminosity = Decimal("34.500")
    particle_count = 42
    raw_data = factory.LazyFunction(lambda: {"detector": "CMS", "tracks": 12})


def make_test_image(width=100, height=100, color="red", fmt="PNG"):
    """Create an in-memory test image file."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return SimpleUploadedFile(f"test.{fmt.lower()}", buf.read(), content_type=f"image/{fmt.lower()}")


class EventImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventImage

    collision = factory.SubFactory(CollisionFactory)
    original_image = factory.LazyFunction(make_test_image)
    processing_status = ProcessingStatus.PENDING
