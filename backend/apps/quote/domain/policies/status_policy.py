# apps/quote/domain/policies/status_policy.py
"""
Status policy for quotes.
"""

from __future__ import annotations

# AIDEV-NOTE: Matrice transitions validée 2026-02-04
# DRAFT = état initial, toutes transitions possibles (workflows variés)
# REJECTED devient terminal (pas de réutilisation brouillon)
ALLOWED_TRANSITIONS = {
    "DRAFT": {"SENT", "ACCEPTED", "PAID", "REJECTED", "EXPIRED", "CANCELLED"},
    "SENT": {"ACCEPTED", "PAID", "REJECTED", "EXPIRED", "CANCELLED"},
    "ACCEPTED": {"PAID", "EXPIRED", "CANCELLED"},
    "REJECTED": set(),
    "PAID": set(),
    "CANCELLED": set(),
    "EXPIRED": set(),
}


def can_transition(current: str, new: str) -> bool:
    """
    Check if a transition from current status to new status is allowed.

    Args:
        current: The current status.
        new: The new status.

    Returns:
        True if the transition is allowed, False otherwise.
    """
    return new in ALLOWED_TRANSITIONS.get(current, set())
