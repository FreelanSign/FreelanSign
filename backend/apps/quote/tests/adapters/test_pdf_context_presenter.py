# apps/quote/tests/adapters/test_pdf_context_presenter.py
import pytest

from apps.quote.adapters.rendering.pdf_context_presenter import preview_context


def test_has_uniform_tax_when_all_items_same_rate():
    """When all line items have the same tax rate, has_uniform_tax should be True"""
    vm = {
        "seller": {"name": "Test Seller"},
        "client": {"name": "Test Client"},
        "meta": {"number": "Q-001", "date": "2026-01-19"},
        "lines": [
            {
                "designation": "Item 1",
                "description": "Description 1",
                "quantity": 1,
                "unit_price": 100.0,
                "tax_rate_display": 20.0,
                "total_ht": 100.0,
                "discount": 0.0,
            },
            {
                "designation": "Item 2",
                "description": "Description 2",
                "quantity": 2,
                "unit_price": 50.0,
                "tax_rate_display": 20.0,
                "total_ht": 100.0,
                "discount": 0.0,
            },
        ],
        "totals": {"subtotal": 200.0, "tax": 40.0, "grand_total": 240.0},
        "branding": {},
    }

    result = preview_context(vm, is_download=False)

    assert result["has_uniform_tax"] is True


def test_has_uniform_tax_when_items_have_mixed_rates():
    """When line items have different tax rates, has_uniform_tax should be False"""
    vm = {
        "seller": {"name": "Test Seller"},
        "client": {"name": "Test Client"},
        "meta": {"number": "Q-001", "date": "2026-01-19"},
        "lines": [
            {
                "designation": "Item 1",
                "description": "Description 1",
                "quantity": 1,
                "unit_price": 100.0,
                "tax_rate_display": 20.0,
                "total_ht": 100.0,
                "discount": 0.0,
            },
            {
                "designation": "Item 2",
                "description": "Description 2",
                "quantity": 2,
                "unit_price": 50.0,
                "tax_rate_display": 10.0,
                "total_ht": 100.0,
                "discount": 0.0,
            },
        ],
        "totals": {"subtotal": 200.0, "tax": 30.0, "grand_total": 230.0},
        "branding": {},
    }

    result = preview_context(vm, is_download=False)

    assert result["has_uniform_tax"] is False


def test_has_uniform_tax_when_no_lines():
    """When there are no line items, has_uniform_tax should be True (trivially uniform)"""
    vm = {
        "seller": {"name": "Test Seller"},
        "client": {"name": "Test Client"},
        "meta": {"number": "Q-001", "date": "2026-01-19"},
        "lines": [],
        "totals": {"subtotal": 0.0, "tax": 0.0, "grand_total": 0.0},
        "branding": {},
    }

    result = preview_context(vm, is_download=False)

    assert result["has_uniform_tax"] is True


def test_has_uniform_tax_when_single_line():
    """When there is only one line item, has_uniform_tax should be True"""
    vm = {
        "seller": {"name": "Test Seller"},
        "client": {"name": "Test Client"},
        "meta": {"number": "Q-001", "date": "2026-01-19"},
        "lines": [
            {
                "designation": "Item 1",
                "description": "Description 1",
                "quantity": 1,
                "unit_price": 100.0,
                "tax_rate_display": 20.0,
                "total_ht": 100.0,
                "discount": 0.0,
            },
        ],
        "totals": {"subtotal": 100.0, "tax": 20.0, "grand_total": 120.0},
        "branding": {},
    }

    result = preview_context(vm, is_download=False)

    assert result["has_uniform_tax"] is True


def test_has_uniform_tax_when_tax_rate_missing():
    """When tax_rate_display is None, it defaults to 0.0 (should be uniform)"""
    vm = {
        "seller": {"name": "Test Seller"},
        "client": {"name": "Test Client"},
        "meta": {"number": "Q-001", "date": "2026-01-19"},
        "lines": [
            {
                "designation": "Item 1",
                "description": "Description 1",
                "quantity": 1,
                "unit_price": 100.0,
                "total_ht": 100.0,
                "discount": 0.0,
            },
            {
                "designation": "Item 2",
                "description": "Description 2",
                "quantity": 1,
                "unit_price": 100.0,
                "tax_rate_display": 0.0,
                "total_ht": 100.0,
                "discount": 0.0,
            },
        ],
        "totals": {"subtotal": 200.0, "tax": 0.0, "grand_total": 200.0},
        "branding": {},
    }

    result = preview_context(vm, is_download=False)

    assert result["has_uniform_tax"] is True
