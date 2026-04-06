from __future__ import annotations

from django.apps import AppConfig


class MockConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mock"
    verbose_name = "Mock Data Generator"
