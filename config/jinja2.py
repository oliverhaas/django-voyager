from typing import Any

from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment


def environment(**options: Any) -> Environment:
    env = Environment(autoescape=True, **options)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
        },
    )
    return env
