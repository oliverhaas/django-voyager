"""
Custom makemigrations command that chains django-pgtrigger and django-syzygy.

Both packages patch Django's MigrationAutodetector:
- pgtrigger patches it via AppConfig.ready() by inserting MigrationAutodetectorMixin
- syzygy replaces it in its makemigrations Command.handle() with a styled subclass

On Django >= 5.2, both use Command.autodetector rather than the module-level class.
syzygy's handle() only wraps its own MigrationAutodetector, losing pgtrigger's mixin.

This command ensures the styled autodetector inherits from both.
"""

from __future__ import annotations

from typing import Any

from django.core.management.commands.makemigrations import Command as DjangoCommand
from syzygy.autodetector import MigrationAutodetector as SyzygyMigrationAutodetector
from syzygy.management.commands.makemigrations import Command as SyzygyCommand


class Command(SyzygyCommand):
    def handle(self, *args: Any, disable_syzygy: bool = False, **options: Any) -> None:
        if disable_syzygy:
            super().handle(*args, disable_syzygy=disable_syzygy, **options)
            return

        # self.autodetector has already been patched by pgtrigger (via AppConfig.ready)
        # to include MigrationAutodetectorMixin. Build a combined autodetector that
        # inherits from both syzygy's autodetector and the pgtrigger-patched one so
        # neither package's migration detection is dropped.
        pgtrigger_patched = self.autodetector
        style = self.style

        class StyledMigrationAutodetector(SyzygyMigrationAutodetector, pgtrigger_patched):  # type: ignore[misc]
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs, style=style)

        self.autodetector = StyledMigrationAutodetector
        try:
            # Call grandparent (Django's makemigrations.Command) directly so we
            # don't let syzygy re-patch autodetector and overwrite our combined one.
            DjangoCommand.handle(self, *args, **options)
        finally:
            self.autodetector = pgtrigger_patched
