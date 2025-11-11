# apps/user/tests/application/usecases/test_reset_password.py
from time import time

import pytest
from django.core import signing

from apps.user.application.dto.user_inputs import ResetPasswordInput
from apps.user.application.errors import UserNotFoundError
from apps.user.application.usecases.reset_password import ResetPassword


def make_token(user_id: int) -> str:
    return signing.dumps({"user_id": user_id, "ts": time()}, salt="user.reset")


def test_resets_password_successfully():
    repo = DummyRepo(user_exists=True)
    use_case = ResetPassword(repo, token_max_age_sec=3600)

    token = make_token(42)
    dto = ResetPasswordInput(token=token, new_password="Valid123!")
    use_case.execute(dto)

    assert repo.updated_password_for == 42


def test_invalid_token_raises_user_not_found():
    repo = DummyRepo()
    use_case = ResetPassword(repo, token_max_age_sec=3600)

    with pytest.raises(UserNotFoundError):
        use_case.execute(ResetPasswordInput(token="invalid", new_password="Valid123!"))


def test_expired_token_rejected():
    repo = DummyRepo()
    use_case = ResetPassword(repo, token_max_age_sec=1)  # 1 second

    token = make_token(42)
    import time as t

    t.sleep(2)

    with pytest.raises(UserNotFoundError):
        use_case.execute(ResetPasswordInput(token=token, new_password="Valid123!"))


class DummyRepo:
    def __init__(self, user_exists=True):
        self.user_exists = user_exists
        self.updated_password_for = None

    def update_password(self, user_id, new_password):
        if not self.user_exists:
            raise UserNotFoundError()
        self.updated_password_for = user_id
