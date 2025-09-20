# apps/quote/services/lineFromPrestation.py
from decimal import Decimal
from ..models import Prestation
from apps.core.utils.money import cents_to_euros

def create_line_from_prestation(quote, prestation: Prestation, qty: Decimal = None, tax_rate: Decimal = None, discount: Decimal = None, order: int = 0):
    """
    Create a QuoteLineItem from a Prestation catalog entry.
    - Convert cents -> euros using existing helper
    - Fill metadata with area_key/name/id for traceability
    - Choose tax_rate based on owner profile if not provided
    """
    from apps.quote.models import QuoteLineItem

    # default qty uses prestation.weight_days (as integer number of days)
    if qty is None:
        qty = Decimal(prestation.weight_days)
    # convert cents -> euros
    unit_price_eur = Decimal(str(cents_to_euros(prestation.default_rate_cents))).quantize(Decimal("0.01"))

    # determine tax_rate: prefer provided tax_rate, otherwise owner profile, otherwise global default 20%
    if tax_rate is None:
        owner = quote.owner
        # Example: check owner.profile.vat_exempt or owner.profile.default_tax_rate if you added them
        # This is pseudo-code, adapt to your user model
        try:
            profile = owner.profile
            if getattr(profile, "vat_exempt", False):
                tax_rate = Decimal("0.00")
            else:
                tax_rate = getattr(profile, "default_tax_rate", Decimal("20.00"))
        except Exception:
            tax_rate = Decimal("20.00")

    if discount is None:
        discount = Decimal("0.00")

    item = QuoteLineItem.objects.create(
        quote=quote,
        description=prestation.name,
        qty=qty,
        unit_price=unit_price_eur,
        tax_rate=Decimal(tax_rate),
        discount=Decimal(discount),
        order=order,
        metadata={
            "prestation_id": prestation.pk,
            "prestation_name": prestation.name,
            "area_name": prestation.area.name,
            "catalog_status": prestation.status,
        },
    )
    return item
