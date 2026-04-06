from typing import Any

from django.templatetags.static import static
from django.urls import reverse
from django_vite.templatetags.django_vite import vite_asset, vite_hmr_client
from jinja2 import Environment


def environment(**options: Any) -> Environment:
    env = Environment(**options)  # noqa: S701 - autoescape is set by Django's Jinja2 backend
    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "vite_asset": vite_asset,
            "vite_hmr_client": vite_hmr_client,
        },
    )
    return env
