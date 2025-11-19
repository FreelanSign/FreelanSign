# apps/quote/domain/policies/tax_policy.py
from __future__ import annotations

from decimal import Decimal

ZERO = Decimal("0.00")


class TaxPolicyError(ValueError):
    """
    Exception raised when tax policy is violated.

    Args:
        message: The error message.
    """

    pass


def normalize_rate_percent(rate: Decimal | None) -> Decimal:
    """Rate as percentage (0..100). - None => None (callers decide)

    Args:
        rate: The tax rate to normalize (as percentage).

    Raises:
        TaxPolicyError: If the tax rate is not between 0 and 100 (percentage).

    Returns:
        The normalized tax rate (as percentage).
    """
    if rate is None:
        return None  # type: ignore
    r = Decimal(str(rate))
    if r < ZERO or r > Decimal("100.00"):
        raise TaxPolicyError("Tax rate must be between 0 and 100 (percentage).")
    return r.quantize(Decimal("0.01"))


def effective_rate_for_line(
    explicit_rate_pct: Decimal | None,
    *,
    owner_vat_exempt: bool,
    owner_default_rate_pct: Decimal,
) -> Decimal:
    """Compute the effective % tax rate for a line.

    Args:
        explicit_rate_pct: The explicit tax rate for the line (as percentage).
        owner_vat_exempt: Whether the owner is VAT-exempt.
        owner_default_rate_pct: The default tax rate for the owner (as percentage).

    Returns:
        The effective tax rate for the line (as percentage).
    """
    if owner_vat_exempt:
        return ZERO
    if explicit_rate_pct is not None:
        return normalize_rate_percent(explicit_rate_pct)
    return normalize_rate_percent(owner_default_rate_pct)  # fallback


def validate_client_vat_rule(
    client_country: str | None,
    owner_vat_exempt: bool,
    line_rates_pct: list[Decimal],
):
    """FR simple rule : if client is French, and owner is not VAT-exempt, then all lines must have a tax rate.

    Args:
        client_country: The country of the client.
        owner_vat_exempt: Whether the owner is VAT-exempt.
        line_rates_pct: The tax rates for the lines (as percentage).

    Raises:
        TaxPolicyError: If the client VAT rule is violated.
    """
    if owner_vat_exempt:
        return
    if client_country and client_country.upper() in {"FR", "FRA", "FRANCE"}:
        any_zero = any((Decimal(str(r)).quantize(Decimal("0.01")) == ZERO for r in line_rates_pct))
        if any_zero:
            raise TaxPolicyError(
                "VAT missing for French client on lines with zero tax rate. Owner must apply VAT or be VAT-exempt."
            )
