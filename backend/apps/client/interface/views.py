# apps/client/interface/views.py
from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.client.models import Client

from .serializers import ClientSerializer


class StandardClientViewSet(viewsets.ModelViewSet):
    """
    Simple CRUD ViewSet for Client.
    - No special permissions: authenticated users create clients.
    - Owners will be set automatically at creation time (owner = request.user).
    - Supports filtering by owner and searching by name/email.
    """

    queryset = Client.objects.all().select_related("owner")
    serializer_class = ClientSerializer

    # minimal filtering/searching
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["owner"]
    search_fields = ["name", "email", "phone"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        By default, return all clients.
        If you want to restrict to the current user's clients later,
        return self.queryset.filter(owner=self.request.user).
        """
        return self.queryset

    def perform_create(self, serializer):
        """
        Set the owner of the Client to the authenticated user.
        """
        user = getattr(self.request, "user", None)
        serializer.save(owner=user)

    def perform_update(self, serializer):
        """
        Updating a client preserves owner. This hook is here if we later want to
        enforce ownership or set updated metadata.
        """
        serializer.save()
