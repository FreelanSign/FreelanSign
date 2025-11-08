# apps/quote/adapters/reference/django_quote_reference_generator.py
from datetime import date

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.core.models.mixins import DocumentCounter
from apps.quote.application.ports.reference_gen import QuoteReferenceGeneratorPort


class DjangoQuoteReferenceGenerator(QuoteReferenceGeneratorPort):
    DOC_TYPE = "QUOTE"

    def next_reference(self, *, owner_id: str | int, when: date | None = None) -> str:
        """Generate a next reference for a quote."""
        if when is None:
            when = timezone.localdate()
        period = when.strftime("%Y-%m")

        with transaction.atomic():
            counter, _ = DocumentCounter.objects.select_for_update().get_or_create(
                owner_id=owner_id, doc_type=self.DOC_TYPE, period=period, defaults={"last_value": 0}
            )
            counter.last_value = F("last_value") + 1
            counter.save(update_fields=["last_value"])
            counter.refresh_from_db(fields=["last_value"])

        seq = f"{counter.last_value:04d}"
        return f"Q-{period}-{seq}"


# Helper optionnel pour le wiring manuel
def get_quote_reference_generator() -> DjangoQuoteReferenceGenerator:
    return DjangoQuoteReferenceGenerator()
