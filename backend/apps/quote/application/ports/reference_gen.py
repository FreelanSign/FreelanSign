# apps/quote/application/ports/reference_gen.py
from __future__ import annotations

from typing import Protocol


class ReferenceGenerator(Protocol):
    """
    Generate a readable unique reference per owner.
    """

    def new(self, *, owner_id) -> str:
        """
        :param owner_id: The ID of the owner.
        :returns: A readable unique reference.
        """
        ...
