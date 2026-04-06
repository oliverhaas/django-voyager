from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from lab.forms import ExperimentForm
from lab.models import Accelerator, CollisionEvent, Element, Experiment

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


@require_GET
def dashboard(request: HttpRequest) -> HttpResponse:
    """Landing page with overview stats."""
    context = {
        "experiment_count": Experiment.objects.count(),
        "active_experiments": Experiment.objects.filter(status="active").count(),
        "element_count": Element.objects.count(),
        "accelerator_count": Accelerator.objects.count(),
        "event_count": CollisionEvent.objects.count(),
        "recent_experiments": Experiment.objects.select_related("accelerator", "lead_researcher").order_by(
            "-created_at",
        )[:5],
    }
    return render(request, "lab/dashboard.html", context)


@require_GET
def experiment_list(request: HttpRequest) -> HttpResponse:
    """List all experiments with optional status filter."""
    status = request.GET.get("status")
    qs = Experiment.objects.select_related("accelerator", "lead_researcher").order_by("-created_at")
    if status:
        qs = qs.filter(status=status)
    context = {
        "experiments": qs,
        "current_status": status,
        "status_choices": Experiment._meta.get_field("status").choices,
    }
    return render(request, "lab/experiment_list.html", context)


@require_GET
def experiment_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Detail page for a single experiment."""
    experiment = get_object_or_404(
        Experiment.objects.select_related("accelerator", "lead_researcher", "category"),
        pk=pk,
    )
    recent_events = experiment.collision_events.order_by("-timestamp")[:20]
    context = {
        "experiment": experiment,
        "recent_events": recent_events,
    }
    return render(request, "lab/experiment_detail.html", context)


@require_http_methods(["GET", "POST"])
def experiment_create(request: HttpRequest) -> HttpResponse:
    """Create a new experiment."""
    if request.method == "POST":
        form = ExperimentForm(request.POST)
        if form.is_valid():
            experiment = form.save(commit=False)
            experiment.lead_researcher = request.user
            experiment.save()
            return redirect("experiment_detail", pk=experiment.pk)
    else:
        form = ExperimentForm()
    return render(request, "lab/experiment_form.html", {"form": form, "title": "New Experiment"})


@require_http_methods(["GET", "POST"])
def experiment_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """Edit an existing experiment."""
    experiment = get_object_or_404(Experiment, pk=pk)
    if request.method == "POST":
        form = ExperimentForm(request.POST, instance=experiment)
        if form.is_valid():
            form.save()
            return redirect("experiment_detail", pk=experiment.pk)
    else:
        form = ExperimentForm(instance=experiment)
    return render(request, "lab/experiment_form.html", {"form": form, "title": "Edit Experiment"})


@require_GET
def element_list(request: HttpRequest) -> HttpResponse:
    """List periodic table elements."""
    category = request.GET.get("category")
    qs = Element.objects.all()
    if category:
        qs = qs.filter(category=category)
    categories = Element.objects.values_list("category", flat=True).distinct().order_by("category")
    context = {
        "elements": qs,
        "categories": categories,
        "current_category": category,
    }
    return render(request, "lab/element_list.html", context)


@require_GET
def accelerator_list(request: HttpRequest) -> HttpResponse:
    """List particle accelerators."""
    from django.db.models import Count

    accelerators = Accelerator.objects.annotate(experiment_count=Count("experiments")).order_by("name")
    return render(request, "lab/accelerator_list.html", {"accelerators": accelerators})
