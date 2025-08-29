from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

_TWO_PLACES = Decimal("0.01")

def _to_decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    # conversion sure pour str/float/int
    return Decimal(str(value))

def euros_to_cents(value) -> int:
    """
    Convertit un montant en euros -> centimes (arrondi).
    euto_to_cents("12.345") -> 1235
    euto_to_cents("12.34") -> 1234
    """
    d = _to_decimal(value).quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    return int((d*100).to_integral_value(rounding=ROUND_HALF_UP))

def cents_to_euros(cents: int | None) -> Decimal:
    """Centimes -> euros (Decimal à 2 décimales)."""
    if cents is None:
        raise ValueError("cents cannot be None")

    # Utiliser une variable locale pour clarifier le type
    assert cents is not None  # Aide l'analyseur statique
    cents_value: int = cents
    return (Decimal(cents_value) / 100).quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)

def format_euros(cents: int, with_symbol: bool = True) -> str:
    """
    Formate un montant en style FR simple : "12,34 €".
    """
    d = cents_to_euros(cents)
    s = f"{d:.2f}".replace(".", ",")
    return f"{s} €" if with_symbol else s

def vat_amount_ht(cents_ht: int, vat_bps: int) -> int:
    """
    Montant de TVA à partir d'un HT, avec tva en basis points (2000 = 20.00%).
    """
    d_ht = cents_to_euros(cents_ht)
    rate = Decimal(vat_bps) / Decimal(10000)
    vat = (d_ht * rate).quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    return euros_to_cents(vat)

def apply_vat(cents_ht: int, vat_bps: int) -> int:
    """HT -> TTC en centimes, via basis points."""
    return int(cents_ht) + vat_amount_ht(cents_ht, vat_bps)

def extract_vat_from_ttc(cents_ttc: int, vat_bps: int) -> tuple[int, int]:
    """
    À partir d'un TTC et d'un taux en bps, renvoie (HT, TVA), en centimes.
    """
    rate = Decimal(vat_bps) / Decimal(10000)
    d_ttc = cents_to_euros(cents_ttc)
    d_ht = (d_ttc / (Decimal(1) + rate)).quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    cents_ht = euros_to_cents(d_ht)
    return cents_ht, int(cents_ttc) - cents_ht
