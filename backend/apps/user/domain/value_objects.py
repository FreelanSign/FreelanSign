# apps/user/domain/value_objects.py
"""
Value Objects du domaine user.
Objets purs, sans dépendance Django.
"""

from enum import Enum


class LegalForm(str, Enum):
    """Formes juridiques pour les freelances français."""

    MICRO = "micro"
    EIRL = "eirl"
    EURL = "eurl"
    SASU = "sasu"
    OTHER = "other"
