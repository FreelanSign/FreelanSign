# apps/client/tests/conftest.py

import pytest
from django.contrib.auth import get_user_model

from apps.user.models.account import Account

User = get_user_model()


@pytest.fixture
def user_with_account(db):
    """Utilisateur avec un Account actif."""
    user = User.objects.create_user(
        email="client_user@test.com",
        password="testpass123",
    )
    Account.objects.create(
        user=user,
        display_name="User Account",
        legal_form="micro",
        is_active=True,
    )
    return user


@pytest.fixture
def account(db, user_with_account):
    """
    Account associé à user_with_account.
    On centralise ici la logique de création/récupération.
    """
    return Account.objects.get(user=user_with_account)
    # ou si tu veux être safe :
    # account, _ = Account.objects.get_or_create(
    #     user=user_with_account,
    #     defaults={"display_name": "User Account", "legal_form": "micro", "is_active": True},
    # )
    # return account
