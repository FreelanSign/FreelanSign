# apps/core/interface/api/serializers.py (ou équivalent)
from rest_framework import serializers

from apps.core.models.audit import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "action",
            "actor",
            "actor_email",
            "target_model",
            "target_id",
            "metadata",
            "ip_address",
            "timestamp",
        ]
        read_only_fields = fields
