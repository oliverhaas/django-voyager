from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

if TYPE_CHECKING:
    from django.http import HttpRequest

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


@admin.register(Element)
class ElementAdmin(ImportExportModelAdmin):
    list_display = ["atomic_number", "symbol", "name", "atomic_mass", "category"]
    list_filter = ["category"]
    search_fields = ["symbol", "name"]
    ordering = ["atomic_number"]


@admin.register(Accelerator)
class AcceleratorAdmin(admin.ModelAdmin):
    list_display = ["name", "location", "max_energy_gev", "is_active", "commissioned_date"]
    list_filter = ["is_active"]
    search_fields = ["name", "location"]


@admin.register(ExperimentCategory)
class ExperimentCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent"]
    search_fields = ["name"]


class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 0
    readonly_fields = ["thumbnail", "processed_image", "processing_status", "created_at"]


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ["name", "accelerator", "lead_researcher", "status", "total_events", "created_at"]
    list_filter = ["status", "accelerator"]
    search_fields = ["name", "description"]
    readonly_fields = ["total_events", "avg_energy_gev", "created_at", "updated_at"]


@admin.register(Collision)
class CollisionAdmin(admin.ModelAdmin):
    list_display = ["pk", "experiment", "timestamp", "energy_gev", "particle_count"]
    list_filter = ["experiment"]
    readonly_fields = [
        "experiment",
        "timestamp",
        "energy_gev",
        "luminosity",
        "particle_count",
        "raw_data",
    ]
    inlines = [EventImageInline]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Collision | None = None) -> bool:
        return False


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "abbreviation", "org_type", "location", "created_at"]
    list_filter = ["org_type"]
    search_fields = ["name", "abbreviation", "location"]
    filter_horizontal = ["members"]


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ["name", "abbreviation", "location", "start_date", "end_date", "organizer"]
    list_filter = ["organizer"]
    search_fields = ["name", "abbreviation", "location"]
    filter_horizontal = ["experiments"]
