# apps/user/tests/test_professional_api.py
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_me_patch_creates_professional_user_if_missing():
    client = APIClient()
    user = User.objects.create_user(email="test@example.com", password="pass")
    client.force_authenticate(user=user)

    url = reverse("user:professional-me")
    payload = {"name": "Mon agence", "tjm_cents": 45000}
    resp = client.patch(url, payload, format="json")  # crée si manquant
    assert resp.status_code == 201, resp.data
    user.refresh_from_db()
    assert hasattr(user, "professional")
    assert user.professional.name == "Mon agence"
    assert user.professional.tjm_cents == 45000


@pytest.mark.django_db
def test_me_patch_updates_professional_if_exists():
    client = APIClient()
    user = User.objects.create_user(email="test2@example.com", password="pass")
    client.force_authenticate(user=user)

    url = reverse("user:professional-me")
    client.patch(url, {"name": "A", "tjm_cents": 1000}, format="json")  # create -> 201

    resp = client.patch(url, {"name": "B"}, format="json")  # update -> 200
    assert resp.status_code == 200, resp.data
    user.refresh_from_db()
    assert user.professional.name == "B"
