"""Integration tests for AccountServiceAdapter."""

import pytest
from django.contrib.auth import get_user_model

from apps.legal_terms.adapters.services.account_service_adapter import AccountServiceAdapter
from apps.legal_terms.domain.exceptions import MissingTemplateVariablesError
from apps.user.models.account import Account

User = get_user_model()


@pytest.fixture
def user_with_profile(db):
    """Create a user with profile."""
    from apps.user.models.models import Profile

    user = User.objects.create_user(
        email="test@example.com",
        password="testpass123",
    )
    # Create profile explicitly for tests
    Profile.objects.create(
        user=user,
        phone="+33612345678",
    )
    return user


@pytest.fixture
def account_with_full_address(user_with_profile):
    """Create an account with complete address."""
    return Account.objects.create(
        user=user_with_profile,
        display_name="Test Business SARL",
        legal_id="12345678901234",
        address_line1="123 Main Street",
        address_line2="Apartment 4B",
        city="Paris",
        postal_code="75001",
        country="fr",
    )


@pytest.fixture
def account_with_partial_address(user_with_profile):
    """Create an account with partial address (no line2, no country)."""
    return Account.objects.create(
        user=user_with_profile,
        display_name="Test Business SARL",
        legal_id="12345678901234",
        address_line1="123 Main Street",
        city="Paris",
        postal_code="75001",
    )


@pytest.fixture
def account_with_no_address(user_with_profile):
    """Create an account with no address."""
    return Account.objects.create(
        user=user_with_profile,
        display_name="Test Business SARL",
        legal_id="12345678901234",
    )


@pytest.mark.django_db
class TestAccountServiceAdapter:
    """Test AccountServiceAdapter integration."""

    def test_get_vars_with_full_address(self, account_with_full_address):
        """Should format full address correctly in template variables."""
        adapter = AccountServiceAdapter()
        result = adapter.get_template_variables(str(account_with_full_address.id))

        assert result.address == "123 Main Street, Apartment 4B, 75001 Paris, FR"
        assert result.siret == "12345678901234"
        assert result.business_name == "Test Business SARL"
        assert result.email == "test@example.com"
        assert result.phone == "+33612345678"

    def test_get_vars_with_partial_address(self, account_with_partial_address):
        """Should format partial address correctly."""
        adapter = AccountServiceAdapter()
        result = adapter.get_template_variables(str(account_with_partial_address.id))

        assert result.address == "123 Main Street, 75001 Paris"
        assert result.siret == "12345678901234"
        assert result.business_name == "Test Business SARL"

    def test_get_vars_with_no_address(self, account_with_no_address):
        """Should use placeholder when no address provided."""
        adapter = AccountServiceAdapter()
        result = adapter.get_template_variables(str(account_with_no_address.id))

        assert result.address == "Adresse à compléter"
        assert result.siret == "12345678901234"
        assert result.business_name == "Test Business SARL"

    def test_raises_error_when_missing_required_fields(self, user_with_profile):
        """Should raise error when required fields are missing."""
        # Create account without required fields
        account = Account.objects.create(
            user=user_with_profile,
            # Missing display_name and legal_id
        )

        adapter = AccountServiceAdapter()
        with pytest.raises(MissingTemplateVariablesError) as exc_info:
            adapter.get_template_variables(str(account.id))

        # Verify error contains missing fields
        error_message = str(exc_info.value)
        assert "SIRET" in error_message or "Business name" in error_message

    def test_address_not_in_missing_fields(self, user_with_profile):
        """Address should not be in missing fields check (optional field)."""
        # Create account with required fields but no address
        account = Account.objects.create(
            user=user_with_profile,
            display_name="Test Business",
            legal_id="12345678901234",
        )

        adapter = AccountServiceAdapter()
        # Should NOT raise error even though address is empty
        result = adapter.get_template_variables(str(account.id))
        assert result.address == "Adresse à compléter"
