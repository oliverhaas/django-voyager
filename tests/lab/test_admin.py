import pytest
from django.test import Client
from django.urls import reverse

from .factories import (
    AcceleratorFactory,
    ElementFactory,
    ExperimentFactory,
    UserFactory,
)


@pytest.fixture
def admin_client():
    user = UserFactory(is_staff=True, is_superuser=True)
    client = Client()
    client.force_login(user)
    return client


@pytest.mark.django_db
class TestElementAdmin:
    def test_changelist_loads(self, admin_client):
        ElementFactory()
        url = reverse("admin:lab_element_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_import_export_buttons_present(self, admin_client):
        url = reverse("admin:lab_element_changelist")
        response = admin_client.get(url)
        content = response.content.decode()
        assert "import" in content.lower() or "Import" in content


@pytest.mark.django_db
class TestAcceleratorAdmin:
    def test_changelist_loads(self, admin_client):
        AcceleratorFactory()
        url = reverse("admin:lab_accelerator_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestExperimentAdmin:
    def test_changelist_loads(self, admin_client):
        ExperimentFactory()
        url = reverse("admin:lab_experiment_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestCollisionEventAdmin:
    def test_changelist_loads(self, admin_client):
        url = reverse("admin:lab_collisionevent_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_no_add_permission(self, admin_client):
        url = reverse("admin:lab_collisionevent_add")
        response = admin_client.get(url)
        assert response.status_code == 403
