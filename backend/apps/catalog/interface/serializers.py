from rest_framework import serializers

from apps.catalog.models import Area, Prestation


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "name", "created_at", "updated_at"]


class PrestationSerializer(serializers.ModelSerializer):
    area = serializers.PrimaryKeyRelatedField(read_only=True)
    area_name = serializers.CharField(source="area.name", read_only=True)
    default_rate_eur = serializers.SerializerMethodField()

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
            "created_at",
            "updated_at",
        ]

    def get_default_rate_eur(self, obj):
        return str(obj.default_rate_eur)
