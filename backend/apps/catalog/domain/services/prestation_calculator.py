# apps/catalog/domain/services/prestation_calculator.py
"""
Services de calcul purs pour les prestations.
"""

from decimal import Decimal
from typing import Any, Dict, List


class PrestationCalculator:
    """Service de calcul pur pour les prestations."""

    @staticmethod
    def cents_to_euros(cents: int) -> Decimal:
        """Convertit des centimes en euros (Decimal)."""
        return Decimal(cents) / Decimal(100)

    @staticmethod
    def euros_to_cents(euros: Decimal) -> int:
        """Convertit des euros (Decimal) en centimes."""
        return int(euros * 100)

    @staticmethod
    def format_rate_display(rate_cents: int) -> str:
        """Formate un tarif pour l'affichage (ex: "1200.00")."""
        euros = PrestationCalculator.cents_to_euros(rate_cents)
        return f"{euros:.2f}"

    @staticmethod
    def calculate_total_days(prestations: List[Dict[str, Any]]) -> int:
        """
        Calcule le total de jours-homme pour une liste de prestations.

        Args:
            prestations: Liste de dicts avec clé 'weight_days'

        Returns:
            Total des jours-homme
        """
        return sum(p.get("weight_days", 0) for p in prestations)

    @staticmethod
    def calculate_total_rate_cents(prestations: List[Dict[str, Any]]) -> int:
        """
        Calcule le montant total en centimes.

        Args:
            prestations: Liste de dicts avec clé 'default_rate_cents'

        Returns:
            Total en centimes
        """
        return sum(p.get("default_rate_cents", 0) for p in prestations)

    @staticmethod
    def group_by_area(prestations: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """
        Regroupe les prestations par area_id.

        Args:
            prestations: Liste de prestations (dicts avec 'area_id')

        Returns:
            Dict {area_id: [prestations]}
        """
        grouped: Dict[int, List[Dict[str, Any]]] = {}

        for prest in prestations:
            area_id = prest.get("area_id")
            if area_id is not None:
                if area_id not in grouped:
                    grouped[area_id] = []
                grouped[area_id].append(prest)

        return grouped
