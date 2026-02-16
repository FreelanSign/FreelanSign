#!/usr/bin/env python3
"""
Generate secret keys for Railway deployment.
Run: python scripts/generate_secrets.py
"""

import secrets
from cryptography.fernet import Fernet


def main():
    print("=" * 60)
    print("🔐 FreelanSign - Secret Keys Generator")
    print("=" * 60)
    print()

    # Generate Django SECRET_KEY
    secret_key = secrets.token_urlsafe(50)
    print("📝 Django SECRET_KEY:")
    print(f"   {secret_key}")
    print()

    # Generate FIELD_ENCRYPTION_KEY
    encryption_key = Fernet.generate_key().decode()
    print("🔒 FIELD_ENCRYPTION_KEY (Fernet):")
    print(f"   {encryption_key}")
    print()

    print("=" * 60)
    print("✅ Copy these values to Railway environment variables")
    print("=" * 60)
    print()
    print("Railway → Service Backend → Variables tab:")
    print()
    print(f"SECRET_KEY={secret_key}")
    print(f"FIELD_ENCRYPTION_KEY={encryption_key}")
    print()


if __name__ == "__main__":
    main()
