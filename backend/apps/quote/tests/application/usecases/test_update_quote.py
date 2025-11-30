from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.client.models import Client
from apps.quote.adapters.persistence.django_quote_repository import DjangoQuoteRepository
from apps.quote.application.usecases.update_quote import UpdateQuoteUseCase
from apps.quote.models import Quote, QuoteLineItem

User = get_user_model()


@pytest.mark.django_db
def test_update_quote_header_only():
    owner = User.objects.create_user(email="owner@example.test", password="test")

    # Create account
    from apps.user.models.account import Account

    account = Account.objects.create(user=owner, display_name="Owner Account")

    client = Client.objects.create(name="Initial Client", owner=owner)

    quote = Quote.objects.create(
        owner=owner,
        account=account,
        client=client,
        title="Initial title",
        status="DRAFT",
        currency="EUR",
        language="fr",
        issue_date=date(2025, 11, 6),
        valid_until=date(2025, 12, 6),
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    usecase = UpdateQuoteUseCase(quote_repo=DjangoQuoteRepository())

    validated_data = {"title": "Updated title"}

    updated = usecase.execute(
        quote=quote,
        requester_id=owner.id,
        validated_data=validated_data,
        client_patch=None,
        items_field_provided=False,
        items=None,
    )

    assert updated.title == "Updated title"


@pytest.mark.django_db
def test_update_quote_with_items():
    owner = User.objects.create_user(email="owner@example.test", password="test")

    # Create account
    from apps.user.models.account import Account

    account = Account.objects.create(user=owner, display_name="Owner Account")

    client = Client.objects.create(name="Client with items", owner=owner)

    quote = Quote.objects.create(
        owner=owner,
        account=account,
        client=client,
        title="With items",
        status="DRAFT",
        currency="EUR",
        language="fr",
        issue_date=date(2025, 11, 6),
        valid_until=date(2025, 12, 6),
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    QuoteLineItem.objects.create(
        quote=quote,
        description="Old item",
        qty=Decimal("1.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        discount=Decimal("0.00"),
        order=0,
        metadata={},
    )

    items = [
        {
            "description": "New item",
            "qty": Decimal("2.00"),
            "unit_price": Decimal("200.00"),
            "tax_rate_pct": Decimal("10.00"),
            "discount": Decimal("0.00"),
            "order": 0,
            "metadata": {},
        }
    ]

    usecase = UpdateQuoteUseCase(quote_repo=DjangoQuoteRepository())

    updated = usecase.execute(
        quote=quote,
        requester_id=owner.id,
        validated_data={},
        client_patch=None,
        items_field_provided=True,
        items=items,
    )

    assert updated.subtotal == Decimal("400.00")
    assert updated.tax_total == Decimal("40.00")
    assert updated.total == Decimal("440.00")
    assert updated.items.count() == 1
    assert updated.items.first().description == "New item"


@pytest.mark.django_db
def test_update_quote_client_patch_forbidden():
    owner = User.objects.create_user(email="owner@example.test", password="test")
    other_user = User.objects.create_user(email="other@example.test", password="test")

    # Create account
    from apps.user.models.account import Account

    account = Account.objects.create(user=owner, display_name="Owner Account")

    client = Client.objects.create(name="Not owned client", owner=other_user)

    quote = Quote.objects.create(
        owner=owner,
        account=account,
        client=client,
        title="Initial",
        status="DRAFT",
        currency="EUR",
        language="fr",
        issue_date=date(2025, 11, 6),
        valid_until=date(2025, 12, 6),
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    usecase = UpdateQuoteUseCase(quote_repo=DjangoQuoteRepository())
    client_patch = {"name": "Hacked"}

    with pytest.raises(ValidationError) as err:
        usecase.execute(
            quote=quote,
            requester_id=owner.id,
            validated_data={},
            client_patch=client_patch,
            items_field_provided=False,
            items=None,
        )

    assert "You do not own this client." in str(err.value)


@pytest.mark.django_db
def test_update_quote_preserve_items():
    owner = User.objects.create_user(email="owner@example.test", password="test")

    # Create account
    from apps.user.models.account import Account

    account = Account.objects.create(user=owner, display_name="Owner Account")

    client = Client.objects.create(name="Client", owner=owner)

    quote = Quote.objects.create(
        owner=owner,
        account=account,
        client=client,
        title="Preserve",
        status="DRAFT",
        currency="EUR",
        language="fr",
        issue_date=date(2025, 11, 6),
        valid_until=date(2025, 12, 6),
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    QuoteLineItem.objects.create(
        quote=quote,
        description="Existing",
        qty=Decimal("1.00"),
        unit_price=Decimal("300.00"),
        tax_rate=Decimal("10.00"),
        discount=Decimal("0.00"),
        order=0,
        metadata={},
    )

    usecase = UpdateQuoteUseCase(quote_repo=DjangoQuoteRepository())

    updated = usecase.execute(
        quote=quote,
        requester_id=owner.id,
        validated_data={},
        client_patch=None,
        items_field_provided=False,
        items=None,
    )

    assert updated.subtotal == Decimal("300.00")
    assert updated.tax_total == Decimal("30.00")
    assert updated.total == Decimal("330.00")
    assert updated.items.count() == 1
    assert updated.items.first().description == "Existing"
