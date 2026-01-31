# apps/quote/application/ports/quote_repository_extensions.py
"""Extensions to QuoteRepository port for quota checks."""

from abc import abstractmethod
from datetime import datetime
from typing import Protocol


class QuoteRepositoryQuotaExt(Protocol):
    """
    Extension protocol for QuoteRepository to support quota checks.

    This avoids modifying the existing QuoteRepository port.
    """

    @abstractmethod
    def count_by_account_since(self, account_id: int, since: datetime) -> int:
        """
        Count quotes for account created since given datetime.

        Args:
            account_id: Account ID
            since: Start datetime (typically start of month)

        Returns:
            Number of quotes created since given date
        """
        ...
