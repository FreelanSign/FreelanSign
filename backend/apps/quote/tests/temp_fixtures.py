import pytest
from apps.user.models import Account


@pytest.fixture
def user_with_account(db, django_user_model):
    user = django_user_model.objects.create_user(email="test@example.com", password="password")
    account = Account.objects.create(user=user, name="Test Account")
    return user, account
