# apps/user/application/ports/clock.py
"""
Port pour l'abstraction du temps.
Permet de mocker les timestamps dans les tests.
"""

from abc import abstractmethod
from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Interface pour obtenir le temps actuel."""

    @abstractmethod
    def now(self) -> datetime:
        """Retourne la date/heure actuelle."""
        ...
