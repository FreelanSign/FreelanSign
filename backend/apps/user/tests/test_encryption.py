# apps/user/tests/test_encryption.py
"""
Unit tests for encrypted fields in Account model.

Tests RGPD compliance encryption for sensitive identification data:
- Account.legal_id (SIRET - EncryptedCharField)

Verifies:
1. Data is encrypted in database (ciphertext storage)
2. Data is decrypted when accessed (transparent to application)
3. CRUD operations work correctly with encrypted fields
4. Null/empty values are handled properly

@author: @Bertrand2808
@since: 2025-12-11
@version: 1.0
"""
import pytest
from django.db import connection

from apps.user.models import User
from apps.user.models.account import Account


@pytest.fixture
def user(db):
    """Create test user."""
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
    )


@pytest.mark.django_db
class TestAccountEncryption:
    """Test Account model field encryption."""

    def test_legal_id_encryption(self, user):
        """Test legal_id (SIRET) field is encrypted in database."""
        # Create account with SIRET
        account = Account.objects.create(
            user=user,
            display_name="Test Account",
            legal_id="12345678901234",  # 14 digits SIRET
        )

        # Verify legal_id is accessible (decrypted)
        assert account.legal_id == "12345678901234"

        # Query database directly to verify encryption
        with connection.cursor() as cursor:
            cursor.execute("SELECT legal_id FROM user_account WHERE id = %s", [account.id])
            row = cursor.fetchone()
            encrypted_value = row[0]

        # Encrypted value should NOT match plaintext
        assert encrypted_value != "12345678901234"
        # Encrypted value should be longer (base64-encoded ciphertext)
        assert len(encrypted_value) > 14

    def test_legal_id_null_value(self, user):
        """Test null legal_id is stored as NULL (not encrypted)."""
        account = Account.objects.create(
            user=user,
            display_name="Test Account",
            legal_id=None,
        )

        # Verify null value remains null
        assert account.legal_id is None

        # Query database directly
        with connection.cursor() as cursor:
            cursor.execute("SELECT legal_id FROM user_account WHERE id = %s", [account.id])
            row = cursor.fetchone()

        # NULL should be stored as NULL
        assert row[0] is None

    def test_legal_id_empty_string(self, user):
        """Test empty string legal_id is stored as empty (not encrypted)."""
        account = Account.objects.create(
            user=user,
            display_name="Test Account",
            legal_id="",
        )

        # Verify empty value remains empty
        assert account.legal_id == ""

        # Query database directly
        with connection.cursor() as cursor:
            cursor.execute("SELECT legal_id FROM user_account WHERE id = %s", [account.id])
            row = cursor.fetchone()

        # Empty string should be stored as empty
        assert row[0] == ""

    def test_update_legal_id(self, user):
        """Test updating legal_id works correctly."""
        account = Account.objects.create(
            user=user,
            display_name="Test Account",
            legal_id="12345678901234",
        )

        # Update legal_id
        account.legal_id = "98765432109876"
        account.save()

        # Reload from database
        account.refresh_from_db()
        assert account.legal_id == "98765432109876"

    def test_query_by_legal_id(self, user):
        """Test querying by encrypted legal_id requires manual iteration."""
        account = Account.objects.create(
            user=user,
            display_name="Account 1",
            legal_id="12345678901234",
        )

        # AIDEV-NOTE: Encrypted fields cannot be queried with filter()
        # Must iterate and compare decrypted values in Python.

        # This will NOT work:
        # accounts = Account.objects.filter(legal_id="12345678901234")

        # Instead, fetch all and filter in Python:
        all_accounts = Account.objects.filter(user=user)
        matching_accounts = [a for a in all_accounts if a.legal_id == "12345678901234"]

        assert len(matching_accounts) == 1
        assert matching_accounts[0].id == account.id

    def test_multiple_accounts_different_encrypted_values(self, user):
        """Test multiple accounts with different legal_ids have different ciphertexts."""
        account1 = Account.objects.create(
            user=user,
            display_name="Account 1",
            legal_id="12345678901234",
        )

        account2 = Account.objects.create(
            user=user,
            display_name="Account 2",
            legal_id="98765432109876",
        )

        # Query database directly for both
        with connection.cursor() as cursor:
            cursor.execute("SELECT legal_id FROM user_account WHERE id IN (%s, %s)", [account1.id, account2.id])
            rows = cursor.fetchall()

        # Both legal_ids should be encrypted differently
        assert rows[0][0] != rows[1][0]
        assert rows[0][0] != "12345678901234"
        assert rows[1][0] != "98765432109876"

    def test_soft_delete_preserves_encrypted_data(self, user):
        """Test soft delete preserves encrypted data for legal archiving."""
        account = Account.objects.create(
            user=user,
            display_name="Test Account",
            legal_id="12345678901234",
        )

        original_id = account.id

        # Soft delete
        account.delete()

        # Query including deleted records
        with connection.cursor() as cursor:
            cursor.execute("SELECT legal_id, is_deleted FROM user_account WHERE id = %s", [original_id])
            row = cursor.fetchone()

        # Data should still be encrypted and marked as deleted
        assert row[0] != "12345678901234"  # Still encrypted
        assert row[1] is True  # Soft deleted
