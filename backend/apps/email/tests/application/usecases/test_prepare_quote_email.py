from datetime import date
from unittest.mock import Mock
from uuid import uuid4

import pytest
from django.core.exceptions import PermissionDenied

from apps.email.application.dto.prepared_email_data import PreparedEmailData
from apps.email.application.usecases.prepare_quote_email import PrepareQuoteEmail, PrepareQuoteEmailCommand
from apps.email.domain.entities.prepared_email import PreparedEmail
from apps.quote.application.errors import QuoteNotFoundError
from apps.user.models import User


def make_fake_quote(owner_id, **overrides):
    client = Mock()
    client.name = "Alice Dupont"
    client.email = "client@example.com"

    quote = Mock()
    quote.owner_id = owner_id
    quote.client = client
    quote.reference = "Q-123"
    quote.title = "Site Web"
    quote.issue_date = date(2024, 1, 1)
    quote.valid_until = date(2024, 1, 31)
    for k, v in overrides.items():
        setattr(quote, k, v)
    return quote


def test_prepare_quote_email_success():
    quote_id = uuid4()
    user = Mock(spec=User)
    user.id = uuid4()

    fake_quote = make_fake_quote(owner_id=user.id)

    repo = Mock()
    repo.get.return_value = fake_quote

    renderer = Mock()
    expected_email = PreparedEmail(
        to="client@example.com",
        subject="Devis Q-123 – Site Web",
        body_plain="Body plain",
        body_html="<p>Body</p>",
        template_version="v1.0",
    )
    renderer.render_plain.return_value = expected_email.body_plain
    renderer.render_html.return_value = expected_email.body_html

    uc = PrepareQuoteEmail(repo, renderer)
    cmd = PrepareQuoteEmailCommand(quote_id=quote_id, requester=user, locale="fr")
    result = uc.execute(cmd)

    assert result == expected_email
    repo.get.assert_called_once_with(quote_id=quote_id, requester_id=str(user.id), include_lines=False)
    renderer.render_plain.assert_called_once()
    renderer.render_html.assert_called_once()


def test_prepare_quote_email_quote_not_found_raises_QuoteNotFound():
    quote_id = uuid4()
    user = Mock(spec=User)
    user.id = uuid4()

    repo = Mock()
    repo.get.side_effect = QuoteNotFoundError()

    renderer = Mock()

    uc = PrepareQuoteEmail(repo, renderer)
    cmd = PrepareQuoteEmailCommand(quote_id=quote_id, requester=user)

    with pytest.raises(QuoteNotFoundError):
        uc.execute(cmd)


def test_prepare_quote_email_ownership_check():
    quote_id = uuid4()
    user = Mock(spec=User)
    user.id = uuid4()

    fake_quote = make_fake_quote(owner_id=uuid4())  # différent du user.id

    repo = Mock()
    repo.get.return_value = fake_quote

    renderer = Mock()

    uc = PrepareQuoteEmail(repo, renderer)
    cmd = PrepareQuoteEmailCommand(quote_id=quote_id, requester=user)

    with pytest.raises(PermissionDenied):
        uc.execute(cmd)
