# apps/client/interface/serializers.py
from __future__ import annotations

from typing import Optional

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.client.application.dto.client_inputs import (
    CreateClientInput,
    ListClientsInput,
    UpdateClientInput,
)
from apps.client.application.dto.client_viewmodels import ClientViewModel
from apps.client.models import Client  # conservé pour compat (ex: admin)

# Note: on n'utilise plus ModelSerializer pour l'API publique

User = get_user_model()


# =========================
# Inputs (API -> DTO)
# =========================


class ClientCreateInputSerializer(serializers.Serializer):
    """
    Payload d'entrée pour créer un client (API -> DTO).
    owner_id est injecté depuis request.user dans la view.
    """

    name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=64)
    # Structured address fields
    address_line1 = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    address_line2 = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    postal_code = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=2)
    company = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    vat_number = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=64)
    metadata = serializers.DictField(required=False, allow_empty=True)

    def validate_name(self, value: str) -> str:
        # Validation "forme" (UI) côté API, la règle métier (non vide trim) est aussi appliquée en domain.policy
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("Client name cannot be empty.")
        return v

    def to_dto(self, *, owner_id: int) -> CreateClientInput:
        data = self.validated_data
        return CreateClientInput(
            owner_id=owner_id,
            name=data["name"],
            email=data.get("email"),
            phone=data.get("phone"),
            address_line1=data.get("address_line1"),
            address_line2=data.get("address_line2"),
            city=data.get("city"),
            postal_code=data.get("postal_code"),
            country=data.get("country"),
            company=data.get("company"),
            vat_number=data.get("vat_number"),
            metadata=data.get("metadata") or {},
        )


class ClientUpdateInputSerializer(serializers.Serializer):
    """
    Payload d'entrée pour mettre à jour un client (API -> DTO).
    Tous les champs sont optionnels (supporte PATCH).
    """

    name = serializers.CharField(required=False, allow_blank=False, max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=64)
    # Structured address fields
    address_line1 = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    address_line2 = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    postal_code = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=2)
    company = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    vat_number = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=64)
    metadata = serializers.DictField(required=False, allow_empty=True)

    def validate_name(self, value: str) -> str:
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("Client name cannot be empty.")
        return v

    def to_dto(self, *, client_id: str) -> UpdateClientInput:
        d = self.validated_data
        return UpdateClientInput(
            client_id=client_id,
            name=d.get("name") if "name" in d else None,
            email=d.get("email") if "email" in d else None,
            phone=d.get("phone") if "phone" in d else None,
            address_line1=d.get("address_line1") if "address_line1" in d else None,
            address_line2=d.get("address_line2") if "address_line2" in d else None,
            city=d.get("city") if "city" in d else None,
            postal_code=d.get("postal_code") if "postal_code" in d else None,
            country=d.get("country") if "country" in d else None,
            company=d.get("company") if "company" in d else None,
            vat_number=d.get("vat_number") if "vat_number" in d else None,
            metadata=d.get("metadata") if "metadata" in d else None,
        )


class ClientListQuerySerializer(serializers.Serializer):
    """
    Query params pour la liste (API -> DTO).
    Laisse la pagination à DRF (limit/offset/page).
    """

    owner = serializers.IntegerField(required=False)
    search = serializers.CharField(required=False, allow_blank=True)
    ordering = serializers.CharField(required=False)

    def to_dto(self) -> ListClientsInput:
        d = self.validated_data
        return ListClientsInput(
            owner_id=d.get("owner"),
            search=d.get("search"),
            ordering=d.get("ordering") or "-created_at",
        )


# =========================
# Outputs (VM -> API)
# =========================


class ClientOutputSerializer(serializers.Serializer):
    """
    Serializer de sortie mappé sur ClientViewModel (pas un modèle Django).
    Garde le contrat actuel : champ 'owner' = id (via owner_id).
    """

    id = serializers.UUIDField()
    owner = serializers.IntegerField(source="owner_id")
    account_id = serializers.IntegerField()  # Phase 5
    name = serializers.CharField()
    email = serializers.CharField(allow_null=True, allow_blank=True)
    phone = serializers.CharField(allow_null=True, allow_blank=True)
    # Structured address fields
    address_line1 = serializers.CharField(allow_null=True, allow_blank=True)
    address_line2 = serializers.CharField(allow_null=True, allow_blank=True)
    city = serializers.CharField(allow_null=True, allow_blank=True)
    postal_code = serializers.CharField(allow_null=True, allow_blank=True)
    country = serializers.CharField(allow_null=True, allow_blank=True)
    company = serializers.CharField(allow_null=True, allow_blank=True)
    vat_number = serializers.CharField(allow_null=True, allow_blank=True)
    metadata = serializers.DictField()
    created_at = serializers.CharField()  # VM fournit déjà un ISO string
    updated_at = serializers.CharField()

    @staticmethod
    def from_vm(vm: ClientViewModel) -> "ClientOutputSerializer":
        """
        Helper pratique si tu veux instancier depuis une VM directement.
        """
        return ClientOutputSerializer(instance=vm)


# =========================
# Compat/lecture "enrichie"
# =========================


class ClientReadSerializer(serializers.Serializer):
    """
    Ancienne variante "read" mais version VM-based.
    (id, name, email, phone, address, vat_number, metadata)
    """

    id = serializers.UUIDField()
    name = serializers.CharField()
    email = serializers.CharField(allow_null=True, allow_blank=True)
    phone = serializers.CharField(allow_null=True, allow_blank=True)
    # Structured address fields
    address_line1 = serializers.CharField(allow_null=True, allow_blank=True)
    address_line2 = serializers.CharField(allow_null=True, allow_blank=True)
    city = serializers.CharField(allow_null=True, allow_blank=True)
    postal_code = serializers.CharField(allow_null=True, allow_blank=True)
    country = serializers.CharField(allow_null=True, allow_blank=True)
    company = serializers.CharField(allow_null=True, allow_blank=True)
    vat_number = serializers.CharField(allow_null=True, allow_blank=True)
    metadata = serializers.DictField()
