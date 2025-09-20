# apps/quote/signals.py
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import QuoteLineItem


@receiver([post_save, post_delete], sender=QuoteLineItem)
def on_quote_lineitem_changed(sender, instance, **kwargs):
    """
    When a line item is created/updated/deleted, recalculate parent quote totals
    after the DB transaction commits to avoid race conditions.
    """
    quote = instance.quote

    def _recalc():
        # import inside function to avoid circular import issues
        quote.recalculate_totals(save=True)

    transaction.on_commit(_recalc)
