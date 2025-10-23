# apps/catalog/interface/serializers.py
"""
Serializers DRF pour l'API catalog.
Gèrent la validation d'entrée et la sérialisation de sortie.
"""
import logging

from rest_framework import serializers

from apps.catalog.application.dto.prestation_viewmodels import (
    AreaViewModel,
    PrestationViewModel,
)
from apps.catalog.models import Area, Prestation

logger = logging.getLogger(__name__)


class AreaSerializer(serializers.ModelSerializer):
    """Serializer pour Area (classique)."""

    class Meta:
        model = Area
        fields = ["id", "name", "created_at", "updated_at"]


class PrestationSerializer(serializers.Serializer):
    """
    Serializer pour Prestation.
    Peut sérialiser soit un modèle Prestation, soit un PrestationViewModel.
    """

    id = serializers.IntegerField(read_only=True)
    area = serializers.IntegerField(source="area_id", read_only=True)
    area_name = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=120)
    description = serializers.CharField(allow_blank=True, required=False)
    weight_days = serializers.IntegerField(min_value=1)
    default_rate_cents = serializers.IntegerField(min_value=0)
    default_rate_eur = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)
    custom = serializers.BooleanField(read_only=True)
    professional_user = serializers.IntegerField(source="professional_user_id", read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def get_default_rate_eur(self, obj) -> str:
        """
        Retourne le tarif en euros formaté.
        Gère à la fois les modèles Prestation et les ViewModels.
        """
        try:
            # Si c'est un ViewModel
            if isinstance(obj, PrestationViewModel):
                return obj.default_rate_display

            # Si c'est un modèle Prestation
            if hasattr(obj, "default_rate_eur"):
                return str(obj.default_rate_eur)

            # Fallback: calculer depuis default_rate_cents
            if hasattr(obj, "default_rate_cents"):
                euros = obj.default_rate_cents / 100
                return f"{euros:.2f}"

            logger.warning("Impossible de calculer default_rate_eur pour objet: %s", type(obj))
            return "0.00"

        except Exception:
            logger.exception("Erreur lors du calcul de default_rate_eur pour id=%s", getattr(obj, "id", None))
            return "0.00"


class PrestationCreateSerializer(serializers.Serializer):
    """Serializer pour la création de prestation (input)."""

    area_id = serializers.IntegerField(min_value=1)
    name = serializers.CharField(max_length=120, min_length=3)
    description = serializers.CharField(allow_blank=True, required=False, default="")
    weight_days = serializers.IntegerField(min_value=1)
    default_rate_cents = serializers.IntegerField(min_value=0)
    status = serializers.ChoiceField(choices=["DRAFT", "ACTIVE", "ARCHIVED"], default="DRAFT")

    def validate_name(self, value):
        """Valide le nom."""
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom ne peut pas être vide")
        return value.strip()


class PrestationUpdateStatusSerializer(serializers.Serializer):
    """Serializer pour changer le statut d'une prestation."""

    status = serializers.ChoiceField(choices=["DRAFT", "ACTIVE", "ARCHIVED"], required=True)
