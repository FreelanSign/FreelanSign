from datetime import date
from decimal import Decimal

import pytest
from django.forms import ValidationError
from django.utils import timezone
from pytest_mock import MockerFixture

from apps.client.models import Client
from apps.quote.application.usecases.create_quote import CreateQuoteUseCase
from apps.quote.models import Quote, QuoteLineItem


@pytest.mark.django_db  # Accéder aux données
def test_create_quote_success(mocker):
    # Créé un User
    from django.contrib.auth import get_user_model

    User = get_user_model()
    owner = User.objects.create_user(email="owner@example.test", password="test")

    # Créé un Client
    client = Client.objects.create(name="Test Client", owner=owner)

    # Définir un item du modèle QuoteLineItem
    item = {
        "description": "Test item",
        "qty": Decimal("2.00"),
        "unit_price": Decimal("100.00"),
        "tax_rate": Decimal("20.00"),
        "discount": Decimal("0.00"),
        "order": 0,
        "metadata": {},
    }

    # Simule ce que le serializer .create(validated_data) transmettrait
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

    # mock qui retourne la référence
    fake_ref_generator = mocker.Mock()
    fake_ref_generator.next_reference.return_value = "Q-2025-11-0001"

    # mock du repository
    fake_repo = mocker.Mock()
    fake_repo.create.side_effect = lambda owner_id, fields: str(
        Quote.objects.create(
            owner_id=owner_id,
            **fields,
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
        ).id
    )

    fake_repo.get.side_effect = lambda quote_id, requester_id: Quote.objects.get(pk=quote_id)

    # instancie le usecase
    usecase = CreateQuoteUseCase(ref_generator=fake_ref_generator, quote_repository=fake_repo)
    quote = usecase.execute(
        owner=owner, validated_data=validated_data.copy()
    )  # copie du validated_data pour pas qu'il soit mute dans le test

    # Assertions
    assert quote.reference == "Q-2025-11-0001"
    assert quote.owner == owner
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

    fake_ref_generator.next_reference.assert_called_once_with(owner_id=owner.id, when=date(2025, 11, 6))
    fake_repo.create.assert_called_once()
    fake_repo.get.assert_called_once()


@pytest.mark.django_db
def test_client_patch_forbidden(mocker):
    # Créé un User
    from django.contrib.auth import get_user_model

    User = get_user_model()
    owner = User.objects.create_user(email="owner@example.test", password="test")

    other_user = User.objects.create_user(email="otheruser@example.test", password="password")

    client = Client.objects.create(name="Client Toto", owner=other_user)

    # Définir un item du modèle QuoteLineItem
    item = {
        "description": "Test item",
        "qty": Decimal("2.00"),
        "unit_price": Decimal("100.00"),
        "tax_rate": Decimal("20.00"),
        "discount": Decimal("0.00"),
        "order": 0,
        "metadata": {},
    }

    # Simule ce que le serializer .create(validated_data) transmettrait
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
    # mock du repository
    fake_repo = mocker.Mock()
    fake_repo.create.side_effect = lambda owner_id, fields: str(
        Quote.objects.create(
            owner_id=owner_id,
            **fields,
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
        ).id
    )

    fake_repo.get.side_effect = lambda quote_id, requester_id: Quote.objects.get(pk=quote_id)

    # Instancie le use case
    usecase = CreateQuoteUseCase(ref_generator=fake_ref_generator, quote_repository=fake_repo)
    with pytest.raises(ValidationError) as execution_info:
        usecase.execute(owner=owner, validated_data=validated_data.copy(), client_patch=client_patch.copy())

    assert "You do not own this client." in str(execution_info)


@pytest.mark.django_db
def test_create_quote_no_changes_to_client(mocker):
    # Créé un User
    from django.contrib.auth import get_user_model

    User = get_user_model()
    owner = User.objects.create_user(email="owner@example.test", password="test")
    client = Client.objects.create(name="Client Toto", owner=owner)

    # Définir un item du modèle QuoteLineItem
    item = {
        "description": "Test item",
        "qty": Decimal("2.00"),
        "unit_price": Decimal("100.00"),
        "tax_rate": Decimal("20.00"),
        "discount": Decimal("0.00"),
        "order": 0,
        "metadata": {},
    }

    # Simule ce que le serializer .create(validated_data) transmettrait
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
    # mock du repository
    fake_repo = mocker.Mock()
    fake_repo.create.side_effect = lambda owner_id, fields: str(
        Quote.objects.create(
            owner_id=owner_id,
            **fields,
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
        ).id
    )

    fake_repo.get.side_effect = lambda quote_id, requester_id: Quote.objects.get(pk=quote_id)

    # Instancie le use case
    usecase = CreateQuoteUseCase(ref_generator=fake_ref_generator, quote_repository=fake_repo)
    quote = usecase.execute(owner=owner, validated_data=validated_data.copy(), client_patch=client_patch.copy())

    assert quote.client == client
    fake_repo.create.assert_called_once()
    fake_repo.get.assert_called_once()


@pytest.mark.django_db
def test_totals_are_computed(mocker):
    # Créé un User
    from django.contrib.auth import get_user_model

    User = get_user_model()
    owner = User.objects.create_user(email="owner@example.test", password="test")
    client = Client.objects.create(name="Client Toto", owner=owner)

    # Définir un item du modèle QuoteLineItem
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

    # Simule ce que le serializer .create(validated_data) transmettrait
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
    # mock du repository
    fake_repo = mocker.Mock()
    fake_repo.create.side_effect = lambda owner_id, fields: str(
        Quote.objects.create(
            owner_id=owner_id,
            **fields,
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
        ).id
    )

    fake_repo.get.side_effect = lambda quote_id, requester_id: Quote.objects.get(pk=quote_id)

    # Instancie le use case
    usecase = CreateQuoteUseCase(ref_generator=fake_ref_generator, quote_repository=fake_repo)
    quote = usecase.execute(owner=owner, validated_data=validated_data.copy(), client_patch=client_patch.copy())

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
