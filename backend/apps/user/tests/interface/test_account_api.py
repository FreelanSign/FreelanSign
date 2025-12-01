# apps/user/tests/interface/test_account_api.py
"""
Integration tests for Account REST API.

Tests use real database (pytest-django) and DRF test client.

@author: @Bertrand2808
@since: 2025-11-26
@version: 1.0
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.user.models.account import Account

User = get_user_model()


@pytest.fixture
def api_client():
    """DRF API client."""
    return APIClient()


@pytest.fixture
def user():
    """Regular user."""
    return User.objects.create_user(email="user@test.com", password="testpass123")


@pytest.fixture
def admin_user():
    """Admin user with profile."""
    admin = User.objects.create_user(email="admin@test.com", password="adminpass123")
    # Create profile with admin role
    from apps.user.models.models import Profile

    Profile.objects.create(user=admin, role="admin")
    return admin


@pytest.fixture
def user_account(user):
    """Account for regular user."""
    return Account.objects.create(user=user, display_name="User Account", legal_form="micro", is_active=True)


@pytest.mark.django_db
class TestAccountList:
    """Tests for GET /api/user/accounts/"""

    def test_list_requires_auth(self, api_client):
        """Unauthenticated request returns 401."""
        response = api_client.get("/api/user/accounts/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_sees_own_accounts_only(self, api_client, user, user_account):
        """User lists only their accounts."""
        # Create another user's account
        other_user = User.objects.create_user(email="other@test.com", password="pass")
        Account.objects.create(user=other_user, display_name="Other Account", legal_form="eurl")

        api_client.force_authenticate(user=user)
        response = api_client.get("/api/user/accounts/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["display_name"] == "User Account"

    def test_admin_sees_all_accounts(self, api_client, admin_user, user_account):
        """Admin lists all accounts."""
        Account.objects.create(user=admin_user, display_name="Admin Account", legal_form="sasu")

        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/user/accounts/")

        assert response.status_code == status.HTTP_200_OK

        assert isinstance(response.data, list)
        assert len(response.data) >= 2

        ids = {item["id"] for item in response.data}
        assert user_account.id in ids


@pytest.mark.django_db
class TestAccountCreate:
    """Tests for POST /api/user/accounts/"""

    def test_create_account_success(self, api_client, user):
        """User creates new account."""
        api_client.force_authenticate(user=user)

        data = {
            "display_name": "New Company",
            "legal_form": "eurl",
            "legal_id": "12345678901234",
        }
        response = api_client.post("/api/user/accounts/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["display_name"] == "New Company"
        assert response.data["legal_form"] == "eurl"
        assert response.data["is_active"] is True

    def test_create_duplicate_name_fails(self, api_client, user, user_account):
        """Duplicate name for same user returns 400."""
        api_client.force_authenticate(user=user)

        data = {
            "display_name": "User Account",  # Duplicate
            "legal_form": "micro",
        }
        response = api_client.post("/api/user/accounts/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data


@pytest.mark.django_db
class TestAccountRetrieve:
    """Tests for GET /api/user/accounts/{id}/"""

    def test_retrieve_own_account(self, api_client, user, user_account):
        """User retrieves their account."""
        api_client.force_authenticate(user=user)

        response = api_client.get(f"/api/user/accounts/{user_account.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == user_account.id
        assert response.data["display_name"] == "User Account"

    def test_retrieve_other_account_forbidden(self, api_client, user):
        """User cannot retrieve another user's account."""
        other_user = User.objects.create_user(email="other@test.com", password="pass")
        other_account = Account.objects.create(user=other_user, display_name="Other Account", legal_form="micro")

        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/user/accounts/{other_account.id}/")

        # ModelViewSet + IsAccountOwner should return 403
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_retrieve_any_account(self, api_client, admin_user, user_account):
        """Admin retrieves any account."""
        api_client.force_authenticate(user=admin_user)

        response = api_client.get(f"/api/user/accounts/{user_account.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == user_account.id


@pytest.mark.django_db
class TestAccountUpdate:
    """Tests for PUT /api/user/accounts/{id}/"""

    def test_update_account_success(self, api_client, user, user_account):
        """User updates their account."""
        api_client.force_authenticate(user=user)

        data = {
            "display_name": "Updated Name",
            "legal_form": "eurl",
        }
        response = api_client.put(f"/api/user/accounts/{user_account.id}/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["display_name"] == "Updated Name"

        # Verify in DB
        user_account.refresh_from_db()
        assert user_account.display_name == "Updated Name"

    def test_update_other_account_forbidden(self, api_client, user):
        """User cannot update another user's account."""
        other_user = User.objects.create_user(email="other@test.com", password="pass")
        other_account = Account.objects.create(user=other_user, display_name="Other Account", legal_form="micro")

        api_client.force_authenticate(user=user)
        data = {"display_name": "Hacked Name", "legal_form": "eurl"}
        response = api_client.put(f"/api/user/accounts/{other_account.id}/", data)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAccountPartialUpdate:
    """Tests for PATCH /api/user/accounts/{id}/"""

    def test_patch_account_partial_fields(self, api_client, user, user_account):
        """PATCH updates only provided fields."""
        api_client.force_authenticate(user=user)

        data = {"display_name": "Patched Name"}  # Only display_name
        response = api_client.patch(f"/api/user/accounts/{user_account.id}/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["display_name"] == "Patched Name"
        assert response.data["legal_form"] == "micro"  # Unchanged


@pytest.mark.django_db
class TestAccountDelete:
    """Tests for DELETE /api/user/accounts/{id}/"""

    def test_delete_account_soft_delete(self, api_client, user, user_account):
        """DELETE soft-deletes (deactivates) account."""
        api_client.force_authenticate(user=user)

        response = api_client.delete(f"/api/user/accounts/{user_account.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify soft delete (still in DB but inactive)
        user_account.refresh_from_db()
        assert user_account.is_active is False

    def test_delete_other_account_forbidden(self, api_client, user):
        """User cannot delete another user's account."""
        other_user = User.objects.create_user(email="other@test.com", password="pass")
        other_account = Account.objects.create(user=other_user, display_name="Other Account", legal_form="micro")

        api_client.force_authenticate(user=user)
        response = api_client.delete(f"/api/user/accounts/{other_account.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Verify not deleted
        other_account.refresh_from_db()
        assert other_account.is_active is True


@pytest.mark.django_db
class TestAccountMiddleware:
    """Tests for X-Account-Id middleware behavior."""

    def test_middleware_sets_account_from_header(self, api_client, user, user_account):
        """Middleware loads account from X-Account-Id header."""
        api_client.force_authenticate(user=user)

        # This would be tested via a view that uses request.account
        # For now, verify header is accepted
        response = api_client.get("/api/user/accounts/", HTTP_X_ACCOUNT_ID=str(user_account.id))

        assert response.status_code == status.HTTP_200_OK

    def test_middleware_fallback_without_header(self, api_client, user, user_account):
        """Middleware falls back to first account if no header."""
        api_client.force_authenticate(user=user)

        response = api_client.get("/api/user/accounts/")

        assert response.status_code == status.HTTP_200_OK
