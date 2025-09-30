# apps/client/interface/serializers.py
from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.client.models import Client

User = get_user_model()


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for Client model.
    - owner is read-only and set automatically from request.user in the view.
    - created_at / updated_at are read-only.
    """

    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "owner",
            "name",
            "email",
            "phone",
            "address",
            "vat_number",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        """Name must be non-empty and trimmed."""
        v = value.strip()
        if not v:
            raise serializers.ValidationError("Client name cannot be empty.")
        return v


# ----------------------------
# Small client read serializer (ENRICHED)
# ----------------------------
class ClientReadSerializer(serializers.ModelSerializer):
    """
    Représentation enrichie du client pour les endpoints de lecture du devis.
    (on n'expose pas owner/created/updated ici)
    """

    class Meta:
        model = Client
        fields = ["id", "name", "email", "phone", "address", "vat_number", "metadata"]
