#!/usr/bin/env python
"""
Migrate plaintext data to encrypted format.

Run with: python manage.py shell < tools/migrate_encrypt_data.py

AIDEV-NOTE: This script encrypts existing plaintext data in the database.
Run once after adding EncryptedField to models.

@author: @Bertrand2808
@since: 2025-12-12
"""
import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
django.setup()

from cryptography.fernet import InvalidToken
from django.db import connection

from apps.core.fields import encrypt_value


def is_encrypted(value):
    """Check if value is already encrypted."""
    if not value:
        return True  # Empty = no need to encrypt
    try:
        from apps.core.fields import decrypt_value

        decrypt_value(value)
        return True  # Decryption succeeded = already encrypted
    except (InvalidToken, Exception):
        return False  # Decryption failed = plaintext


def migrate_table(table_name, encrypted_fields):
    """Migrate plaintext fields to encrypted in a table."""
    print(f"\n[{table_name}] Starting migration...")

    with connection.cursor() as cursor:
        # Get all rows
        cursor.execute(f"SELECT id, {', '.join(encrypted_fields)} FROM {table_name}")
        rows = cursor.fetchall()

        if not rows:
            print(f"[{table_name}] No rows found.")
            return

        print(f"[{table_name}] Found {len(rows)} rows.")

        updated = 0
        for row in rows:
            row_id = row[0]
            values = row[1:]

            # Check if any field needs encryption
            needs_update = False
            encrypted_values = []

            for i, value in enumerate(values):
                if value and not is_encrypted(value):
                    encrypted_values.append(encrypt_value(value))
                    needs_update = True
                else:
                    encrypted_values.append(value)

            if needs_update:
                # Build UPDATE query
                set_clause = ", ".join([f"{field} = %s" for field in encrypted_fields])
                cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE id = %s", [*encrypted_values, row_id])
                updated += 1
                print(f"[{table_name}] Updated row {row_id}")

        print(f"[{table_name}] Migration complete. Updated {updated}/{len(rows)} rows.")


if __name__ == "__main__":
    print("=== Encrypting existing plaintext data ===")

    # Migrate Account.legal_id
    migrate_table("user_account", ["legal_id"])

    # Migrate Client fields
    migrate_table("client_client", ["email", "phone", "vat_number"])

    print("\n=== Migration complete ===")
