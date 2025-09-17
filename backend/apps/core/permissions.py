from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthenticatedReadOnly(BasePermission):
    """
    Autorise uniquement les requêtes SAFE (GET/HEAD/OPTIONS) pour les users authentifiés.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.method in SAFE_METHODS
