from datetime import date
from decimal import Decimal

import pytest
from django.forms import ValidationError
from django.utils import timezone
from pytest_mock import MockerFixture

from apps.client.models import Client
from apps.quote.application.usecases.create_quote import CreateQuoteUseCase
from apps.quote.models import Quote, QuoteLineItem


@pytest.mark.django_db
def test_create_quote_success(mocker):
    """
    Test création quote avec nouveau système Account.

    Changements:
    - owner (User) → account_id (int) + requester_id (int)
    - Création d'un Account avant le test
    - ref_generator prend account_id au lieu de owner_id
    """
    from django.contrib.auth import get_user_model
    from apps.user.models import Account

    User = get_user_model()
    owner = User.objects.create_user(email="owner@example.test", password="test")

    account = Account.objects.create(user=owner, display_name="Test Account", legal_form="EI")

    client = Client.objects.create(name="Test Client", owner=owner, account=account)

    item = {
        "description": "Test item",
        "qty": Decimal("2.00"),
        "unit_price": Decimal("100.00"),
        "tax_rate": Decimal("20.00"),
        "discount": Decimal("0.00"),
        "order": 0,
        "metadata": {},
    }

    validated_data = {
        "title": "Devis Test",
        "currency": "EUR",
        "language": "fr",
        "status": "DRAFT",
        "issue_date": date(2025, 11, 6),
        "valid_until": date(2025, 12, 6),
        "payment_terms": None,
        "payment_terms_text": "",
        "note": "",
        "metadata": {},
        "client": client,
        "items": [item],
    }

    # Mock ref generator
    fake_ref_generator = mocker.Mock()
    fake_ref_generator.next_reference.return_value = "Q-2025-11-0001"

    # Mock repository
    fake_repo = mocker.Mock()
    fake_repo.create.side_effect = lambda account_id, fields: str(
        Quote.objects.create(
            account_id=account_id,
            **fields,
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
        ).id
    )

    fake_repo.get.side_effect = lambda quote_id, requester_id: Quote.objects.get(pk=quote_id)

    usecase = CreateQuoteUseCase(ref_generator=fake_ref_generator, quote_repository=fake_repo)

    quote = usecase.execute(
        account_id=account.id,
        requester_id=owner.id,
        validated_data=validated_data.copy(),
    )

    assert quote.reference == "Q-2025-11-0001"
    assert quote.account_id == account.id
    assert quote.client == client
    assert quote.subtotal == Decimal("200.00")
    assert quote.tax_total == Decimal("40.00")
    assert quote.total == Decimal("240.00")

    items = list(quote.items.all())
    assert len(items) == 1
    assert items[0].description == "Test item"
    assert items[0].qty == Decimal("2.00")
    assert items[0].unit_price == Decimal("100.00")
    assert items[0].tax_rate == Decimal("20.00")

    fake_ref_generator.next_reference.assert_called_once_with(owner_id=account.id, when=date(2025, 11, 6))
    fake_repo.create.assert_called_once()
    fake_repo.get.assert_called_once()


@pytest.mark.django_db
def test_client_patch_forbidden(mocker):
    """
    Test qu'un User ne peut pas patcher le Client d'un autre User.

    Changements:
    - owner → account_id + requester_id
    - Vérification: requester_id != client.owner_id → 403
    """
    from django.contrib.auth import get_user_model
    from apps.user.models import Account

    User = get_user_model()
    owner = User.objects.create_user(email="owner@example.test", password="test")
    other_user = User.objects.create_user(email="otheruser@example.test", password="password")

    account = Account.objects.create(user=owner, display_name="Owner Account", legal_form="EI")

    client = Client.objects.create(name="Client Toto", owner=other_user, account=account)

    item = {
        "description": "Test item",
        "qty": Decimal("2.00"),
        "unit_price": Decimal("100.00"),
        "tax_rate": Decimal("20.00"),
        "discount": Decimal("0.00"),
        "order": 0,
        "metadata": {},
    }

    validated_data = {
        "title": "Devis Test",
        "currency": "EUR",
        "language": "fr",
        "status": "DRAFT",
        "issue_date": date(2025, 11, 6),
        "valid_until": date(2025, 12, 6),
        "payment_terms": None,
        "payment_terms_text": "",
        "note": "",
        "metadata": {},
        "client": client,
        "items": [item],
    }

    client_patch = {"name": "new patch name"}

    fake_ref_generator = mocker.Mock()
    fake_ref_generator.next_reference.return_value = "Q-2025-11-0001"

    fake_repo = mocker.Mock()
    fake_repo.create.side_effect = lambda account_id, fields: str(
        Quote.objects.create(
            account_id=account_id,
            **fields,
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
        ).id
    )

    fake_repo.get.side_effect = lambda quote_id, requester_id: Quote.objects.get(pk=quote_id)

    usecase = CreateQuoteUseCase(ref_generator=fake_ref_generator, quote_repository=fake_repo)

    with pytest.raises(ValidationError) as execution_info:
        usecase.execute(
            account_id=account.id,
            requester_id=owner.id,
            validated_data=validated_data.copy(),
            client_patch=client_patch.copy(),
        )

    assert "You do not own this client." in str(execution_info)


@pytest.mark.django_db
def test_create_quote_no_changes_to_client(mocker):
    """
    Test création quote sans patch client (client_patch vide).

    Changements:
    - owner → account_id + requester_id
    """
    from django.contrib.auth import get_user_model
    from apps.user.models import Account

    User = get_user_model()
    owner = User.objects.create_user(email="owner@example.test", password="test")

    account = Account.objects.create(user=owner, display_name="Test Account", legal_form="EI")

    client = Client.objects.create(name="Client Toto", owner=owner, account=account)

    item = {
        "description": "Test item",
        "qty": Decimal("2.00"),
        "unit_price": Decimal("100.00"),
        "tax_rate": Decimal("20.00"),
        "discount": Decimal("0.00"),
        "order": 0,
        "metadata": {},
    }

    validated_data = {
        "title": "Devis Test",
        "currency": "EUR",
        "language": "fr",
        "status": "DRAFT",
        "issue_date": date(2025, 11, 6),
        "valid_until": date(2025, 12, 6),
        "payment_terms": None,
        "payment_terms_text": "",
        "note": "",
        "metadata": {},
        "client": client,
        "items": [item],
    }

    client_patch = {}

    fake_ref_generator = mocker.Mock()
    fake_ref_generator.next_reference.return_value = "Q-2025-11-0001"

    fake_repo = mocker.Mock()
    fake_repo.create.side_effect = lambda account_id, fields: str(
        Quote.objects.create(
            account_id=account_id,
            **fields,
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
        ).id
    )

    fake_repo.get.side_effect = lambda quote_id, requester_id: Quote.objects.get(pk=quote_id)

    usecase = CreateQuoteUseCase(ref_generator=fake_ref_generator, quote_repository=fake_repo)

    # ✅ CHANGEMENT
    quote = usecase.execute(
        account_id=account.id,
        requester_id=owner.id,
        validated_data=validated_data.copy(),
        client_patch=client_patch.copy(),
    )

    assert quote.client == client
    fake_repo.create.assert_called_once()
    fake_repo.get.assert_called_once()


@pytest.mark.django_db
def test_totals_are_computed(mocker):
    """
    Test calcul des totaux avec plusieurs items.

    Changements:
    - owner → account_id + requester_id
    """
    from django.contrib.auth import get_user_model
    from apps.user.models import Account

    User = get_user_model()
    owner = User.objects.create_user(email="owner@example.test", password="test")

    account = Account.objects.create(user=owner, display_name="Test Account", legal_form="EI")

    client = Client.objects.create(name="Client Toto", owner=owner, account=account)

    item1 = {
        "description": "Test item",
        "qty": Decimal("2.00"),
        "unit_price": Decimal("100.00"),
        "tax_rate": Decimal("20.00"),
        "discount": Decimal("0.00"),
        "order": 0,
        "metadata": {},
    }
    # item 1 = 240

    item2 = {
        "description": "Test item 2",
        "qty": Decimal("1.00"),
        "unit_price": Decimal("1220.00"),
        "tax_rate": Decimal("20.00"),
        "discount": Decimal("0.00"),
        "order": 0,
        "metadata": {},
    }
    # item2 = 1464

    items = [item1, item2]

    validated_data = {
        "title": "Devis Test",
        "currency": "EUR",
        "language": "fr",
        "status": "DRAFT",
        "issue_date": date(2025, 11, 6),
        "valid_until": date(2025, 12, 6),
        "payment_terms": None,
        "payment_terms_text": "",
        "note": "",
        "metadata": {},
        "client": client,
        "items": items,
        "discount_total": Decimal("10.00"),
    }

    client_patch = {}

    fake_ref_generator = mocker.Mock()
    fake_ref_generator.next_reference.return_value = "Q-2025-11-0001"

    fake_repo = mocker.Mock()
    fake_repo.create.side_effect = lambda account_id, fields: str(
        Quote.objects.create(
            account_id=account_id,
            **fields,
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
        ).id
    )

    fake_repo.get.side_effect = lambda quote_id, requester_id: Quote.objects.get(pk=quote_id)

    usecase = CreateQuoteUseCase(ref_generator=fake_ref_generator, quote_repository=fake_repo)

    quote = usecase.execute(
        account_id=account.id,
        requester_id=owner.id,
        validated_data=validated_data.copy(),
        client_patch=client_patch.copy(),
    )

    subtotal_expected = Decimal("1420.00")
    tax_expected = Decimal("284.00")  # 20% de 1420
    discount_total = Decimal("10.00")
    total_expected = subtotal_expected + tax_expected - discount_total

    assert quote.subtotal == subtotal_expected
    assert quote.tax_total == tax_expected
    assert quote.discount_total == discount_total
    assert quote.total == total_expected
    fake_repo.create.assert_called_once()
    fake_repo.get.assert_called_once()
