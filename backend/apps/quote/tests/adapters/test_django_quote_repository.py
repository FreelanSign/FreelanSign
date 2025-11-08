from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.client.models import Client
from apps.quote.adapters.persistence.django_quote_repository import DjangoQuoteRepository
from apps.quote.models import Quote

User = get_user_model()


@pytest.mark.django_db
def test_replace_lines_recalculates_totals():
    user = User.objects.create_user(email="repo1@example.test", password="x")
    client = Client.objects.create(owner=user, name="ACME")

    # Création d'un devis "brut" (ici on ne teste pas la génération de référence)
    q = Quote.objects.create(
        id=None,
        owner=user,
        client=client,
        title="Test Repo Replace",
        reference="Q-2025-11-9999",
        currency="EUR",
        language="fr",
        status=Quote.Status.DRAFT,
        issue_date=timezone.localdate(),
        valid_until=None,
        payment_terms=None,
        payment_terms_text="",
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
        note="",
    )

    repo = DjangoQuoteRepository()
    items = [
        {
            "description": "Ligne A",
            "qty": Decimal("2"),
            "unit_price": Decimal("100.00"),
            "tax_rate_pct": Decimal("20.00"),
            "discount": Decimal("10.00"),
            "metadata": {"sku": "A"},
        },
        {
            "description": "Ligne B",
            "qty": Decimal("1.5"),
            "unit_price": Decimal("200.00"),
            "tax_rate_pct": Decimal("10.00"),
            "discount": Decimal("0.00"),
            "metadata": {"sku": "B"},
        },
    ]

    repo.replace_lines(q, items)

    q.refresh_from_db()
    lines = list(q.items.order_by("order"))

    assert len(lines) == 2
    assert lines[0].order == 0 and lines[1].order == 1

    # Pré-tax:
    # A: (2 * 100) - 10 = 190.00
    # B: (1.5 * 200) - 0 = 300.00
    expected_subtotal = Decimal("490.00")

    # Taxes:
    # A: 190 * 20% = 38.00
    # B: 300 * 10% = 30.00
    expected_tax = Decimal("68.00")

    # Total = 490 + 68 - 0 = 558.00
    expected_total = Decimal("558.00")

    assert q.subtotal == expected_subtotal
    assert q.tax_total == expected_tax
    assert q.total == expected_total


@pytest.mark.django_db
def test_add_line_item_updates_totals():
    user = User.objects.create_user(email="repo2@example.test", password="x")
    client = Client.objects.create(owner=user, name="BETA")

    q = Quote.objects.create(
        owner=user,
        client=client,
        title="Test Repo Add",
        reference="Q-2025-11-8888",
        currency="EUR",
        language="fr",
        status=Quote.Status.DRAFT,
        issue_date=timezone.localdate(),
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    repo = DjangoQuoteRepository()

    # Ajoute une première ligne
    q1, line1 = repo.add_line_item(
        quote_id=str(q.id),
        description="Setup",
        qty=Decimal("1"),
        unit_price=Decimal("150.00"),
        tax_rate_pct=Decimal("20.00"),
        discount=Decimal("0.00"),
        order=0,
        metadata={"sku": "SETUP"},
    )
    assert q1.subtotal == Decimal("150.00")
    assert q1.tax_total == Decimal("30.00")
    assert q1.total == Decimal("180.00")

    # Ajoute une seconde ligne
    q2, line2 = repo.add_line_item(
        quote_id=str(q.id),
        description="Run",
        qty=Decimal("2"),
        unit_price=Decimal("80.00"),
        tax_rate_pct=Decimal("10.00"),
        discount=Decimal("10.00"),
        order=1,
        metadata={"sku": "RUN"},
    )

    # L1: pre-tax = 150; tax=30
    # L2: pre-tax = (2*80)-10=150 ; tax=15
    # Subtotal = 300 ; Tax = 45 ; Total = 345
    assert q2.subtotal == Decimal("300.00")
    assert q2.tax_total == Decimal("45.00")
    assert q2.total == Decimal("345.00")
