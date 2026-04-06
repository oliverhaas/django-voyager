from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import smart_str
from waffle.utils import get_setting

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


class AsyncWaffleMiddleware(MiddlewareMixin):
    """Async-compatible replacement for waffle.middleware.WaffleMiddleware.

    The original only overrides process_response to set waffle cookies on the
    response based on request.waffles / request.waffle_tests attributes that
    waffle populates during view execution. No DB access happens here.

    Using MiddlewareMixin gives us both sync and async support automatically:
    in async mode, __acall__ wraps process_response in sync_to_async.
    """

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        secure = get_setting("SECURE")
        max_age = get_setting("MAX_AGE")

        if hasattr(request, "waffles"):
            for k in request.waffles:
                name = smart_str(get_setting("COOKIE") % k)
                active, rollout = request.waffles[k]
                if rollout and not active:
                    # "Inactive" is a session cookie during rollout mode.
                    age = None
                else:
                    age = max_age
                response.set_cookie(name, value=active, max_age=age, secure=secure)

        if hasattr(request, "waffle_tests"):
            for k in request.waffle_tests:
                name = smart_str(get_setting("TEST_COOKIE") % k)
                value = request.waffle_tests[k]
                response.set_cookie(name, value=value)

        return response
