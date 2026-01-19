"""Unit tests for address formatter domain service."""

import pytest

from apps.legal_terms.domain.services.address_formatter import format_address


class TestFormatAddress:
    """Test address formatting logic."""

    def test_formats_full_address(self):
        """Should format complete address with all fields."""
        result = format_address(
            address_line1="123 Main Street",
            address_line2="Apartment 4B",
            city="Paris",
            postal_code="75001",
            country="fr",
        )
        assert result == "123 Main Street, Apartment 4B, 75001 Paris, FR"

    def test_formats_partial_no_line2(self):
        """Should format address without line2."""
        result = format_address(
            address_line1="123 Main Street",
            address_line2=None,
            city="Paris",
            postal_code="75001",
            country="fr",
        )
        assert result == "123 Main Street, 75001 Paris, FR"

    def test_formats_partial_no_country(self):
        """Should format address without country."""
        result = format_address(
            address_line1="123 Main Street",
            address_line2="Apartment 4B",
            city="Paris",
            postal_code="75001",
            country=None,
        )
        assert result == "123 Main Street, Apartment 4B, 75001 Paris"

    def test_formats_minimal_city_postal(self):
        """Should format with only city and postal code."""
        result = format_address(
            address_line1=None,
            address_line2=None,
            city="Paris",
            postal_code="75001",
            country="fr",
        )
        assert result == "75001 Paris, FR"

    def test_returns_placeholder_all_empty(self):
        """Should return placeholder when all fields are empty strings."""
        result = format_address(
            address_line1="",
            address_line2="",
            city="",
            postal_code="",
            country="",
        )
        assert result == "Adresse à compléter"

    def test_returns_placeholder_all_none(self):
        """Should return placeholder when all fields are None."""
        result = format_address(
            address_line1=None,
            address_line2=None,
            city=None,
            postal_code=None,
            country=None,
        )
        assert result == "Adresse à compléter"

    def test_strips_whitespace(self):
        """Should treat whitespace-only fields as empty."""
        result = format_address(
            address_line1="  ",
            address_line2="   ",
            city="  ",
            postal_code="  ",
            country="  ",
        )
        assert result == "Adresse à compléter"

    def test_uppercases_country(self):
        """Should uppercase country code."""
        result = format_address(
            address_line1="123 Main Street",
            address_line2=None,
            city="Paris",
            postal_code="75001",
            country="france",
        )
        assert result == "123 Main Street, 75001 Paris, FRANCE"

    def test_mixed_empty_and_whitespace(self):
        """Should handle mix of None, empty strings, and whitespace."""
        result = format_address(
            address_line1="123 Main Street",
            address_line2="  ",
            city=None,
            postal_code="",
            country="fr",
        )
        assert result == "123 Main Street, FR"

    def test_only_address_line1(self):
        """Should format with only line1."""
        result = format_address(
            address_line1="123 Main Street",
            address_line2=None,
            city=None,
            postal_code=None,
            country=None,
        )
        assert result == "123 Main Street"

    def test_only_city_no_postal(self):
        """Should format with only city."""
        result = format_address(
            address_line1=None,
            address_line2=None,
            city="Paris",
            postal_code=None,
            country=None,
        )
        assert result == "Paris"
