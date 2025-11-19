# apps/quote/tests/domain/test_tax_policy.py
from decimal import Decimal

import pytest

from apps.quote.domain.policies.tax_policy import (
    TaxPolicyError,
    effective_rate_for_line,
    normalize_rate_percent,
    validate_client_vat_rule,
)

D = Decimal


def test_normalize_rate_percent_bounds_and_rounding():
    assert normalize_rate_percent(D("0")) == D("0.00")
    assert normalize_rate_percent(D("20")) == D("20.00")
    assert normalize_rate_percent(D("19.999")) == D("20.00")
    with pytest.raises(TaxPolicyError):
        normalize_rate_percent(D("-0.01"))
    with pytest.raises(TaxPolicyError):
        normalize_rate_percent(D("100.01"))


def test_effective_rate_owner_exempt_forces_zero():
    rate = effective_rate_for_line(
        explicit_rate_pct=None,
        owner_vat_exempt=True,
        owner_default_rate_pct=D("20"),
    )
    assert rate == D("0.00")


def test_effective_rate_uses_explicit_when_provided():
    rate = effective_rate_for_line(
        explicit_rate_pct=D("5.50"),
        owner_vat_exempt=False,
        owner_default_rate_pct=D("20"),
    )
    assert rate == D("5.50")


def test_effective_rate_fallbacks_to_owner_default():
    rate = effective_rate_for_line(
        explicit_rate_pct=None,
        owner_vat_exempt=False,
        owner_default_rate_pct=D("20"),
    )
    assert rate == D("20.00")


def test_validate_client_vat_rule_owner_exempt_no_check():
    # Owner exempt: pas d'erreur même si des lignes sont à 0%
    validate_client_vat_rule("FR", True, [D("0.00"), D("0.00")])


def test_validate_client_vat_rule_fr_client_requires_non_zero_when_owner_taxable():
    # Client FR et owner non exempt: doit lever si une ligne à 0%
    with pytest.raises(TaxPolicyError):
        validate_client_vat_rule("FR", False, [D("0.00"), D("20.00")])
    # OK si toutes > 0
    validate_client_vat_rule("FR", False, [D("10.00"), D("20.00")])


def test_validate_client_vat_rule_non_fr_is_free():
    # Client non FR: aucune contrainte dans cette règle simple
    validate_client_vat_rule("ES", False, [D("0.00"), D("20.00")])
