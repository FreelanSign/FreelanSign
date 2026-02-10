# apps/client/tests/test_encryption.py
"""
Unit tests for encrypted fields in Client model.

Tests RGPD compliance encryption for sensitive personal data:
- Client.email (EncryptedEmailField)
- Client.phone (EncryptedCharField)
- Client.vat_number (EncryptedCharField)

Verifies:
1. Data is encrypted in database (ciphertext storage)
2. Data is decrypted when accessed (transparent to application)
3. CRUD operations work correctly with encrypted fields
4. Empty/null values are handled properly

@author: @Bertrand2808
@since: 2025-12-11
@version: 1.0
"""

import pytest
from django.db import connection

from apps.client.models import Client
from apps.user.models import User
from apps.user.models.account import Account


@pytest.fixture
def user(db):
    """Create test user."""
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def account(db, user):
    """Create test account."""
    return Account.objects.create(
        user=user,
        display_name="Test Account",
    )


@pytest.mark.django_db
class TestClientEncryption:
    """Test Client model field encryption."""

    def test_email_encryption(self, account):
        """Test email field is encrypted in database."""
        # Create client with email
        client = Client.objects.create(
            owner=account.user,
            account=account,
            name="Test Client",
            email="client@example.com",
        )

        # Verify email is accessible (decrypted)
        assert client.email == "client@example.com"

        # Query database directly to verify encryption
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM client_client WHERE id = %s", [str(client.id)])
            row = cursor.fetchone()
            encrypted_value = row[0]

        # Encrypted value should NOT match plaintext
        assert encrypted_value != "client@example.com"
        # Encrypted value should be base64-like (contains alphanumeric + special chars)
        assert len(encrypted_value) > len("client@example.com")

    def test_phone_encryption(self, account):
        """Test phone field is encrypted in database."""
        client = Client.objects.create(
            owner=account.user,
            account=account,
            name="Test Client",
            phone="+33612345678",
        )

        # Verify phone is accessible (decrypted)
        assert client.phone == "+33612345678"

        # Query database directly
        with connection.cursor() as cursor:
            cursor.execute("SELECT phone FROM client_client WHERE id = %s", [str(client.id)])
            row = cursor.fetchone()
            encrypted_value = row[0]

        # Encrypted value should NOT match plaintext
        assert encrypted_value != "+33612345678"

    def test_vat_number_encryption(self, account):
        """Test vat_number field is encrypted in database."""
        client = Client.objects.create(
            owner=account.user,
            account=account,
            name="Test Client",
            vat_number="FR12345678901",
        )

        # Verify vat_number is accessible (decrypted)
        assert client.vat_number == "FR12345678901"

        # Query database directly
        with connection.cursor() as cursor:
            cursor.execute("SELECT vat_number FROM client_client WHERE id = %s", [str(client.id)])
            row = cursor.fetchone()
            encrypted_value = row[0]

        # Encrypted value should NOT match plaintext
        assert encrypted_value != "FR12345678901"

    def test_empty_values_not_encrypted(self, account):
        """Test empty/blank values are stored as empty (not encrypted)."""
        client = Client.objects.create(
            owner=account.user,
            account=account,
            name="Test Client",
            email="",
            phone="",
            vat_number="",
        )

        # Verify empty values remain empty
        assert client.email == ""
        assert client.phone == ""
        assert client.vat_number == ""

        # Query database directly
        with connection.cursor() as cursor:
            cursor.execute("SELECT email, phone, vat_number FROM client_client WHERE id = %s", [str(client.id)])
            row = cursor.fetchone()

        # Empty strings should be stored as empty
        assert row[0] == ""
        assert row[1] == ""
        assert row[2] == ""

    def test_update_encrypted_fields(self, account):
        """Test updating encrypted fields works correctly."""
        client = Client.objects.create(
            owner=account.user,
            account=account,
            name="Test Client",
            email="old@example.com",
        )

        # Update email
        client.email = "new@example.com"
        client.save()

        # Reload from database
        client.refresh_from_db()
        assert client.email == "new@example.com"

    def test_query_by_encrypted_field(self, account):
        """Test querying by encrypted field requires manual iteration."""
        client = Client.objects.create(
            owner=account.user,
            account=account,
            name="Client 1",
            email="test1@example.com",
        )

        # AIDEV-NOTE: Encrypted fields cannot be queried with filter()
        # because the database stores ciphertext, not plaintext.
        # Must iterate and compare decrypted values in Python.

        # This will NOT work (returns empty):
        # clients = Client.objects.filter(email="test1@example.com")

        # Instead, must fetch all and filter in Python:
        all_clients = Client.objects.filter(account=account)
        matching_clients = [c for c in all_clients if c.email == "test1@example.com"]

        assert len(matching_clients) == 1
        assert matching_clients[0].id == client.id

    def test_multiple_clients_different_encrypted_values(self, account):
        """Test multiple clients with different values have different ciphertexts."""
        client1 = Client.objects.create(
            owner=account.user,
            account=account,
            name="Client 1",
            email="client1@example.com",
        )

        client2 = Client.objects.create(
            owner=account.user,
            account=account,
            name="Client 2",
            email="client2@example.com",
        )

        # Query database directly for both
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM client_client WHERE id IN (%s, %s)", [str(client1.id), str(client2.id)])
            rows = cursor.fetchall()

        # Both emails should be encrypted differently
        assert rows[0][0] != rows[1][0]
        assert rows[0][0] != "client1@example.com"
        assert rows[1][0] != "client2@example.com"
