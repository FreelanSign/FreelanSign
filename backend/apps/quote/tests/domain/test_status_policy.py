import pytest

from apps.quote.domain.policies.status_policy import can_transition


@pytest.mark.parametrize(
    "current, new",
    [
        ("DRAFT", "SENT"),
        ("DRAFT", "ACCEPTED"),
        ("DRAFT", "PAID"),
        ("DRAFT", "REJECTED"),
        ("DRAFT", "EXPIRED"),
        ("DRAFT", "CANCELLED"),
        ("SENT", "ACCEPTED"),
        ("SENT", "PAID"),
        ("SENT", "REJECTED"),
        ("SENT", "EXPIRED"),
        ("SENT", "CANCELLED"),
        ("ACCEPTED", "PAID"),
        ("ACCEPTED", "EXPIRED"),
        ("ACCEPTED", "CANCELLED"),
    ],
)
def test_can_transition_valid(current, new):
    """Test transitions that should be allowed."""
    assert can_transition(current, new) is True


@pytest.mark.parametrize(
    "current, new",
    [
        ("SENT", "DRAFT"),
        ("ACCEPTED", "SENT"),
        ("ACCEPTED", "DRAFT"),
        ("ACCEPTED", "REJECTED"),
        ("REJECTED", "DRAFT"),
        ("REJECTED", "SENT"),
        ("REJECTED", "ACCEPTED"),
        ("PAID", "DRAFT"),
        ("PAID", "SENT"),
        ("PAID", "ACCEPTED"),
        ("CANCELLED", "DRAFT"),
        ("CANCELLED", "SENT"),
        ("EXPIRED", "SENT"),
        ("EXPIRED", "DRAFT"),
        ("UNKNOWN", "DRAFT"),
    ],
)
def test_can_transition_invalid(current, new):
    """Test transitions that should be blocked."""
    assert can_transition(current, new) is False


def test_can_transition_same_status_is_blocked():
    """By default, same status transition is not in our allowed sets."""
    assert can_transition("DRAFT", "DRAFT") is False
    assert can_transition("SENT", "SENT") is False
