from django.contrib import admin
from django.urls import include, path
from ninja import NinjaAPI
from ninja.openapi.docs import Swagger

from lab.api import router as lab_router

api = NinjaAPI(
    title="Voyager API",
    version="1.0.0",
    docs=Swagger(settings={"docExpansion": "list"}),
)
api.add_router("/", lab_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("lab.urls")),
]
