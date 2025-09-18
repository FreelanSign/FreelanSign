# apps/user/tests/test_professional_api.py
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_onboarding_creates_professional_user():
    client = APIClient()
    user = User.objects.create_user(email="test@example.com", password="pass")
    client.force_authenticate(user=user)

    url = reverse("onboarding-professional")
    payload = {"name": "Mon agence", "tjm_cents": 45000}
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 201
    # objet lié
    assert hasattr(user, "professional")
    assert user.professional.name == "Mon agence"
    assert user.professional.tjm_cents == 45000


@pytest.mark.django_db
def test_me_patch_updates_professional():
    client = APIClient()
    user = User.objects.create_user(email="test2@example.com", password="pass")
    client.force_authenticate(user=user)
    # create first
    client.post(reverse("onboarding-professional"), {"name": "A", "tjm_cents": 1000}, format="json")

    resp = client.patch(reverse("professional-me"), {"name": "B"}, format="json")
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.professional.name == "B"
