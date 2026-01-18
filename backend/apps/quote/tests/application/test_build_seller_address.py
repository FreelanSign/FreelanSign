# apps/quote/tests/application/test_build_seller_address.py
"""
Unit tests for _build_seller_from_actor address fields (feat/account-address).

@author: @Bertrand2808
@since: 2026-01-18
"""

import pytest

from apps.quote.application.usecases.download_pdf import _build_seller_from_actor


class MockAccount:
    """Mock Account object for testing."""

    def __init__(self, **kwargs):
        self.display_name = kwargs.get("display_name", "Test Company")
        self.legal_id = kwargs.get("legal_id")
        self.legal_form = kwargs.get("legal_form")
        self.professional_headline = kwargs.get("professional_headline")
        self.logo_url = kwargs.get("logo_url")
        self.address_line1 = kwargs.get("address_line1")
        self.address_line2 = kwargs.get("address_line2")
        self.city = kwargs.get("city")
        self.postal_code = kwargs.get("postal_code")
        self.country = kwargs.get("country")


class MockUser:
    """Mock User object for testing."""

    def __init__(self, **kwargs):
        self.email = kwargs.get("email", "test@example.com")
        self.full_name = kwargs.get("full_name")
        self.profile = kwargs.get("profile")
        self.professional = kwargs.get("professional")


class TestBuildSellerFromActor:
    """Tests for _build_seller_from_actor function."""

    def test_includes_address_fields_from_account(self):
        """Seller dict includes address fields from Account."""
        account = MockAccount(
            display_name="My Company",
            address_line1="123 Main Street",
            address_line2="Suite 456",
            city="Paris",
            postal_code="75001",
            country="FR",
        )
        user = MockUser()

        seller = _build_seller_from_actor(user, account, owner_vat_exempt=False)

        assert seller["address_line1"] == "123 Main Street"
        assert seller["address_line2"] == "Suite 456"
        assert seller["city"] == "Paris"
        assert seller["postal_code"] == "75001"
        assert seller["country"] == "FR"

    def test_builds_formatted_address_from_fields(self):
        """Seller dict includes formatted address string."""
        account = MockAccount(
            display_name="My Company",
            address_line1="123 Main Street",
            city="Paris",
            postal_code="75001",
            country="FR",
        )
        user = MockUser()

        seller = _build_seller_from_actor(user, account, owner_vat_exempt=False)

        # Formatted address should combine address parts
        assert seller["address"] is not None
        assert "123 Main Street" in seller["address"]
        assert "75001" in seller["address"]
        assert "Paris" in seller["address"]

    def test_handles_partial_address(self):
        """Seller dict handles partial address (only some fields set)."""
        account = MockAccount(
            display_name="My Company",
            city="Paris",
            postal_code="75001",
        )
        user = MockUser()

        seller = _build_seller_from_actor(user, account, owner_vat_exempt=False)

        assert seller["address_line1"] is None
        assert seller["city"] == "Paris"
        assert seller["postal_code"] == "75001"
        # Formatted address should still work with partial data
        assert seller["address"] is not None
        assert "Paris" in seller["address"]

    def test_handles_no_account(self):
        """Seller dict handles None account gracefully."""
        user = MockUser()

        seller = _build_seller_from_actor(user, None, owner_vat_exempt=False)

        assert seller["address_line1"] is None
        assert seller["city"] is None
        assert seller["address"] is None

    def test_handles_empty_address_fields(self):
        """Seller dict handles empty address fields."""
        account = MockAccount(
            display_name="My Company",
            address_line1="",
            city="",
            postal_code="",
            country="",
        )
        user = MockUser()

        seller = _build_seller_from_actor(user, account, owner_vat_exempt=False)

        # Empty strings should not be included in formatted address
        assert seller["address"] is None or seller["address"] == ""
