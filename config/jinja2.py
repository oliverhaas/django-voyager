from pathlib import Path
from typing import Any

from django.templatetags.static import static
from django.urls import reverse
from django_vite.templatetags.django_vite import vite_asset, vite_hmr_client
from jinja2 import Environment
from jinjax import Catalog

BASE_DIR = Path(__file__).resolve().parent.parent


def _make_catalog(env: Environment) -> Catalog:
    """Create a fresh JinjaX catalog bound to the given environment."""
    cat = Catalog(jinja_env=env)
    cat.add_folder(BASE_DIR / "components")
    return cat


def environment(**options: Any) -> Environment:
    # Add JinjaX extension
    extensions = list(options.pop("extensions", []))
    extensions.append("jinjax.JinjaX")
    options["extensions"] = extensions

    env = Environment(**options)  # noqa: S701 - autoescape is set by Django's Jinja2 backend

    # Create catalog bound to this specific environment instance
    catalog = _make_catalog(env)

    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "catalog": catalog,
            "vite_asset": vite_asset,
            "vite_hmr_client": vite_hmr_client,
        },
    )

    return env
