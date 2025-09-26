import logging

from rest_framework import serializers

from apps.catalog.models import Area, Prestation
from apps.core.logging import get_logger

logger = logging.getLogger(__name__)


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "name", "created_at", "updated_at"]


class PrestationSerializer(serializers.ModelSerializer):
    area = serializers.PrimaryKeyRelatedField(read_only=True)
    area_name = serializers.CharField(source="area.name", read_only=True)
    default_rate_eur = serializers.SerializerMethodField()
    custom = serializers.BooleanField(read_only=True)
    professional_user = serializers.IntegerField(source="professional_user_id", read_only=True)

    class Meta:
        model = Prestation
        fields = [
            "id",
            "area",
            "area_name",
            "name",
            "description",
            "weight_days",
            "default_rate_cents",
            "default_rate_eur",
            "status",
            "custom",
            "professional_user",
            "created_at",
            "updated_at",
        ]

    def get_default_rate_eur(self, obj):
        request = self.context.get("request")
        logger = get_logger(__name__, request)
        try:
            val = str(obj.default_rate_eur)
            logger.debug("get_default_rate_eur: id=%s default_rate_eur=%s", getattr(obj, "id", None), val)
            return val
        except Exception:
            logger.exception("Erreur lors du calcul de default_rate_eur pour prestation id=%s", getattr(obj, "id", None))
