# apps/client/domain/policies/client_policies.py
from typing import Callable

from apps.client.domain.errors import ClientAlreadyExistsError, ClientInvalidNameError, ClientNotFoundError


def ensure_name_valid(name: str) -> str:
    v = (name or "").strip()
    if not v:
        raise ClientInvalidNameError(name)
    return v


def normalize_email(email: str | None) -> str | None:
    if not email:
        return None
    e = email.strip().lower()
    # (ici on reste simple; la validation champistique est côté serializer)
    return e


def ensure_unique_name_within_owner(owner_id: int, name: str, exists_by_owner_name: Callable[[int, str], bool]):
    # exists_by_owner_name(owner_id, name) -> bool
    # L’orchestration la passera depuis l’implémentation repo
    if exists_by_owner_name(owner_id, name):
        raise ClientAlreadyExistsError(name)


def ensure_unique_name_within_account(account_id: int, name: str, exists_by_account_name: Callable[[int, str], bool]):
    # Phase 5: Check uniqueness within account
    if exists_by_account_name(account_id, name):
        raise ClientAlreadyExistsError(name)


def ensure_client_exists(client_id: str):
    if not client_id:
        raise ClientNotFoundError(client_id)


def normalize_phone_number(phone: str | None) -> str | None:
    if not phone:
        return None
    p = phone.strip()
    # (ici on reste simple; la validation champistique est côté serializer)
    return p


# ISO 3166-1 alpha-2 country codes whitelist
ALLOWED_COUNTRY_CODES = {
    "FR",
    "BE",
    "CH",
    "LU",
    "DE",
    "ES",
    "IT",
    "PT",
    "NL",
    "GB",
    "US",
    "CA",
    "AT",
    "DK",
    "SE",
    "NO",
    "FI",
    "IE",
    "PL",
    "CZ",
}


def validate_country_code(country: str | None) -> str:
    """Validate ISO 3166-1 alpha-2 country code against whitelist.

    Args:
        country: Country code (2-letter ISO code)

    Returns:
        Validated and normalized country code (uppercase)

    Raises:
        ValueError: If country code is invalid or not in whitelist
    """
    if not country:
        return ""
    code = country.strip().upper()
    if len(code) != 2:
        raise ValueError(f"Invalid country code length: {code}")
    if code not in ALLOWED_COUNTRY_CODES:
        raise ValueError(f"Unsupported country code: {code}")
    return code
