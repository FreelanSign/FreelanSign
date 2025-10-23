from __future__ import annotations
from apps.quote.application.ports.template_renderer import TemplateRenderer
from apps.quote.application.ports.pdf_generator import PdfGenerator
from apps.quote.application.ports.quote_repository import QuoteRepository
from apps.quote.application.usecases.generate_preview import generate_preview
from apps.quote.application.dto.quote_inputs import PreviewPayloadDTO, LineItemInputDTO

class DownloadPdf:
    """Download a PDF of a quote.

    Args:
        repo: The quote repository.
        renderer: The template renderer.
        pdf: The PDF generator.
    """
    def __init__(self, repo: QuoteRepository, renderer: TemplateRenderer, pdf: PdfGenerator):
        """Initialize the DownloadPdf use case."""
        self.repo, self.renderer, self.pdf = repo, renderer, pdf

    def execute(self, *, quote_id: str, owner_vat_exempt: bool, owner_default_rate_pct, client_country: str | None, actor):
        """Download a PDF of a quote."""
        quote = self.repo.get(quote_id, include_lines=True)
        # build DTO from quote (see send_quote)
        lines = [LineItemInputDTO(description=li.description, qty=li.qty, unit_price=li.unit_price,
                                  discount=li.discount, tax_rate_pct=li.tax_rate) for li in quote.items.all()]
        dto = PreviewPayloadDTO(
            seller={"name": getattr(actor, "display_name", "Owner")},
            client={"name": getattr(quote.client, "name", ""), "country": client_country},
            meta={"ref": quote.reference, "issue_date": str(quote.issue_date)},
            lines=lines,
            branding=None,
            owner_vat_exempt=owner_vat_exempt,
            owner_default_rate_pct=owner_default_rate_pct,
            client_country=client_country,
        )
        vm = generate_preview(dto)
        html = self.renderer.render("quote/pdf/document.html", vm)
        return self.pdf.generate(html)
