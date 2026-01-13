import os
import sys

import django

"""
Clear all encrypted fields to fix InvalidToken errors after key loss.

Usage:
    Local:  python scripts/clear_encrypted_fields.py
    Docker: docker exec -it freelansign_backend_prod python manage.py shell < scripts/clear_encrypted_fields.py

AIDEV-NOTE: This script clears all encrypted fields that were encrypted with a lost key.
Users will need to re-enter this data through the app.

@author: @Bertrand2808
@date: 2026-01-13
"""

# Setup Django environment if run directly
if __name__ == "__main__":
    # Add the backend directory to sys.path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    sys.path.append(project_root)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

from django.db import connection

print("=== Clearing Encrypted Fields ===\n")

# Clear Account.legal_id (accepts NULL)
print("1. Clearing Account.legal_id...")
with connection.cursor() as cursor:
    cursor.execute("UPDATE user_account SET legal_id = NULL WHERE legal_id IS NOT NULL")
    count = cursor.rowcount
    print(f"   ✓ Cleared {count} accounts\n")

# Clear Client encrypted fields (use empty string '' for NOT NULL fields)
print("2. Clearing Client encrypted fields...")
with connection.cursor() as cursor:
    cursor.execute(
        """
        UPDATE client_client SET
            email = '',
            phone = '',
            address_line1 = '',
            address_line2 = '',
            city = '',
            postal_code = '',
            company = '',
            vat_number = ''
        WHERE email != ''
           OR phone != ''
           OR address_line1 != ''
           OR address_line2 != ''
           OR city != ''
           OR postal_code != ''
           OR company != ''
           OR vat_number != ''
    """
    )
    count = cursor.rowcount
    print(f"   ✓ Cleared {count} clients\n")

print("=== Complete ===")
print("All encrypted fields cleared. Restart the application server.")
print("\nUsers will need to re-enter:")
print("  - Account: SIRET")
print("  - Clients: Email, phone, address, VAT number")
