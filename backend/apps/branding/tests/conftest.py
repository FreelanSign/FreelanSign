# apps/branding/tests/conftest.py
import pytest


@pytest.fixture
def user_with_account(db, django_user_model):
    from apps.user.models import Account

    user = django_user_model.objects.create_user(email="test@example.com", password="password")
    account = Account.objects.create(user=user, display_name="Test Account", is_active=True)
    return user, account
