# apps/core/fields.py
"""
Custom encrypted fields for RGPD compliance.

Uses Fernet symmetric encryption (cryptography library) to encrypt sensitive data at rest.
Encryption key configured via FIELD_ENCRYPTION_KEY environment variable.

AIDEV-NOTE: These fields automatically encrypt data before saving to database
and decrypt when retrieving. The database stores base64-encoded ciphertext.

Security requirements (SPECIFICATIONS_RGPD.md Section 3.1.1):
- Encryption key must be 32-byte Fernet key (base64-encoded)
- Key rotation requires re-encrypting all data
- Lost keys = permanent data loss
- Production: Use AWS Secrets Manager for key storage

@author: @Bertrand2808
@since: 2025-12-11
@version: 1.0
"""
import base64
from typing import Any, Optional

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


def get_fernet_key() -> bytes:
    """
    Get Fernet encryption key from settings.

    Returns:
        bytes: 32-byte Fernet key

    Raises:
        ImproperlyConfigured: If FIELD_ENCRYPTION_KEY is not set
    """
    key = getattr(settings, "FIELD_ENCRYPTION_KEY", None)
    if not key:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY must be set in settings. "
            'Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )
    if isinstance(key, str):
        key = key.encode()
    return key


def encrypt_value(value: str) -> str:
    """
    Encrypt a string value using Fernet.

    Args:
        value: Plaintext string to encrypt

    Returns:
        str: Base64-encoded ciphertext

    AIDEV-NOTE: Empty strings are stored as empty strings (not encrypted)
    to preserve NULL/blank semantics in database queries.
    """
    if not value:
        return value

    fernet = Fernet(get_fernet_key())
    encrypted_bytes = fernet.encrypt(value.encode())
    return encrypted_bytes.decode()


def decrypt_value(value: str) -> str:
    """
    Decrypt a Fernet-encrypted string.

    Args:
        value: Base64-encoded ciphertext

    Returns:
        str: Decrypted plaintext

    AIDEV-NOTE: Empty strings are returned as-is without decryption.
    """
    if not value:
        return value

    fernet = Fernet(get_fernet_key())
    decrypted_bytes = fernet.decrypt(value.encode())
    return decrypted_bytes.decode()


class EncryptedFieldMixin:
    """
    Mixin for Django fields that provides transparent encryption/decryption.

    Database storage: TEXT column with base64-encoded ciphertext
    Python access: Plaintext string (automatically decrypted)
    """

    def from_db_value(self, value: Optional[str], expression, connection) -> Optional[str]:
        """Decrypt value when loading from database."""
        if value is None:
            return value
        return decrypt_value(value)

    def to_python(self, value: Optional[str]) -> Optional[str]:
        """Convert value to Python string (decrypt if needed)."""
        if value is None or value == "":
            return value
        # If value is already decrypted (from form), return as-is
        # If value is encrypted (from DB), decrypt it
        try:
            # Test if it's encrypted by attempting to decrypt
            return decrypt_value(value)
        except Exception:
            # If decryption fails, assume it's already plaintext
            return value

    def get_prep_value(self, value: Optional[str]) -> Optional[str]:
        """Encrypt value before saving to database."""
        if value is None or value == "":
            return value
        return encrypt_value(value)


class EncryptedCharField(EncryptedFieldMixin, models.TextField):
    """
    Encrypted CharField that stores data as encrypted text in database.

    Usage:
        phone = EncryptedCharField(max_length=64, blank=True)

    Database: TEXT column (stores base64-encoded ciphertext)
    Python: str (automatically encrypted/decrypted)

    AIDEV-NOTE: Uses TextField as base to store variable-length ciphertext.
    The max_length parameter is for validation only, not database constraint.
    """

    description = "Encrypted text field"

    def __init__(self, *args, **kwargs):
        # Extract max_length for validation, but use TextField storage
        self.max_length = kwargs.pop("max_length", None)
        kwargs.pop("max_length", None)  # Remove max_length from kwargs
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.max_length is not None:
            kwargs["max_length"] = self.max_length
        return name, path, args, kwargs


class EncryptedEmailField(EncryptedFieldMixin, models.TextField):
    """
    Encrypted EmailField that stores encrypted email addresses.

    Usage:
        email = EncryptedEmailField(blank=True)

    Database: TEXT column (stores base64-encoded ciphertext)
    Python: str (automatically encrypted/decrypted)

    AIDEV-NOTE: Email validation is performed before encryption.
    Queries by email require exact match (cannot use __icontains).
    """

    description = "Encrypted email field"

    def __init__(self, *args, **kwargs):
        kwargs.pop("max_length", None)  # Remove max_length if provided
        super().__init__(*args, **kwargs)
