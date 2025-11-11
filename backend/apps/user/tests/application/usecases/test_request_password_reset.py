# apps/user/tests/application/usecases/test_request_password_reset.py

from unittest.mock import Mock

import pytest

from apps.user.application.usecases.request_password_reset import RequestPasswordReset


def test_sends_token_if_user_found():
    repo = Mock()
    sender = Mock()
    repo.get_by_email.return_value = Mock(id=42, email="bob@example.com")

    use_case = RequestPasswordReset(user_repository=repo, token_sender=sender)
    use_case.execute("bob@example.com")

    sender.send_reset_link.assert_called_once()
    called_email = sender.send_reset_link.call_args.kwargs["email"]
    called_token = sender.send_reset_link.call_args.kwargs["token"]
    assert isinstance(called_token, str)
    assert called_email == "bob@example.com"
    assert len(called_token) > 10


def test_silent_if_user_not_found():
    repo = Mock()
    sender = Mock()
    repo.get_by_email.return_value = None

    use_case = RequestPasswordReset(user_repository=repo, token_sender=sender)
    use_case.execute("ghost@example.com")

    sender.send_reset_link.assert_not_called()
