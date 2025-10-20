# apps/quote/domain/policies/status_policy.py
"""
Status policy for quotes.
"""

from __future__ import annotations

ALLOWED_TRANSITIONS = {
    "DRAFT": {"SENT", "CANCELLED"},
    "SENT": {"ACCEPTED", "REJECTED", "CANCELLED"},
    "ACCEPTED": {"PAID", "CANCELLED"},
    "REJECTED": {"DRAFT"},
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
