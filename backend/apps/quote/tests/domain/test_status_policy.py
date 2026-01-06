import pytest

from apps.quote.domain.policies.status_policy import can_transition


@pytest.mark.parametrize(
    "current, new",
    [
        ("DRAFT", "SENT"),
        ("DRAFT", "CANCELLED"),
        ("SENT", "ACCEPTED"),
        ("SENT", "REJECTED"),
        ("SENT", "CANCELLED"),
        ("ACCEPTED", "PAID"),
        ("ACCEPTED", "CANCELLED"),
        ("REJECTED", "DRAFT"),
    ],
)
def test_can_transition_valid(current, new):
    """Test transitions that should be allowed."""
    assert can_transition(current, new) is True


@pytest.mark.parametrize(
    "current, new",
    [
        ("DRAFT", "PAID"),
        ("DRAFT", "ACCEPTED"),
        ("SENT", "DRAFT"),
        ("SENT", "PAID"),
        ("ACCEPTED", "SENT"),
        ("ACCEPTED", "DRAFT"),
        ("PAID", "DRAFT"),
        ("PAID", "SENT"),
        ("CANCELLED", "DRAFT"),
        ("EXPIRED", "SENT"),
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
