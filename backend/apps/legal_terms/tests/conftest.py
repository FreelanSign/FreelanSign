"""
Pytest fixtures for legal_terms tests.
"""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """API client for testing."""
    return APIClient()


@pytest.fixture
def user_with_account(db, django_user_model):
    """Create a user with an account and profile."""
    from apps.user.models import Account, Profile

    user = django_user_model.objects.create_user(email="test@example.com", password="password")

    # Create profile
    Profile.objects.create(
        user=user,
        first_name="Test",
        last_name="User",
        phone="",  # Will be set by tests
    )

    # Create account
    account = Account.objects.create(
        user=user,
        display_name="Test Account",
        is_active=True,
    )

    return user, account
