# apps/quote/tests/test_models.py
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.quote.models import PaymentTerms, Quote, QuoteLineItem

User = get_user_model()


@pytest.mark.django_db
def test_reference_unique_per_owner(client_model):
    """Ensure (owner, reference) uniqueness is enforced."""
    owner = User.objects.create_user(email="a@x.io", password="x")
    c = client_model.objects.create(owner=owner, name="ACME")  # adapte à ton Client

    q1 = Quote.objects.create(
        owner=owner,
        client=c,
        title="Q1",
        reference="REF-001",
        currency="EUR",
        language="fr",
        status=Quote.Status.DRAFT,
        issue_date=timezone.now().date(),
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    with pytest.raises(Exception):
        Quote.objects.create(
            owner=owner,
            client=c,
            title="Q2",
            reference="REF-001",
            currency="EUR",
            language="fr",
            status=Quote.Status.DRAFT,
            issue_date=timezone.now().date(),
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
        )


@pytest.mark.django_db
def test_totals_verification(client_model):
    """Protect decimals and arithmetic: subtotal + tax_total - discount_total == total."""
    owner = User.objects.create_user(email="b@x.io", password="x")
    c = client_model.objects.create(owner=owner, name="Client B")

    q = Quote.objects.create(
        owner=owner,
        client=c,
        title="Q",
        reference="REF-100",
        currency="EUR",
        language="fr",
        status=Quote.Status.DRAFT,
        issue_date=timezone.now().date(),
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    # 2 lignes
    QuoteLineItem.objects.create(
        quote=q,
        description="Dev",
        qty=Decimal("10"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        discount=Decimal("50.00"),
        order=1,
        line_total=Decimal("0.00"),
    )
    QuoteLineItem.objects.create(
        quote=q,
        description="Design",
        qty=Decimal("5"),
        unit_price=Decimal("80.00"),
        tax_rate=Decimal("10.00"),
        discount=Decimal("0.00"),
        order=2,
        line_total=Decimal("0.00"),
    )

    # Recalcule logiquement (ici on simule une logique d'update des montants)
    subtotal = q.compute_subtotal()  # (10*100-50) + (5*80-0) = 950 + 400 = 1350.00
    tax_total = q.compute_tax_total()  # 950*0.20 + 400*0.10 = 190 + 40 = 230.00
    discount_total = Decimal("100.00")  # remise globale supplémentaire
    total = subtotal + tax_total - discount_total

    # Stocke, puis vérifie la contrainte
    q.subtotal = subtotal
    q.tax_total = tax_total
    q.discount_total = discount_total
    q.total = total
    q.save()

    assert q.totals_match() is True
