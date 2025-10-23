# apps/quote/application/ports/client_repository.py
from __future__ import annotations

from typing import Any, Protocol


class ClientRepository(Protocol):
    """
    Access to clients to check/patch allowed fields.
    """

    def get(self, *, client_id, requester_id) -> Any: ...
    def patch_owned_fields(self, *, client_id, requester_id, changes: dict) -> None: ...
    def get_country(self, *, client_id) -> str | None: ...
