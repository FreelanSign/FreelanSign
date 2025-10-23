# apps/quote/tests/application/test_add_prestation_line.py
import pytest
from decimal import Decimal
from apps.quote.application.usecases.add_prestation_line import AddPrestationLineToQuote, AddPrestationLineInput
from apps.quote.application.ports.prestation_repository import PrestationDTO

class FakePrestations:
    def __init__(self, dto): self.dto = dto
    def get(self, _): return self.dto

class FakeQuotes:
    def __init__(self): self.called=False
    def add_line_item(self, quote_id, **k):
        self.called=True
        class Q: subtotal=Decimal("100"); tax_total=Decimal("20"); total=Decimal("120")
        return Q(), object()

def test_usecase_add_line_ok():
    uc = AddPrestationLineToQuote(
        quotes=FakeQuotes(),
        prestations=FakePrestations(PrestationDTO(
            id="P1", name="Audit", area_name="SEO", default_rate_cents=10000, weight_days=2, status="active"
        ))
    )
    q, li = uc.execute(AddPrestationLineInput(
        quote_id="Q1", prestation_id="P1",
        owner_vat_exempt=False, owner_default_rate_pct=Decimal("20.00")
    ))
    assert q.total == Decimal("120")
