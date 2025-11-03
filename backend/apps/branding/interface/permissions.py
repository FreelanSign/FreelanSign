# apps/branding/interface/permissions.py
from __future__ import annotations

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        return str(obj.professional_id) == str(request.user.id)


class IsProfessionalUser(permissions.BasePermission):
    """
    Custom permission to only allow professional users to access the view.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if not hasattr(user, "professional"):
            raise PermissionDenied(self.message)

        return True
