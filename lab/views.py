from __future__ import annotations

from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from django.db.models import Count
from django.shortcuts import aget_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from lab.forms import ExperimentForm
from lab.models import Accelerator, Collision, Element, Experiment

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

_render = sync_to_async(render)


@require_GET
async def dashboard(request: HttpRequest) -> HttpResponse:
    """Landing page with overview stats."""
    context = {
        "experiment_count": await Experiment.objects.acount(),
        "active_experiments": await Experiment.objects.filter(status="active").acount(),
        "element_count": await Element.objects.acount(),
        "accelerator_count": await Accelerator.objects.acount(),
        "event_count": await Collision.objects.acount(),
        "recent_experiments": [
            exp
            async for exp in Experiment.objects.select_related("accelerator", "lead_researcher").order_by(
                "-created_at",
            )[:5]
        ],
    }
    return await _render(request, "lab/dashboard.html", context)


@require_GET
async def experiment_list(request: HttpRequest) -> HttpResponse:
    """List all experiments with optional status filter."""
    status = request.GET.get("status")
    qs = Experiment.objects.select_related("accelerator", "lead_researcher").order_by("-created_at")
    if status:
        qs = qs.filter(status=status)
    context = {
        "experiments": [exp async for exp in qs],
        "current_status": status,
        "status_choices": Experiment._meta.get_field("status").choices,
    }
    return await _render(request, "lab/experiment_list.html", context)


@require_GET
async def experiment_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Detail page for a single experiment."""
    experiment = await aget_object_or_404(
        Experiment.objects.select_related("accelerator", "lead_researcher", "category"),
        pk=pk,
    )
    recent_events = [event async for event in experiment.collisions.order_by("-timestamp")[:20]]
    context = {
        "experiment": experiment,
        "recent_events": recent_events,
    }
    return await _render(request, "lab/experiment_detail.html", context)


@require_http_methods(["GET", "POST"])
async def experiment_create(request: HttpRequest) -> HttpResponse:
    """Create a new experiment."""
    if request.method == "POST":
        form = ExperimentForm(request.POST)
        if await sync_to_async(form.is_valid)():
            experiment = await sync_to_async(form.save)(commit=False)
            experiment.lead_researcher = await request.auser()
            await experiment.asave()
            return redirect("experiment_detail", pk=experiment.pk)
    else:
        form = ExperimentForm()
    return await _render(request, "lab/experiment_form.html", {"form": form, "title": "New Experiment"})


@require_http_methods(["GET", "POST"])
async def experiment_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """Edit an existing experiment."""
    experiment = await aget_object_or_404(Experiment, pk=pk)
    if request.method == "POST":
        form = ExperimentForm(request.POST, instance=experiment)
        if await sync_to_async(form.is_valid)():
            await sync_to_async(form.save)()
            return redirect("experiment_detail", pk=experiment.pk)
    else:
        form = ExperimentForm(instance=experiment)
    return await _render(request, "lab/experiment_form.html", {"form": form, "title": "Edit Experiment"})


@require_GET
async def element_list(request: HttpRequest) -> HttpResponse:
    """List periodic table elements."""
    category = request.GET.get("category")
    qs = Element.objects.all()
    if category:
        qs = qs.filter(category=category)
    categories = [
        cat async for cat in Element.objects.values_list("category", flat=True).distinct().order_by("category")
    ]
    context = {
        "elements": [el async for el in qs],
        "categories": categories,
        "current_category": category,
    }
    return await _render(request, "lab/element_list.html", context)


@require_GET
async def accelerator_list(request: HttpRequest) -> HttpResponse:
    """List particle accelerators."""
    accelerators = [
        acc async for acc in Accelerator.objects.annotate(experiment_count=Count("experiments")).order_by("name")
    ]
    return await _render(request, "lab/accelerator_list.html", {"accelerators": accelerators})
