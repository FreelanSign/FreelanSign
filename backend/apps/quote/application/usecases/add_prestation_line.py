from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from apps.quote.application.ports.quote_repository import QuoteRepository
from apps.quote.application.ports.prestation_repository import PrestationRepository
from apps.quote.domain.policies.tax_policy import effective_rate_for_line

def cents_to_euros(cents: int) -> Decimal:
    """ Convert cents to euros. """
    return (Decimal(cents) / Decimal("100")).quantize(Decimal("0.01"))

@dataclass(frozen=True)
class AddPrestationLineInput:
    """ Input for the AddPrestationLineToQuote use case. """
    quote_id: str
    prestation_id: str
    qty: Decimal | None = None
    tax_rate_pct: Decimal | None = None
    discount: Decimal | None = None
    order: int = 0
    # contexte TVA pour policy :
    owner_vat_exempt: bool = False
    owner_default_rate_pct: Decimal = Decimal("20.00")

class AddPrestationLineToQuote:
    """ Use case to add a prestation line to a quote. """
    def __init__(self, *, quotes: QuoteRepository, prestations: PrestationRepository):
        self.quotes = quotes
        self.prestations = prestations

    def execute(self, inp: AddPrestationLineInput):
        """ Execute the AddPrestationLineToQuote use case. """
        # 1) charge la prestation + quote (le repo quote peut vérifier ownership en interne)
        p = self.prestations.get(inp.prestation_id)

        # 2) qty par défaut = weight_days
        qty = Decimal(inp.qty) if inp.qty is not None else Decimal(p.weight_days)

        # 3) prix unitaire en euros
        unit_price = cents_to_euros(p.default_rate_cents)

        # 4) taux TVA effectif
        rate = effective_rate_for_line(
            inp.tax_rate_pct,
            owner_vat_exempt=inp.owner_vat_exempt,
            owner_default_rate_pct=inp.owner_default_rate_pct,
        )

        # 5) discount
        discount = Decimal(inp.discount or Decimal("0.00"))

        # 6) métadonnées de provenance
        meta = {
            "prestation_id": p.id,
            "prestation_name": p.name,
            "area_name": p.area_name,
            "catalog_status": p.status,
        }

        # 7) création de la ligne via le repo + recalc
        quote, line = self.quotes.add_line_item(
            inp.quote_id,
            description=p.name,
            qty=qty,
            unit_price=unit_price,
            tax_rate_pct=rate,
            discount=discount,
            order=inp.order,
            metadata=meta,
        )
        return quote, line
