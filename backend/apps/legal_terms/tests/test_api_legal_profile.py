"""
TDD tests for legal profile API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status

from apps.legal_terms.adapters.persistence.models import (
    LegalProfileModel,
    LegalTemplateModel,
)


@pytest.fixture
def legal_template(db):
    """Get or create a legal template for testing."""
    # Try to get existing template first (from migration)
    try:
        template = LegalTemplateModel.objects.get(jurisdiction="FR", version="1.0.0")
        return template
    except LegalTemplateModel.DoesNotExist:
        # Create if doesn't exist
        return LegalTemplateModel.objects.create(
            name="CGV Auto-Entrepreneur FR",
            jurisdiction="FR",
            version="1.0.0",
            is_active=True,
            clauses=[
                {
                    "identifier": "payment_terms",
                    "category": "mandatory",
                    "default_title": "Conditions de paiement",
                    "default_body": "Le paiement est dû sous 30 jours.",
                    "default_order": 1,
                    "default_is_active": True,
                },
                {
                    "identifier": "warranty",
                    "category": "optional",
                    "default_title": "Garantie",
                    "default_body": "Garantie de 6 mois.",
                    "default_order": 2,
                    "default_is_active": False,
                },
            ],
        )


@pytest.mark.django_db
class TestLegalProfileAPI:
    """Test suite for legal profile API endpoints."""

    def test_get_legal_profile_returns_profile_for_account(self, api_client, user_with_account, legal_template):
        """Test GET /api/legal-terms/profile/ returns profile for current account."""
        user, account = user_with_account
        api_client.force_login(user)

        url = reverse("legal_terms:legal-profile")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "id" in data
        assert data["account_id"] == str(account.id)
        assert data["template_id"] == str(legal_template.id)
        assert data["template_version"] == "1.0.0"
        assert "clause_overrides" in data

    def test_get_legal_profile_creates_profile_if_not_exists(self, api_client, user_with_account, legal_template):
        """Test GET creates profile if it doesn't exist."""
        user, account = user_with_account
        api_client.force_login(user)

        # Ensure no profile exists
        assert not LegalProfileModel.objects.filter(account=account).exists()

        url = reverse("legal_terms:legal-profile")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Profile should now exist
        assert LegalProfileModel.objects.filter(account=account).exists()

    def test_get_legal_profile_requires_authentication(self, api_client, legal_template):
        """Test GET /api/legal-terms/profile/ requires authentication."""
        url = reverse("legal_terms:legal-profile")
        response = api_client.get(url)

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_patch_legal_profile_updates_clause_overrides(self, api_client, user_with_account, legal_template):
        """Test PATCH /api/legal-terms/profile/ updates clause overrides."""
        user, account = user_with_account
        api_client.force_login(user)

        # Create profile first
        profile = LegalProfileModel.objects.create(
            account=account,
            template=legal_template,
            clause_overrides={},
        )

        url = reverse("legal_terms:legal-profile")
        payload = {
            "updates": [
                {
                    "identifier": "warranty",
                    "is_active": True,
                    "custom_title": "Garantie personnalisée",
                }
            ]
        }
        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check that override was applied
        assert "warranty" in data["clause_overrides"]
        warranty_override = data["clause_overrides"]["warranty"]
        assert warranty_override["is_active"] is True
        assert warranty_override["custom_title"] == "Garantie personnalisée"

    def test_patch_legal_profile_prevents_disabling_mandatory_clause(self, api_client, user_with_account, legal_template):
        """Test PATCH prevents disabling mandatory clauses."""
        user, account = user_with_account
        api_client.force_login(user)

        # Create profile first
        LegalProfileModel.objects.create(
            account=account,
            template=legal_template,
            clause_overrides={},
        )

        url = reverse("legal_terms:legal-profile")
        payload = {
            "updates": [
                {
                    "identifier": "payment_terms",
                    "is_active": False,  # Try to disable mandatory clause
                }
            ]
        }
        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.json()

    def test_patch_legal_profile_allows_disabling_optional_clause(self, api_client, user_with_account, legal_template):
        """Test PATCH allows disabling optional clauses."""
        user, account = user_with_account
        api_client.force_login(user)

        # Create profile first with warranty enabled
        profile = LegalProfileModel.objects.create(
            account=account,
            template=legal_template,
            clause_overrides={"warranty": {"is_active": True}},
        )

        url = reverse("legal_terms:legal-profile")
        payload = {
            "updates": [
                {
                    "identifier": "warranty",
                    "is_active": False,
                }
            ]
        }
        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check that override was applied
        assert "warranty" in data["clause_overrides"]
        assert data["clause_overrides"]["warranty"]["is_active"] is False

    def test_patch_legal_profile_requires_authentication(self, api_client, legal_template):
        """Test PATCH requires authentication."""
        url = reverse("legal_terms:legal-profile")
        payload = {"updates": [{"identifier": "warranty", "is_active": True}]}
        response = api_client.patch(url, payload, format="json")

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_patch_legal_profile_returns_404_for_unknown_clause(self, api_client, user_with_account, legal_template):
        """Test PATCH returns 400 for unknown clause identifier."""
        user, account = user_with_account
        api_client.force_login(user)

        # Create profile first
        LegalProfileModel.objects.create(
            account=account,
            template=legal_template,
            clause_overrides={},
        )

        url = reverse("legal_terms:legal-profile")
        payload = {
            "updates": [
                {
                    "identifier": "unknown_clause",
                    "is_active": True,
                }
            ]
        }
        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.json()

    def test_patch_legal_profile_applies_multiple_updates(self, api_client, user_with_account, legal_template):
        """Test PATCH can apply multiple updates at once."""
        user, account = user_with_account
        api_client.force_login(user)

        # Create profile first
        LegalProfileModel.objects.create(
            account=account,
            template=legal_template,
            clause_overrides={},
        )

        url = reverse("legal_terms:legal-profile")
        payload = {
            "updates": [
                {
                    "identifier": "warranty",
                    "is_active": True,
                    "custom_title": "Garantie modifiée",
                },
                {
                    "identifier": "payment_terms",
                    "custom_body": "Paiement sous 15 jours",
                },
            ]
        }
        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check both overrides were applied
        assert "warranty" in data["clause_overrides"]
        assert "payment_terms" in data["clause_overrides"]
        assert data["clause_overrides"]["warranty"]["custom_title"] == "Garantie modifiée"
        assert data["clause_overrides"]["payment_terms"]["custom_body"] == "Paiement sous 15 jours"
