# apps/user/interface/permissions/account_permissions.py
"""
Permissions for Account resource.

@author: @Bertrand2808
@since: 2025-11-26
@version: 1.0
"""
from rest_framework import permissions


class IsAccountOwner(permissions.BasePermission):
    """
    Permission to check if user owns the account.

    Admin users bypass ownership check and can access any account.
    Regular users can only access their own accounts.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access this account object.

        Args:
            request: HTTP request
            view: ViewSet
            obj: Account instance

        Returns:
            True if admin or owner, False otherwise
        """
        # Admin bypass - can access any account
        if hasattr(request.user, "profile") and request.user.profile.role == "admin":
            return True

        # Owner check - must be the account's user
        return obj.user == request.user
