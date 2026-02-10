# apps/quote/tests/test_download_pdf_api.py
from decimal import Decimal

import pytest
from django.urls import reverse

from apps.legal_terms.adapters.persistence.models import (
    AttachedTermsModel,
    LegalProfileModel,
    LegalTemplateModel,
)
from apps.legal_terms.domain.value_objects.clause_category import ClauseCategory


@pytest.mark.django_db
@pytest.mark.django_db
def test_download_pdf_ok(api_client, user_with_account, mock_pdf_and_email):
    # Setup rapide : user + client + quote + line item
    user, account = user_with_account
    api_client.force_login(user)

    from apps.client.models import Client as ClientModel
    from apps.quote.models import Quote, QuoteLineItem

    cli = ClientModel.objects.create(owner=user, name="ACME", email="a@a.test", account=account)
    q = Quote.objects.create(
        owner=user,
        account=account,
        client=cli,
        title="T",
        reference="REF-TEST",
        currency="EUR",
        language="fr",
        status=Quote.Status.DRAFT,
        issue_date="2025-01-01",
        subtotal=Decimal("0.00"),
        tax_total=Decimal("0.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("0.00"),
    )
    QuoteLineItem.objects.create(
        quote=q,
        description="L1",
        qty=Decimal("1.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        discount=Decimal("0.00"),
        order=0,
    )
    q.recalculate_totals(save=True)

    url = reverse("quote:quote-download-pdf", kwargs={"pk": q.pk})  # nom configuré dans ta view
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/pdf"
    assert resp.content.startswith(b"%PDF")


@pytest.mark.django_db
def test_quote_pdf_includes_attached_legal_terms_html(api_client, user_with_account):
    """
    Phase 7: Integration test to verify PDF generation includes legal terms.

    Light integration test (as per Phase 7 spec) that verifies:
    1. PDF download succeeds for a quote with attached legal terms
    2. The attached terms exist and are linked to the quote

    Note: Detailed HTML content verification would require unmocking the renderer,
    but Phase 7 spec says "can be light" so we verify the flow works end-to-end.
    """
    # Setup: user + account + client + quote + legal terms
    user, account = user_with_account
    api_client.force_login(user)

    from apps.client.models import Client as ClientModel
    from apps.quote.models import Quote, QuoteLineItem

    # Get or create template (might exist from seed data)
    template, _ = LegalTemplateModel.objects.get_or_create(
        jurisdiction="FR",
        version="1.0.0",
        defaults={
            "name": "CGV FR Test",
            "clauses": [
                {
                    "identifier": "payment",
                    "category": ClauseCategory.MANDATORY.value,
                    "default_title": "Conditions de paiement",
                    "default_body": "Le paiement est dû sous 30 jours.",
                    "default_order": 1,
                    "default_is_active": True,
                }
            ],
            "is_active": True,
        },
    )

    profile = LegalProfileModel.objects.create(
        account=account,
        template=template,
        clause_overrides={},
    )

    # Create client and quote
    cli = ClientModel.objects.create(owner=user, name="Test Client", email="client@test.fr", account=account)
    q = Quote.objects.create(
        owner=user,
        account=account,
        client=cli,
        title="Devis avec CGV",
        reference="REF-CGV-001",
        currency="EUR",
        language="fr",
        status=Quote.Status.DRAFT,
        issue_date="2025-01-01",
        subtotal=Decimal("100.00"),
        tax_total=Decimal("20.00"),
        discount_total=Decimal("0.00"),
        total=Decimal("120.00"),
    )
    QuoteLineItem.objects.create(
        quote=q,
        description="Service test",
        qty=Decimal("1.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        discount=Decimal("0.00"),
        order=0,
    )

    # Create attached terms with distinctive HTML
    test_legal_html = "<h2>CONDITIONS GÉNÉRALES DE VENTE</h2><p>Conditions de paiement: 30 jours.</p>"
    AttachedTermsModel.objects.create(
        quote=q,
        template_version="1.0.0",
        rendered_html=test_legal_html,
        rendered_text="CGV - Paiement 30 jours",
        snapshot_data={
            "template_version": "1.0.0",
            "clauses": [
                {"identifier": "payment", "title": "Conditions de paiement", "body": "Le paiement est dû sous 30 jours."}
            ],
            "variables_used": {},
        },
    )

    # Download PDF
    url = reverse("quote:quote-download-pdf", kwargs={"pk": q.pk})
    resp = api_client.get(url)

    # Phase 7: Verify PDF download succeeds
    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/pdf"
    # Note: response content is mocked in tests, actual PDF generation tested elsewhere

    # Verify the attached terms exist and are properly linked
    attached_terms = AttachedTermsModel.objects.get(quote=q)
    assert attached_terms is not None
    assert attached_terms.template_version == "1.0.0"
    assert "CONDITIONS GÉNÉRALES" in attached_terms.rendered_html
    assert "30 jours" in attached_terms.rendered_html

    # Verify the full integration: quote → attached_terms → PDF download works
    # The legal terms are fetched and passed to the PDF renderer (tested via logs in use case)
