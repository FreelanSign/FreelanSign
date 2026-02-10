# apps/user/interface/permissions/account_permissions.py
"""
Permissions for Account resource.

@author: @Bertrand2808
@since: 2025-11-26
@version: 1.0
"""

from rest_framework import permissions

from apps.user.models.account import Account


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


class HasAccountContext(permissions.BasePermission):
    """
    Permission to ensure the request has a valid account context.

    - Admin (is_staff) : bypass
    - Utilisateur authentifié : doit avoir un Account actif
      -> on essaye d'abord request.account (middleware)
      -> sinon on fallback vers le 1er account actif en DB
    """

    def has_permission(self, request, view):
        # Pas logué => pas d'account context pour les opérations écriture
        # (IsAuthenticatedOrReadOnly) s'occupe déjà de refuser les méthodes non SAFE
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin bypass
        if request.user.is_staff:
            return True

        # Middleware a déjà mis un account ?
        account = getattr(request, "account", None)
        if account is not None:
            return True

        # Fallback vers le 1er account actif en DB
        account = Account.objects.filter(user=request.user, is_active=True).first()
        if account:
            request.account = account
            return True

        # User sans account actif => 403
        return False
