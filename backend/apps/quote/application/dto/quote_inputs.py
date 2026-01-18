from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LineItemInputDTO:
    """
    Entrée d'une ligne pour la preview (les taux sont en PERCENT si fournis).
    Note: 'tax_rate_pct' est optionnel; on ne veut PAS de champ obligatoire 'tax_rate'.
    """

    designation: str  # Item name/title (was previously 'description')
    qty: Decimal
    unit_price: Decimal
    discount: Decimal | None = None
    tax_rate_pct: Decimal | None = None  # ex: 20 => 20%
    description: str | None = None  # Optional detailed description


@dataclass(frozen=True)
class PreviewPayloadDTO:
    """
    Payload d'entrée pour le use case de preview.
    """

    seller: dict
    client: dict
    meta: dict
    lines: list[LineItemInputDTO]
    branding: dict | None
    owner_vat_exempt: bool
    owner_default_rate_pct: Decimal  # <— NOM harmonisé avec les tests
    client_country: str | None
