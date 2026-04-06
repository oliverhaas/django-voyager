from decimal import Decimal

import pytest
from django.test import Client
from django.utils import timezone

from lab.models import Collision, Experiment

from .factories import (
    AcceleratorFactory,
    CollisionFactory,
    ElementFactory,
    EventImageFactory,
    ExperimentCategoryFactory,
    ExperimentFactory,
    UserFactory,
)


@pytest.fixture
def client():
    return Client()


# ---------------------------------------------------------------------------
# Elements
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestElementsAPI:
    def test_list_elements(self, client):
        ElementFactory(atomic_number=1, symbol="H", name="Hydrogen")
        ElementFactory(atomic_number=2, symbol="He", name="Helium")

        response = client.get("/api/elements/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["symbol"] == "H"

    def test_list_elements_empty(self, client):
        response = client.get("/api/elements/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_element(self, client):
        ElementFactory(atomic_number=6, symbol="C", name="Carbon")
        response = client.get("/api/elements/6/")
        assert response.status_code == 200
        assert response.json()["symbol"] == "C"

    def test_get_element_not_found(self, client):
        response = client.get("/api/elements/999/")
        assert response.status_code == 404

    def test_create_element(self, client):
        payload = {
            "atomic_number": 79,
            "symbol": "Au",
            "name": "Gold",
            "atomic_mass": "196.966569",
            "category": "transition metal",
        }
        response = client.post("/api/elements/", data=payload, content_type="application/json")
        assert response.status_code == 201
        assert response.json()["symbol"] == "Au"

    def test_put_element(self, client):
        ElementFactory(atomic_number=3, symbol="Li", name="Lithium", atomic_mass="6.941", category="alkali metal")
        payload = {
            "atomic_number": 3,
            "symbol": "Li",
            "name": "Lithium",
            "atomic_mass": "6.941",
            "category": "alkali metal updated",
        }
        response = client.put("/api/elements/3/", data=payload, content_type="application/json")
        assert response.status_code == 200
        assert response.json()["category"] == "alkali metal updated"

    def test_patch_element(self, client):
        ElementFactory(atomic_number=7, symbol="N", name="Nitrogen", atomic_mass="14.007", category="nonmetal")
        response = client.patch(
            "/api/elements/7/",
            data={"category": "diatomic nonmetal"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["category"] == "diatomic nonmetal"

    def test_delete_element(self, client):
        ElementFactory(atomic_number=10, symbol="Ne", name="Neon")
        response = client.delete("/api/elements/10/")
        assert response.status_code == 204


# ---------------------------------------------------------------------------
# Accelerators
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAcceleratorsAPI:
    def test_list_accelerators(self, client):
        AcceleratorFactory()
        response = client.get("/api/accelerators/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_filter_by_is_active(self, client):
        AcceleratorFactory(is_active=True)
        AcceleratorFactory(is_active=False)
        response = client.get("/api/accelerators/?is_active=true")
        assert len(response.json()) == 1
        assert response.json()[0]["is_active"] is True

    def test_get_accelerator(self, client):
        acc = AcceleratorFactory(name="LHC")
        response = client.get(f"/api/accelerators/{acc.pk}/")
        assert response.status_code == 200
        assert response.json()["name"] == "LHC"

    def test_get_accelerator_not_found(self, client):
        response = client.get("/api/accelerators/9999/")
        assert response.status_code == 404

    def test_create_accelerator(self, client):
        payload = {
            "name": "Tevatron",
            "location": "Fermilab",
            "max_energy_gev": "1960.000",
            "is_active": False,
            "commissioned_date": "1983-10-13",
        }
        response = client.post("/api/accelerators/", data=payload, content_type="application/json")
        assert response.status_code == 201
        assert response.json()["name"] == "Tevatron"

    def test_patch_accelerator(self, client):
        acc = AcceleratorFactory(is_active=True)
        response = client.patch(
            f"/api/accelerators/{acc.pk}/",
            data={"is_active": False},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_delete_accelerator(self, client):
        acc = AcceleratorFactory()
        response = client.delete(f"/api/accelerators/{acc.pk}/")
        assert response.status_code == 204


# ---------------------------------------------------------------------------
# Experiment Categories
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCategoriesAPI:
    def test_list_categories(self, client):
        ExperimentCategoryFactory(name="High Energy")
        response = client.get("/api/categories/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_category(self, client):
        cat = ExperimentCategoryFactory(name="Nuclear")
        response = client.get(f"/api/categories/{cat.pk}/")
        assert response.status_code == 200
        assert response.json()["name"] == "Nuclear"

    def test_get_category_not_found(self, client):
        response = client.get("/api/categories/9999/")
        assert response.status_code == 404

    def test_create_category(self, client):
        payload = {"name": "Plasma Physics"}
        response = client.post("/api/categories/", data=payload, content_type="application/json")
        assert response.status_code == 201
        assert response.json()["name"] == "Plasma Physics"

    def test_patch_category(self, client):
        cat = ExperimentCategoryFactory(name="Old Name")
        response = client.patch(
            f"/api/categories/{cat.pk}/",
            data={"name": "New Name"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"

    def test_delete_category(self, client):
        cat = ExperimentCategoryFactory()
        response = client.delete(f"/api/categories/{cat.pk}/")
        assert response.status_code == 204


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestExperimentsAPI:
    def test_list_experiments(self, client):
        ExperimentFactory(name="ATLAS")
        response = client.get("/api/experiments/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "ATLAS"

    def test_filter_by_status(self, client):
        ExperimentFactory(status="draft")
        ExperimentFactory(status="active")
        response = client.get("/api/experiments/?status=active")
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "active"

    def test_get_experiment(self, client):
        exp = ExperimentFactory(name="CMS")
        response = client.get(f"/api/experiments/{exp.pk}/")
        assert response.status_code == 200
        assert response.json()["name"] == "CMS"

    def test_get_experiment_not_found(self, client):
        response = client.get("/api/experiments/9999/")
        assert response.status_code == 404

    def test_create_experiment(self, client):
        acc = AcceleratorFactory()
        user = UserFactory()
        payload = {
            "name": "ALICE",
            "description": "A Large Ion Collider Experiment",
            "accelerator_id": acc.pk,
            "lead_researcher_id": user.pk,
            "status": "draft",
        }
        response = client.post("/api/experiments/", data=payload, content_type="application/json")
        assert response.status_code == 201
        assert response.json()["name"] == "ALICE"
        assert Experiment.objects.filter(name="ALICE").exists()

    def test_put_experiment(self, client):
        exp = ExperimentFactory(name="Old Name", status="draft")
        payload = {
            "name": "New Name",
            "description": exp.description,
            "accelerator_id": exp.accelerator_id,
            "lead_researcher_id": exp.lead_researcher_id,
            "status": "active",
        }
        response = client.put(f"/api/experiments/{exp.pk}/", data=payload, content_type="application/json")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["status"] == "active"

    def test_patch_experiment(self, client):
        exp = ExperimentFactory(status="draft")
        response = client.patch(
            f"/api/experiments/{exp.pk}/",
            data={"status": "active"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["status"] == "active"

    def test_delete_experiment(self, client):
        exp = ExperimentFactory()
        response = client.delete(f"/api/experiments/{exp.pk}/")
        assert response.status_code == 204
        assert not Experiment.objects.filter(pk=exp.pk).exists()


# ---------------------------------------------------------------------------
# Collisions
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCollisionsAPI:
    def test_create_event(self, client):
        exp = ExperimentFactory()
        payload = {
            "experiment_id": exp.pk,
            "timestamp": timezone.now().isoformat(),
            "energy_gev": "125.300",
            "luminosity": "34.500",
            "particle_count": 42,
            "raw_data": {"detector": "CMS"},
        }
        response = client.post("/api/collisions/", data=payload, content_type="application/json")
        assert response.status_code == 201
        assert Collision.objects.count() == 1

    def test_list_events(self, client):
        CollisionFactory()
        response = client.get("/api/collisions/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_filter_events_by_experiment(self, client):
        e1 = CollisionFactory()
        CollisionFactory()
        response = client.get(f"/api/collisions/?experiment_id={e1.experiment_id}")
        data = response.json()
        assert len(data) == 1
        assert data[0]["experiment_id"] == e1.experiment_id

    def test_filter_events_by_energy_range(self, client):
        CollisionFactory(energy_gev=Decimal("100.000"))
        CollisionFactory(energy_gev=Decimal("200.000"))
        response = client.get("/api/collisions/?min_energy=150&max_energy=250")
        data = response.json()
        assert len(data) == 1

    def test_get_collision(self, client):
        col = CollisionFactory()
        response = client.get(f"/api/collisions/{col.pk}/")
        assert response.status_code == 200
        assert response.json()["id"] == col.pk

    def test_get_collision_not_found(self, client):
        response = client.get("/api/collisions/9999/")
        assert response.status_code == 404

    def test_patch_collision(self, client):
        col = CollisionFactory(particle_count=10)
        response = client.patch(
            f"/api/collisions/{col.pk}/",
            data={"particle_count": 99},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["particle_count"] == 99

    def test_delete_collision(self, client):
        col = CollisionFactory()
        response = client.delete(f"/api/collisions/{col.pk}/")
        assert response.status_code == 204
        assert not Collision.objects.filter(pk=col.pk).exists()

    def test_batch_create_collisions(self, client):
        exp = ExperimentFactory()
        ts = timezone.now().isoformat()
        payload = {
            "items": [
                {
                    "experiment_id": exp.pk,
                    "timestamp": ts,
                    "energy_gev": "100.000",
                    "luminosity": "10.000",
                    "particle_count": 5,
                    "raw_data": {},
                },
                {
                    "experiment_id": exp.pk,
                    "timestamp": ts,
                    "energy_gev": "200.000",
                    "luminosity": "20.000",
                    "particle_count": 10,
                    "raw_data": {},
                },
            ],
        }
        response = client.post("/api/collisions/batch/", data=payload, content_type="application/json")
        assert response.status_code == 201
        data = response.json()
        assert data["created"] == 2
        assert len(data["items"]) == 2
        assert Collision.objects.filter(experiment=exp).count() == 2

    def test_batch_create_updates_experiment_stats(self, client):
        exp = ExperimentFactory()
        ts = timezone.now().isoformat()
        payload = {
            "items": [
                {
                    "experiment_id": exp.pk,
                    "timestamp": ts,
                    "energy_gev": "100.000",
                    "luminosity": "10.000",
                    "particle_count": 1,
                    "raw_data": {},
                },
                {
                    "experiment_id": exp.pk,
                    "timestamp": ts,
                    "energy_gev": "200.000",
                    "luminosity": "20.000",
                    "particle_count": 2,
                    "raw_data": {},
                },
            ],
        }
        client.post("/api/collisions/batch/", data=payload, content_type="application/json")
        exp.refresh_from_db()
        assert exp.total_events == 2


# ---------------------------------------------------------------------------
# Event Images
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestImagesAPI:
    def test_list_images(self, client):
        EventImageFactory()
        response = client.get("/api/images/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_filter_images_by_collision(self, client):
        img = EventImageFactory()
        EventImageFactory()
        response = client.get(f"/api/images/?collision_id={img.collision_id}")
        assert len(response.json()) == 1

    def test_get_image(self, client):
        img = EventImageFactory()
        response = client.get(f"/api/images/{img.pk}/")
        assert response.status_code == 200
        assert response.json()["id"] == img.pk

    def test_get_image_not_found(self, client):
        response = client.get("/api/images/9999/")
        assert response.status_code == 404

    def test_patch_image_status(self, client):
        img = EventImageFactory(processing_status="pending")
        response = client.patch(
            f"/api/images/{img.pk}/",
            data={"processing_status": "completed"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["processing_status"] == "completed"

    def test_delete_image(self, client):
        img = EventImageFactory()
        response = client.delete(f"/api/images/{img.pk}/")
        assert response.status_code == 204
