# apps/catalog/tests/domain/test_prestation_calculator.py
"""
Tests unitaires pour le service de calcul.
"""

from decimal import Decimal

import pytest

from apps.catalog.domain.services.prestation_calculator import PrestationCalculator


class TestPrestationCalculator:
    """Tests du service de calcul pur."""

    def test_cents_to_euros(self):
        """Test conversion centimes -> euros."""
        assert PrestationCalculator.cents_to_euros(120000) == Decimal("1200.00")
        assert PrestationCalculator.cents_to_euros(0) == Decimal("0")
        assert PrestationCalculator.cents_to_euros(99) == Decimal("0.99")

    def test_euros_to_cents(self):
        """Test conversion euros -> centimes."""
        assert PrestationCalculator.euros_to_cents(Decimal("1200.00")) == 120000
        assert PrestationCalculator.euros_to_cents(Decimal("0")) == 0
        assert PrestationCalculator.euros_to_cents(Decimal("0.99")) == 99

    def test_format_rate_display(self):
        """Test formatage pour affichage."""
        assert PrestationCalculator.format_rate_display(120000) == "1200.00"
        assert PrestationCalculator.format_rate_display(0) == "0.00"
        assert PrestationCalculator.format_rate_display(99) == "0.99"

    def test_calculate_total_days(self):
        """Test calcul du total de jours-homme."""
        prestations = [
            {"weight_days": 5},
            {"weight_days": 3},
            {"weight_days": 10},
        ]

        total = PrestationCalculator.calculate_total_days(prestations)
        assert total == 18

    def test_calculate_total_days_empty(self):
        """Test calcul avec liste vide."""
        assert PrestationCalculator.calculate_total_days([]) == 0

    def test_calculate_total_days_missing_key(self):
        """Test calcul avec clé manquante."""
        prestations = [
            {"weight_days": 5},
            {"name": "Test"},  # pas de weight_days
        ]

        total = PrestationCalculator.calculate_total_days(prestations)
        assert total == 5

    def test_calculate_total_rate_cents(self):
        """Test calcul du total en centimes."""
        prestations = [
            {"default_rate_cents": 120000},
            {"default_rate_cents": 50000},
            {"default_rate_cents": 30000},
        ]

        total = PrestationCalculator.calculate_total_rate_cents(prestations)
        assert total == 200000

    def test_group_by_area(self):
        """Test regroupement par area."""
        prestations = [
            {"area_id": 1, "name": "Prest 1"},
            {"area_id": 2, "name": "Prest 2"},
            {"area_id": 1, "name": "Prest 3"},
        ]

        grouped = PrestationCalculator.group_by_area(prestations)

        assert len(grouped) == 2
        assert len(grouped[1]) == 2
        assert len(grouped[2]) == 1
        assert grouped[1][0]["name"] == "Prest 1"
        assert grouped[1][1]["name"] == "Prest 3"

    def test_group_by_area_empty(self):
        """Test regroupement avec liste vide."""
        grouped = PrestationCalculator.group_by_area
