import pytest
from django.test import Client

from .factories import (
    AcceleratorFactory,
    CollisionFactory,
    ElementFactory,
    ExperimentFactory,
    UserFactory,
)


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def auth_client():
    user = UserFactory()
    client = Client()
    client.force_login(user)
    return client


@pytest.mark.django_db
class TestDashboard:
    def test_loads(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Dashboard" in response.content

    def test_shows_stats(self, client):
        ExperimentFactory()
        ElementFactory()
        response = client.get("/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestExperimentList:
    def test_loads(self, client):
        response = client.get("/experiments/")
        assert response.status_code == 200

    def test_shows_experiments(self, client):
        ExperimentFactory(name="ATLAS")
        response = client.get("/experiments/")
        assert b"ATLAS" in response.content

    def test_filters_by_status(self, client):
        ExperimentFactory(name="Active One", status="active")
        ExperimentFactory(name="Draft One", status="draft")
        response = client.get("/experiments/?status=active")
        assert b"Active One" in response.content
        assert b"Draft One" not in response.content


@pytest.mark.django_db
class TestExperimentDetail:
    def test_loads(self, client):
        exp = ExperimentFactory(name="CMS")
        response = client.get(f"/experiments/{exp.pk}/")
        assert response.status_code == 200
        assert b"CMS" in response.content

    def test_shows_events(self, client):
        exp = ExperimentFactory()
        CollisionFactory(experiment=exp)
        response = client.get(f"/experiments/{exp.pk}/")
        assert response.status_code == 200

    def test_404_for_missing(self, client):
        response = client.get("/experiments/99999/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestExperimentCreate:
    def test_form_loads(self, auth_client):
        response = auth_client.get("/experiments/new/")
        assert response.status_code == 200
        assert b"New Experiment" in response.content

    def test_creates_experiment(self, auth_client):
        acc = AcceleratorFactory()
        response = auth_client.post(
            "/experiments/new/",
            {"name": "Test Exp", "accelerator": acc.pk, "status": "draft", "description": ""},
        )
        assert response.status_code == 302  # redirect on success


@pytest.mark.django_db
class TestExperimentEdit:
    def test_form_loads(self, auth_client):
        exp = ExperimentFactory()
        response = auth_client.get(f"/experiments/{exp.pk}/edit/")
        assert response.status_code == 200
        assert b"Edit Experiment" in response.content


@pytest.mark.django_db
class TestElementList:
    def test_loads(self, client):
        response = client.get("/elements/")
        assert response.status_code == 200

    def test_shows_elements(self, client):
        ElementFactory(symbol="H", name="Hydrogen")
        response = client.get("/elements/")
        assert b"Hydrogen" in response.content

    def test_filters_by_category(self, client):
        ElementFactory(symbol="H", name="Hydrogen", category="nonmetal")
        ElementFactory(symbol="He", name="Helium", category="noble gas")
        response = client.get("/elements/?category=nonmetal")
        assert b"Hydrogen" in response.content
        assert b"Helium" not in response.content


@pytest.mark.django_db
class TestAcceleratorList:
    def test_loads(self, client):
        response = client.get("/accelerators/")
        assert response.status_code == 200

    def test_shows_accelerators(self, client):
        AcceleratorFactory(name="LHC")
        response = client.get("/accelerators/")
        assert b"LHC" in response.content
