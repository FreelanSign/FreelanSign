# apps/catalog/tests/test_api_catalog.py
from urllib.parse import urlencode

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.catalog.models import Area, Prestation, PrestationStatus

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    u = User.objects.create_user(email="test@acme.io", password="pwd12345")
    return u


@pytest.fixture
def seed_catalog(db):
    a1 = Area.objects.create(name="Développement Web")
    a2 = Area.objects.create(name="UI/UX Design")

    p1 = Prestation.objects.create(
        area=a1,
        name="Site vitrine",
        description="Simple site",
        weight_days=5,
        default_rate_cents=250000,
        status=PrestationStatus.ACTIVE,
    )
    p2 = Prestation.objects.create(
        area=a1,
        name="Audit Django",
        description="Perf & sécurité",
        weight_days=2,
        default_rate_cents=120000,
        status=PrestationStatus.DRAFT,
    )
    p3 = Prestation.objects.create(
        area=a2,
        name="Maquettes 3 écrans",
        description="Figma",
        weight_days=3,
        default_rate_cents=150000,
        status=PrestationStatus.ACTIVE,
    )
    return {"areas": (a1, a2), "prestations": (p1, p2, p3)}


# ---------- Helpers resilient to router naming ----------
def _try_reverse(candidates):
    """
    Essaie plusieurs noms pour reverse() et retourne la première URL valide.
    """
    for name in candidates:
        try:
            return reverse(name)
        except Exception:
            continue
    return None


def get_areas_list_url():
    # candidats possibles en fonction du basename qu'on a utilisé dans le router
    candidates = [
        "catalog:catalog-areas-list",
        "catalog:catalog_areas-list",
        "catalog:areas-list",
        "catalog:areas-list",  # double entrée safe
    ]
    url = _try_reverse(candidates)
    if url:
        return url
    # fallback direct path (prefix possible: /api/)
    return "/api/catalog/areas/"


def get_prestations_list_url():
    candidates = [
        "catalog:catalog-prestations-list",
        "catalog:catalog_prestations-list",
        "catalog:prestations-list",
        "catalog:prestation-list",
    ]
    url = _try_reverse(candidates)
    if url:
        return url
    return "/api/catalog/prestations/"


def get_prestation_detail_url(pk):
    candidates = [
        "catalog:catalog-prestations-detail",
        "catalog:catalog_prestations-detail",
        "catalog:prestations-detail",
        "catalog:prestation-detail",
    ]
    for name in candidates:
        try:
            return reverse(name, args=[pk])
        except Exception:
            continue
    # fallback direct path
    return f"/api/catalog/prestations/{pk}/"


# ---------- tests ----------
def test_areas_requires_auth(api_client):
    url = get_areas_list_url()
    resp = api_client.get(url)
    assert resp.status_code in (401, 403)


def test_prestations_requires_auth(api_client):
    url = get_prestations_list_url()
    resp = api_client.get(url)
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_list_areas_search(api_client, user, seed_catalog):
    api_client.force_authenticate(user=user)
    base = get_areas_list_url()
    qs = urlencode({"search": "ui/ux"})
    url = f"{base}?{qs}"
    resp = api_client.get(url)
    assert resp.status_code == 200
    names = [x["name"] for x in resp.data["results"]]
    assert any("UI/UX" in n for n in names)


@pytest.mark.django_db
def test_list_prestations_filter_by_area_and_status(api_client, user, seed_catalog):
    api_client.force_authenticate(user=user)
    a1 = seed_catalog["areas"][0]
    base = get_prestations_list_url()
    qs = urlencode({"area": a1.id, "status": "ACTIVE"})
    url = f"{base}?{qs}"
    resp = api_client.get(url)
    assert resp.status_code == 200
    results = resp.data["results"]
    # On s'assure que les résultats sont bien des prestations (champs attendus)
    assert all("name" in r and "default_rate_cents" in r for r in results)
    # On vérifie qu'au moins la prestation 'Site vitrine' est présente
    assert any(r["name"] == "Site vitrine" for r in results)


@pytest.mark.django_db
def test_list_prestations_ordering(api_client, user, seed_catalog):
    api_client.force_authenticate(user=user)
    base = get_prestations_list_url()
    qs = urlencode({"ordering": "-default_rate_cents"})
    url = f"{base}?{qs}"
    resp = api_client.get(url)
    assert resp.status_code == 200
    values = [x["default_rate_cents"] for x in resp.data["results"]]
    assert values == sorted(values, reverse=True)


@pytest.mark.django_db
def test_retrieve_prestation(api_client, user, seed_catalog):
    api_client.force_authenticate(user=user)
    p = seed_catalog["prestations"][0]
    url = get_prestation_detail_url(p.id)
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data["id"] == p.id
    assert resp.data["area"] == p.area_id
    assert resp.data["area_name"] == p.area.name
