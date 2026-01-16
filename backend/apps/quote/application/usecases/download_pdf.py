from __future__ import annotations

import logging

from apps.branding.domain.services.theme_normalizer import normalize_theme_dict
from apps.legal_terms.adapters.persistence.django_attached_terms_repository import DjangoAttachedTermsRepository
from apps.quote.application.dto.quote_inputs import LineItemInputDTO, PreviewPayloadDTO
from apps.quote.application.ports.pdf_generator import PdfGenerator
from apps.quote.application.ports.quote_repository import QuoteRepository
from apps.quote.application.ports.template_renderer import TemplateRenderer
from apps.quote.application.usecases.generate_preview import generate_preview

log = logging.getLogger(__name__)


class DownloadPdf:
    def __init__(self, repo: QuoteRepository, renderer: TemplateRenderer, pdf: PdfGenerator, theme_loader=None):
        self.repo = repo
        self.renderer = renderer
        self.pdf = pdf
        self.theme_loader = theme_loader

    def execute(
        self,
        *,
        quote_id: str,
        owner_vat_exempt: bool,
        owner_default_rate_pct,
        client_country: str | None,
        actor,
    ):
        log.info("download_pdf.start quote_id=%s, actor_id=%s", quote_id, getattr(actor, "id", None))

        # 1) récupérer le devis
        quote = self.repo.get(quote_id, requester_id=str(actor.id), include_lines=True)
        log.info(
            "download_pdf.quote_loaded quote_id=%s, client_id=%s, nb_lines=%s",
            quote.id,
            getattr(quote.client, "id", None),
            quote.items.count(),
        )

        # 2) charger le thème (sans forcer en UUID)
        branding = None
        raw_theme = None
        if self.theme_loader and hasattr(actor, "id"):
            raw_id = actor.id
            log.debug("download_pdf.theme_loader.call actor_id=%s, actor_id_type=%s", raw_id, type(raw_id).__name__)
            try:
                raw_theme = self.theme_loader(raw_id)
                log.debug(
                    "download_pdf.theme_loader.done actor_id=%s, has_branding=%s, theme_name=%s",
                    raw_id,
                    bool(raw_theme),
                    raw_theme.get("name") if isinstance(raw_theme, dict) else None,
                )
            except Exception as e:
                log.exception("download_pdf.theme_loader.error actor_id=%s", raw_id)
                raw_theme = None
            branding = normalize_theme_dict(raw_theme)
        else:
            log.debug(
                "download_pdf.theme_loader.skipped_no_theme_loader has_loader=%s, actor_id=%s",
                bool(self.theme_loader),
                getattr(actor, "id", None),
            )

        # 3) mapper les lignes
        lines = [
            LineItemInputDTO(
                description=li.description,
                qty=li.qty,
                unit_price=li.unit_price,
                discount=li.discount,
                tax_rate_pct=li.tax_rate,
            )
            for li in quote.items.all()
        ]
        seller_payload = _build_seller_from_actor(actor, quote.account)
        log.debug("download_pdf.seller_payload seller_payload=%s", seller_payload)
        # 4) construire le DTO de preview
        dto = PreviewPayloadDTO(
            seller=seller_payload,
            client={"name": getattr(quote.client, "name", ""), "country": client_country},
            # ⚠️ ton template lit meta.number / meta.date → on les met bien comme ça
            meta={
                "number": quote.reference,
                "date": str(quote.issue_date),
            },
            lines=lines,
            branding=branding,
            owner_vat_exempt=owner_vat_exempt,
            owner_default_rate_pct=owner_default_rate_pct,
            client_country=client_country,
        )

        # 5) générer le viewmodel (OBJET)
        vm = generate_preview(dto)

        # Phase 7: Fetch legal terms for PDF
        # AIDEV-NOTE: Diagnostic logs added to debug legal terms generation issue (#87)
        legal_terms_html = None
        try:
            attached_terms_repo = DjangoAttachedTermsRepository()
            log.debug("download_pdf.legal_terms_fetch.start quote_id=%s", quote_id)
            attached_terms = attached_terms_repo.get_by_quote(quote_id)
            if attached_terms:
                legal_terms_html = attached_terms.rendered_html
                log.info(
                    "download_pdf.legal_terms_loaded quote_id=%s html_length=%s html_preview=%s",
                    quote_id,
                    len(legal_terms_html) if legal_terms_html else 0,
                    legal_terms_html[:100] if legal_terms_html else "EMPTY",
                )
            else:
                log.warning("download_pdf.no_legal_terms quote_id=%s attached_terms_is_none=True", quote_id)
        except Exception as e:
            log.error(
                "download_pdf.legal_terms_error quote_id=%s error=%s",
                quote_id,
                str(e),
                exc_info=True,
            )

        # 6) logs sans casser le type
        log.debug(
            "download_pdf.before_render quote_id=%s has_branding=%s meta_keys=%s has_legal_terms=%s",
            quote_id,
            bool(getattr(vm, "branding", None)),
            list(vm.meta.keys()) if hasattr(vm, "meta") and isinstance(vm.meta, dict) else None,
            bool(legal_terms_html),
        )

        # 7) rendu
        html = self.renderer.render("quote/pdf/document.html", vm, legal_terms_html=legal_terms_html)
        pdf_bytes = self.pdf.generate(html)

        log.info("download_pdf.done quote_id=%s, pdf_len=%s", quote_id, len(pdf_bytes))
        return pdf_bytes


def _build_seller_from_actor(actor, account=None) -> dict:
    """
    Construit le payload 'seller' pour le PDF à partir du user connecté et du compte.
    On agrège: user, profile, professional, account.
    """
    if actor is None:
        return {"name": "FreelanSign"}

    # 1) base user
    email = getattr(actor, "email", None)
    # tu avais un champ deprecated full_name
    legacy_name = getattr(actor, "full_name", None)

    # 2) profile
    profile = getattr(actor, "profile", None)
    first_name = getattr(profile, "first_name", None) if profile else None
    last_name = getattr(profile, "last_name", None) if profile else None

    # 3) professional (legacy)
    pro = getattr(actor, "professional", None)
    pro_name = getattr(pro, "name", None) if pro else None
    siret = getattr(pro, "number_pro", None) if pro else None
    statut = getattr(pro, "status_juridique", None) if pro else None

    # 4) account (new architecture)
    account_name = getattr(account, "display_name", None) if account else None
    account_siret = getattr(account, "legal_id", None) if account else None
    account_legal_form = getattr(account, "legal_form", None) if account else None
    professional_headline = getattr(account, "professional_headline", None) if account else None

    # priorité d'affichage: account > professional > profile > legacy > email
    display_name = (
        account_name
        or pro_name
        or (" ".join(p for p in [first_name, last_name] if p) or None)
        or legacy_name
        or email
        or "FreelanSign"
    )

    # Priorité SIRET: account > professional
    final_siret = account_siret or siret
    # Priorité statut juridique: account > professional
    final_statut = account_legal_form or statut

    seller = {
        "name": display_name,
        "professional_headline": professional_headline,
        "siret": final_siret,
        "vat_number": None,  # tu pourras le mapper depuis un autre modèle plus tard
        "address": None,
        "email": email,
        "legal_status": final_statut,
    }

    return seller
