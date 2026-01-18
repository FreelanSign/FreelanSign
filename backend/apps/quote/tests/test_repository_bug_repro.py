import datetime
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.client.models import Client
from apps.quote.adapters.persistence.django_quote_repository import DjangoQuoteRepository
from apps.quote.models import Quote, QuoteLineItem
from apps.user.models import Account

User = get_user_model()


@pytest.mark.django_db
def test_replace_lines_saves_details_field():
    # GIVEN a quote created manually
    user = User.objects.create_user(email="test@example.com", password="password")
    account = Account.objects.create(display_name="Test Account", user=user)
    client = Client.objects.create(account=account, name="Test Client", owner=user)

    quote = Quote.objects.create(
        owner=user,
        account=account,
        client=client,
        title="Test Quote",
        issue_date=datetime.date.today(),
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )

    repo = DjangoQuoteRepository()

    # WHEN replacing lines with a line that has 'details'
    lines_data = [
        {
            "description": "Prestation principale",
            "details": "Détails très importants qui ne doivent pas disparaitre",
            "qty": Decimal("1.00"),
            "unit_price": Decimal("100.00"),
            "tax_rate": Decimal("20.00"),
            "discount": Decimal("0.00"),
        }
    ]

    repo.replace_lines(quote_id=quote.id, lines=lines_data)

    # THEN the details are saved
    item = quote.items.first()
    assert item is not None
    assert item.description == "Prestation principale"
    assert item.details == "Détails très importants qui ne doivent pas disparaitre"
