from __future__ import annotations

from typing import Any, ClassVar

import pghistory
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.db import models
from tree_queries.models import TreeNode

User = settings.AUTH_USER_MODEL


class Element(models.Model):
    atomic_number = models.PositiveSmallIntegerField(primary_key=True)
    symbol = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50, unique=True)
    atomic_mass = models.DecimalField(max_digits=12, decimal_places=6)
    category = models.CharField(max_length=50)

    class Meta:
        ordering: ClassVar = ["atomic_number"]

    def __str__(self) -> str:
        return f"{self.symbol} ({self.name})"


class Accelerator(models.Model):
    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=200)
    max_energy_gev = models.DecimalField(max_digits=12, decimal_places=3)
    is_active = models.BooleanField(default=True)
    commissioned_date = models.DateField()
    webhook_url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.name


class ExperimentCategory(TreeNode):
    name: models.CharField[str, str] = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "experiment categories"

    def __str__(self) -> str:
        return self.name


class ExperimentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    ARCHIVED = "archived", "Archived"


@pghistory.track(
    pghistory.InsertEvent("experiment.insert"),
    pghistory.UpdateEvent("experiment.status_change"),
    fields=["status"],
)
class Experiment(DirtyFieldsMixin, models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    accelerator = models.ForeignKey(Accelerator, on_delete=models.CASCADE, related_name="experiments")
    lead_researcher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="experiments")
    status = models.CharField(max_length=20, choices=ExperimentStatus.choices, default=ExperimentStatus.DRAFT)
    category = models.ForeignKey(ExperimentCategory, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    total_events = models.PositiveIntegerField(default=0)
    avg_energy_gev = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.is_dirty() and "status" in self.get_dirty_fields():
            self._status_changed = True
        else:
            self._status_changed = False
        super().save(*args, **kwargs)


class Collision(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="collisions")
    timestamp = models.DateTimeField()
    energy_gev = models.DecimalField(max_digits=12, decimal_places=3)
    luminosity = models.DecimalField(max_digits=12, decimal_places=3)
    particle_count = models.PositiveIntegerField()
    raw_data = models.JSONField(default=dict)

    class Meta:
        ordering: ClassVar = ["-timestamp"]

    def __str__(self) -> str:
        return f"Collision {self.pk} @ {self.timestamp}"


class ProcessingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class EventImage(models.Model):
    collision = models.ForeignKey(Collision, on_delete=models.CASCADE, related_name="images")
    original_image = models.ImageField(upload_to="event_images/originals/")
    thumbnail = models.ImageField(upload_to="event_images/thumbnails/", blank=True)
    processed_image = models.ImageField(upload_to="event_images/processed/", blank=True)
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Image {self.pk} for Collision {self.collision_id}"


class OrgType(models.TextChoices):
    LABORATORY = "laboratory", "Laboratory"
    UNIVERSITY = "university", "University"
    INSTITUTE = "institute", "Institute"
    CONSORTIUM = "consortium", "Consortium"
    OTHER = "other", "Other"


class Organization(models.Model):
    name = models.CharField(max_length=200, unique=True)
    abbreviation = models.CharField(max_length=20, unique=True, blank=True)
    location = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    org_type = models.CharField(max_length=20, choices=OrgType.choices)
    members = models.ManyToManyField(User, related_name="organizations", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.abbreviation or self.name


class Conference(models.Model):
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    organizer = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="conferences"
    )
    experiments = models.ManyToManyField(Experiment, related_name="conferences", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-start_date"]

    def __str__(self) -> str:
        return self.abbreviation or self.name
