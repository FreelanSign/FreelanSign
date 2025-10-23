from __future__ import annotations

from apps.quote.application.dto.quote_inputs import LineItemInputDTO, PreviewPayloadDTO
from apps.quote.application.ports.email_sender import EmailSender
from apps.quote.application.ports.pdf_generator import PdfGenerator
from apps.quote.application.ports.quote_repository import QuoteRepository
from apps.quote.application.ports.template_renderer import TemplateRenderer
from apps.quote.application.usecases.generate_preview import generate_preview


class SendQuote:
    """Send a quote."""

    def __init__(self, repo: QuoteRepository, renderer: TemplateRenderer, pdf: PdfGenerator, mailer: EmailSender):
        self.repo, self.renderer, self.pdf, self.mailer = repo, renderer, pdf, mailer

    def execute(self, *, quote_id: str, owner_vat_exempt: bool, owner_default_rate_pct, client_country: str | None, actor):
        """Send a quote."""
        quote = self.repo.get(quote_id, include_lines=True)
        # build DTO from persisted quote (or reuse your existing mapping utils)
        lines = [
            LineItemInputDTO(
                description=li.description,
                qty=li.qty,
                unit_price=li.unit_price,
                discount=li.discount,
                tax_rate_pct=li.tax_rate,  # already in %
            )
            for li in quote.items.all()
        ]
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
        pdf_bytes = self.pdf.generate(html)

        # persist attachment if you have a helper; otherwise leave as email-only
        try:
            from apps.quote.models import QuoteHistory

            # attach to model filefield if needed
            # quote.pdf_file.save(filename, ContentFile(pdf_bytes))  # optional
            quote.status = "SENT"
            from django.utils import timezone

            quote.sent_at = timezone.now()
            quote.save(update_fields=["status", "sent_at", "updated_at"])
            QuoteHistory.objects.create(
                quote=quote, payload_snapshot={"status": "SENT"}, action=QuoteHistory.Action.SENT, actor=actor
            )
        except Exception:
            pass

        recipients = []
        if getattr(quote.client, "email", None):
            recipients.append(quote.client.email)
        if getattr(actor, "email", None):
            recipients.append(actor.email)
        if recipients:
            self.mailer.send_quote(
                recipients=recipients,
                subject=f"Votre devis {quote.reference}",
                body_html=html,
                attachments=[(f"{quote.reference}.pdf", pdf_bytes)],
            )
        return quote, pdf_bytes
