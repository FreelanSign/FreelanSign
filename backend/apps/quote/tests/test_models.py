# apps/quote/tests/test_models.py
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.client.models import Client  # ← Import direct
from apps.quote.models import Quote, QuoteLineItem

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.django_db
def test_reference_unique_per_owner():  # ← Retire le paramètre client_model
    """Ensure (owner, reference) uniqueness is enforced."""
    owner = User.objects.create_user(email="a@x.io", password="x")

    # Create account
    from apps.user.models.account import Account

    account = Account.objects.create(user=owner, display_name="Account A")

    c = Client.objects.create(owner=owner, name="ACME", account=account)

    q1 = Quote.objects.create(
        owner=owner,
        account=account,
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
            account=account,
            client=c,
            title="Q2",
            reference="REF-001",  # ← Doublon
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
def test_totals_verification():  # ← Retire le paramètre client_model
    """Protect decimals and arithmetic: subtotal + tax_total - discount_total == total."""
    owner = User.objects.create_user(email="b@x.io", password="x")

    # Create account
    from apps.user.models.account import Account

    account = Account.objects.create(user=owner, display_name="Account B")

    c = Client.objects.create(owner=owner, name="Client B", account=account)

    q = Quote.objects.create(
        owner=owner,
        account=account,
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

    subtotal = q.compute_subtotal()
    tax_total = q.compute_tax_total()
    discount_total = Decimal("100.00")
    total = subtotal + tax_total - discount_total

    q.subtotal = subtotal
    q.tax_total = tax_total
    q.discount_total = discount_total
    q.total = total
    q.save()

    assert q.totals_match() is True


@pytest.mark.django_db
def test_line_item_long_description():
    """Verify description field accepts text longer than 255 characters."""
    owner = User.objects.create_user(email="long@desc.io", password="x")

    from apps.user.models.account import Account

    account = Account.objects.create(user=owner, display_name="Account Long")
    client = Client.objects.create(owner=owner, name="Client Long", account=account)

    q = Quote.objects.create(
        owner=owner,
        account=account,
        client=client,
        title="Q Long",
        reference="REF-LONG",
        currency="EUR",
        language="fr",
        status=Quote.Status.DRAFT,
        issue_date=timezone.now().date(),
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    # Create a description longer than 255 characters
    long_description = "A" * 500

    line = QuoteLineItem.objects.create(
        quote=q,
        description=long_description,
        qty=Decimal("1"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        discount=Decimal("0.00"),
        order=1,
        line_total=Decimal("100.00"),
    )

    # Refresh from DB and verify full description is stored
    line.refresh_from_db()
    assert len(line.description) == 500
    assert line.description == long_description
