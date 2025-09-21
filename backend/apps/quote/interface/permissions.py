# apps/quote/interface/permissions.py
from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS
from typing import Any


class IsOwnerOrAdmin(BasePermission):
    """
    Permission class for Quote ViewSet.

    Rules:
      - Request must be authenticated (has_permission).
      - Object-level:
          - If view.action == "send": only the owner may call it.
          - Otherwise: owner OR admin (is_staff/is_superuser) is allowed.
          - Safe methods (GET/HEAD/OPTIONS) follow the same owner-or-admin rule.
    This class assumes objects have an 'owner' attribute pointing to a User.
    """

    def has_permission(self, request, view) -> bool:
        # Basic gate: require authenticated user
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj: Any) -> bool:
        """
        Object-level permission:
        - send: owner only
        - all other actions: owner or staff/superuser
        """
        user = request.user

        # If there's no user (shouldn't happen because has_permission checked), deny.
        if not user or not user.is_authenticated:
            return False

        # Special-case: 'send' action must be performed by the owner only
        action = getattr(view, "action", None)
        if action == "send":
            # owner strictly required for sending
            return getattr(obj, "owner", None) == user

        # Admins (staff or superuser) can do everything else
        if user.is_staff or user.is_superuser:
            return True

        # Otherwise only the owner may operate
        return getattr(obj, "owner", None) == user
