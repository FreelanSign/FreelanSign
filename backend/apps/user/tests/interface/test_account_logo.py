# apps/user/tests/interface/test_account_logo.py
"""
TDD tests for Account Logo Upload feature.

Tests written BEFORE implementation to ensure:
1. Logo uploads use 'logos' bucket (not 'avatars')
2. Permission: only account owner can upload
3. API returns logo_url on success

@author: Assistant
@since: 2026-01-16
"""

from io import BytesIO
from unittest.mock import MagicMock, patch

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
def other_user():
    """Another user for permission tests."""
    return User.objects.create_user(email="other@test.com", password="testpass123")


@pytest.fixture
def user_account(user):
    """Account for regular user."""
    return Account.objects.create(
        user=user,
        display_name="Test Account",
        legal_form="micro",
        is_active=True,
    )


@pytest.fixture
def other_account(other_user):
    """Account for other user."""
    return Account.objects.create(
        user=other_user,
        display_name="Other Account",
        legal_form="eurl",
        is_active=True,
    )


@pytest.fixture
def fake_image():
    """Create a fake image file for upload tests."""
    # 1x1 red PNG
    png_data = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03"
        b"\x00\x01\x00\x05\xfe\xd4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return BytesIO(png_data)


@pytest.mark.django_db
class TestAccountLogoUpload:
    """Tests for POST /api/user/accounts/{id}/logo/"""

    def test_upload_logo_requires_auth(self, api_client, user_account, fake_image):
        """Unauthenticated request returns 401."""
        response = api_client.post(
            f"/api/user/accounts/{user_account.id}/logo/",
            {"file": fake_image},
            format="multipart",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_logo_to_other_account_forbidden(self, api_client, user, other_account, fake_image):
        """User cannot upload logo to another user's account."""
        api_client.force_authenticate(user=user)

        fake_image.name = "logo.png"
        response = api_client.post(
            f"/api/user/accounts/{other_account.id}/logo/",
            {"file": fake_image},
            format="multipart",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("apps.user.adapters.storage.supabase_storage.get_storage_adapter")
    def test_upload_logo_to_own_account_success(self, mock_get_adapter, api_client, user, user_account, fake_image):
        """User can upload logo to their own account."""
        # Mock storage adapter
        mock_adapter = MagicMock()
        mock_adapter.upload_logo.return_value = "https://example.com/logos/test.png"
        mock_get_adapter.return_value = mock_adapter

        api_client.force_authenticate(user=user)

        fake_image.name = "logo.png"
        response = api_client.post(
            f"/api/user/accounts/{user_account.id}/logo/",
            {"file": fake_image},
            format="multipart",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "logo_url" in response.data
        assert response.data["logo_url"] == "https://example.com/logos/test.png"

        # Verify adapter was called with correct account_id
        mock_adapter.upload_logo.assert_called_once()
        call_args = mock_adapter.upload_logo.call_args
        assert call_args.kwargs.get("account_id") == user_account.id

    @patch("apps.user.adapters.storage.supabase_storage.get_storage_adapter")
    def test_upload_logo_uses_logos_bucket(self, mock_get_adapter, api_client, user, user_account, fake_image):
        """Verify upload_logo is called, not upload_avatar."""
        mock_adapter = MagicMock()
        mock_adapter.upload_logo.return_value = "https://example.com/logos/test.png"
        mock_get_adapter.return_value = mock_adapter

        api_client.force_authenticate(user=user)

        fake_image.name = "logo.png"
        api_client.post(
            f"/api/user/accounts/{user_account.id}/logo/",
            {"file": fake_image},
            format="multipart",
        )

        # CRITICAL: Must call upload_logo, NOT upload_avatar
        mock_adapter.upload_logo.assert_called_once()
        mock_adapter.upload_avatar.assert_not_called()

    def test_upload_logo_no_file_returns_400(self, api_client, user, user_account):
        """Request without file returns 400."""
        api_client.force_authenticate(user=user)

        response = api_client.post(
            f"/api/user/accounts/{user_account.id}/logo/",
            {},
            format="multipart",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data


@pytest.mark.django_db
class TestAccountLogoInResponse:
    """Tests for logo_url in account responses."""

    def test_logo_url_in_account_retrieve(self, api_client, user, user_account):
        """GET /api/user/accounts/{id}/ includes logo_url."""
        # Set logo_url directly
        user_account.logo_url = "https://example.com/logos/existing.png"
        user_account.save()

        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/user/accounts/{user_account.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert "logo_url" in response.data
        assert response.data["logo_url"] == "https://example.com/logos/existing.png"

    def test_logo_url_null_when_not_set(self, api_client, user, user_account):
        """logo_url is null when not set."""
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/user/accounts/{user_account.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert "logo_url" in response.data
        assert response.data["logo_url"] is None
