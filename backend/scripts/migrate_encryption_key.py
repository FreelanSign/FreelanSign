#!/usr/bin/env python
"""
Migration script to re-encrypt Account.legal_id with a new encryption key.

Usage:
    1. Set OLD_FIELD_ENCRYPTION_KEY environment variable to the old key
    2. Set FIELD_ENCRYPTION_KEY environment variable to the new key
    3. Run: python manage.py shell < scripts/migrate_encryption_key.py

AIDEV-NOTE: This script handles the cryptography.fernet.InvalidToken error
by temporarily using the old key to decrypt, then re-encrypting with new key.

@author: @Bertrand2808
@date: 2026-01-13
"""

import os
import sys

from cryptography.fernet import Fernet

# Get old and new keys from environment
OLD_KEY = os.environ.get("OLD_FIELD_ENCRYPTION_KEY")
NEW_KEY = os.environ.get("FIELD_ENCRYPTION_KEY")

if not OLD_KEY or not NEW_KEY:
    print("ERROR: Both OLD_FIELD_ENCRYPTION_KEY and FIELD_ENCRYPTION_KEY must be set")
    sys.exit(1)

print(f"Starting encryption key migration...")
print(f"Old key: {OLD_KEY[:20]}...")
print(f"New key: {NEW_KEY[:20]}...")

# Get Account model
from apps.user.models import Account

# Create Fernet instances
old_fernet = Fernet(OLD_KEY.encode())
new_fernet = Fernet(NEW_KEY.encode())

# Process all accounts
accounts = Account.objects.all()
total = accounts.count()
print(f"\nFound {total} accounts to process")

migrated = 0
skipped = 0
errors = 0

for account in accounts:
    try:
        # Get the raw encrypted value from database
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT legal_id FROM user_account WHERE id = %s", [account.id])
            row = cursor.fetchone()
            encrypted_value = row[0] if row else None

        # Skip if empty
        if not encrypted_value:
            print(f"  Account {account.id}: No legal_id, skipping")
            skipped += 1
            continue

        # Decrypt with old key
        decrypted = old_fernet.decrypt(encrypted_value.encode()).decode()

        # Re-encrypt with new key
        new_encrypted = new_fernet.encrypt(decrypted.encode()).decode()

        # Update database directly
        with connection.cursor() as cursor:
            cursor.execute("UPDATE user_account SET legal_id = %s WHERE id = %s", [new_encrypted, account.id])

        print(f"  Account {account.id}: Migrated successfully")
        migrated += 1

    except Exception as e:
        print(f"  Account {account.id}: ERROR - {e}")
        errors += 1

print(f"\n=== Migration Complete ===")
print(f"Total: {total}")
print(f"Migrated: {migrated}")
print(f"Skipped (empty): {skipped}")
print(f"Errors: {errors}")

if errors > 0:
    print(f"\nWARNING: {errors} accounts failed to migrate")
    sys.exit(1)
else:
    print("\nSUCCESS: All accounts migrated successfully")
