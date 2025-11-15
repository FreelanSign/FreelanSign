# backend/apps/email/application/ports/quote_repository.py

from abc import ABC, abstractmethod
from uuid import UUID

from apps.quote.models import Quote


class QuoteRepository(ABC):
    """
    Port interface for accessing Quote aggregate.

    Rationale:
    - Inversion of control: the use case does not depend on Django ORM.
    - Aligns with Hexagonal Architecture: this is a primary port.
    - Enables mocking in tests and adapter substitution (e.g. caching, fallback).

    Implemented by infrastructure adapter (e.g. DjangoQuoteRepository).
    """

    @abstractmethod
    def get_by_id(self, quote_id: UUID) -> Quote:
        """
        Retrieve a quote by ID or raise QuoteNotFound.

        Must ensure ownership and validation are handled outside this layer.
        """
        raise NotImplementedError
