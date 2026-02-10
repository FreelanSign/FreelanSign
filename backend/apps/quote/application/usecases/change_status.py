from __future__ import annotations

from apps.quote.application.ports.quote_repository import QuoteRepository
from apps.quote.domain.policies.status_policy import can_transition


class ChangeStatus:
    """Change the status of a quote."""

    def __init__(self, repo: QuoteRepository):
        self.repo = repo

    def execute(self, *, quote_id: str, new_status: str, actor):
        quote = self.repo.get(quote_id, requester_id=str(actor.id), include_lines=False)
        if not can_transition(quote.status, new_status):
            raise ValueError(f"Transition from {quote.status} to {new_status} is not allowed.")
        quote.status = new_status
        if new_status == "ACCEPTED":
            from django.utils import timezone

            quote.accepted_at = timezone.now()
        quote.save(update_fields=["status", "accepted_at", "updated_at"])
        # create history (keep the ORM model for now)
        from apps.quote.models import QuoteHistory

        QuoteHistory.objects.create(
            quote=quote,
            payload_snapshot={"from": quote.status, "to": new_status},
            action=QuoteHistory.Action.STATUS_CHANGED,
            actor=actor,
        )
        return quote
