from decimal import Decimal

import pytest
from django.test import Client
from django.utils import timezone

from lab.models import Collision

from .factories import CollisionFactory, ElementFactory, ExperimentFactory


@pytest.fixture
def client():
    return Client()


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
