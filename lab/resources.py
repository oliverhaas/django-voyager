"""django-import-export resources for all lab models."""

from import_export.resources import ModelResource

from lab.models import (
    Accelerator,
    Collision,
    Conference,
    Element,
    EventImage,
    Experiment,
    ExperimentCategory,
    Organization,
)


class ElementResource(ModelResource):
    class Meta:
        model = Element


class AcceleratorResource(ModelResource):
    class Meta:
        model = Accelerator


class ExperimentCategoryResource(ModelResource):
    class Meta:
        model = ExperimentCategory


class ExperimentResource(ModelResource):
    class Meta:
        model = Experiment


class CollisionResource(ModelResource):
    class Meta:
        model = Collision


class EventImageResource(ModelResource):
    class Meta:
        model = EventImage


class OrganizationResource(ModelResource):
    class Meta:
        model = Organization


class ConferenceResource(ModelResource):
    class Meta:
        model = Conference
