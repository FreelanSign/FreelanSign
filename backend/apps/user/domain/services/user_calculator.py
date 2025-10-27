# apps/user/domain/services/user_calculator.py
"""
Services de calcul purs pour les utilisateurs.
"""
from decimal import Decimal


class UserCalculator:
    """Service de calcul pur pour les utilisateurs."""

    @staticmethod
    def cents_to_euros(cents: int) -> Decimal:
        """Convertit des centimes en euros (Decimal)."""
        return Decimal(cents) / Decimal(100)

    @staticmethod
    def euros_to_cents(euros: Decimal) -> int:
        """Convertit des euros (Decimal) en centimes."""
        return int(euros * 100)

    @staticmethod
    def format_tjm_display(tjm_cents: int) -> str:
        """Formate un TJM pour l'affichage (ex: "500.00")."""
        euros = UserCalculator.cents_to_euros(tjm_cents)
        return f"{euros:.2f}"

    @staticmethod
    def calculate_project_cost(tjm_cents: int, days: int) -> int:
        """
        Calcule le coût d'un projet en centimes.

        Args:
            tjm_cents: TJM en centimes
            days: Nombre de jours

        Returns:
            Coût total en centimes
        """
        return tjm_cents * days

    @staticmethod
    def format_full_name(first_name: str, last_name: str) -> str:
        """
        Formate un nom complet.

        Args:
            first_name: Prénom
            last_name: Nom

        Returns:
            Nom complet formaté
        """
        parts = []
        if first_name:
            parts.append(first_name.strip())
        if last_name:
            parts.append(last_name.strip())

        return " ".join(parts) if parts else ""

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        Normalise un numéro de téléphone.
        Supprime les espaces et caractères superflus.

        Args:
            phone: Numéro de téléphone brut

        Returns:
            Numéro normalisé
        """
        if not phone:
            return ""

        # Garder seulement +, chiffres et espaces
        normalized = "".join(c for c in phone if c.isdigit() or c in ["+", " "])

        return normalized.strip()
