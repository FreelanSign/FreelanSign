# apps/branding/interface/permissions.py
from __future__ import annotations

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Note: Currently unused. Uses account context from Phase 5.3 migration.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        # Phase 5.3: Check against account instead of professional
        return hasattr(request, "account") and obj.account_id == request.account.id
