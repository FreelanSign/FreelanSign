# apps/quote/application/ports/reference_gen.py
from __future__ import annotations

from datetime import date
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


class QuoteReferenceGeneratorPort(Protocol):
    """
    Generate a next reference for a quote.
    """

    def next_reference(self, *, owner_id: str | int, when: date) -> str:
        """
        :param owner_id: The ID of the owner.
        :param when: The issue date of the quote.
        :returns: A readable unique reference.
        """
        ...
