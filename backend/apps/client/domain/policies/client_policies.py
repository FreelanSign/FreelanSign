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


def ensure_client_exists(client_id: str):
    if not client_id:
        raise ClientNotFoundError(client_id)


def normalize_phone_number(phone: str | None) -> str | None:
    if not phone:
        return None
    p = phone.strip()
    # (ici on reste simple; la validation champistique est côté serializer)
    return p
