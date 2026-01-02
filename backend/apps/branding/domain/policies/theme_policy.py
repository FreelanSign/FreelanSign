# apps/branding/domain/policies/theme_policy.py
from __future__ import annotations


class ThemePolicyError(ValueError):
    """
    Exception raised when theme policy is violated.

    Args:
        message: The error message.
    """

    pass


def validate_single_active_theme(existing_active_count: int, is_activating: bool) -> None:
    """
    Ensure only one theme can be active at a time per professional.

    Args:
        existing_active_count: The number of active themes for the professional.
        is_activating: Whether the theme is being activated.
    """
    if existing_active_count > 0 and is_activating:
        raise ThemePolicyError("Only one theme can be active at a time per professional. Deactivate another theme first.")


def validate_theme_ownership(theme_account_id: int | str, requester_account_id: int | str) -> None:
    """
    Ensure the theme belongs to the requester.

    Args:
        theme_account_id: The ID of the professional who owns the theme.
        requester_account_id: The ID of the professional making the request.
    """
    if theme_account_id != requester_account_id:
        raise ThemePolicyError("You can only modify themes you own.")
