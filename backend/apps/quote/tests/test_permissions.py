# apps/quote/tests/test_permissions.py
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.client.models import Client
from apps.quote.models import Quote

User = get_user_model()


@pytest.mark.django_db
def test_other_professional_cannot_view_or_edit_quote():
    # create users
    owner = User.objects.create_user(email="owner@example.com", password="pwd")
    other = User.objects.create_user(email="other@example.com", password="pwd")
    # create client owned by 'owner' (owner is required by Client model)
    client = Client.objects.create(owner=owner, name="Acme Corp")
    # create a quote owned by 'owner'
    q = Quote.objects.create(
        owner=owner,
        client=client,
        title="Owner's quote",
        reference="REF-OWN-1",
        currency="EUR",
        language="fr",
        status=Quote.Status.DRAFT,
        issue_date=date.today(),
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    api = APIClient()
    api.force_authenticate(user=other)

    # retrieve should be 404 because the queryset filters owner-only
    resp = api.get(f"/api/quotes/{q.pk}/")
    assert resp.status_code == 404

    # update (PUT) should also not find (404 or 403)
    resp = api.put(f"/api/quotes/{q.pk}/", data={"title": "hacked"})
    assert resp.status_code in (404, 400, 403)

    # send action should be inaccessible (404)
    resp = api.post(f"/api/quotes/{q.pk}/send/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_admin_can_read_and_cancel_with_all_param():
    owner = User.objects.create_user(email="owner2@example.com", password="pwd")
    admin = User.objects.create_user(email="admin@example.com", password="pwd", is_staff=True)
    # client must have an owner as per Client model constraints
    client = Client.objects.create(owner=owner, name="Acme Corp 2")
    q = Quote.objects.create(
        owner=owner,
        client=client,
        title="Owner's quote 2",
        reference="REF-OWN-2",
        currency="EUR",
        language="fr",
        status=Quote.Status.DRAFT,
        issue_date=date.today(),
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    api = APIClient()
    api.force_authenticate(user=admin)

    # Admin must include ?all=true to see other owners' quotes with current config
    resp = api.get(f"/api/quotes/{q.pk}/?all=true")
    assert resp.status_code == 200

    # Admin can delete (which maps to a CANCELLED partial-delete in perform_destroy)
    resp = api.delete(f"/api/quotes/{q.pk}/?all=true")
    assert resp.status_code == 204

    # refresh and check status changed to CANCELLED
    q.refresh_from_db()
    assert q.status == Quote.Status.CANCELLED
