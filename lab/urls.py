from django.urls import path

from lab import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("experiments/", views.experiment_list, name="experiment_list"),
    path("experiments/new/", views.experiment_create, name="experiment_create"),
    path("experiments/<int:pk>/", views.experiment_detail, name="experiment_detail"),
    path("experiments/<int:pk>/edit/", views.experiment_edit, name="experiment_edit"),
    path("elements/", views.element_list, name="element_list"),
    path("accelerators/", views.accelerator_list, name="accelerator_list"),
]
