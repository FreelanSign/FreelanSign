# apps/core/interface/api/audit_views.py
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle

from apps.core.models.audit import AuditLog

from .serializers import AuditLogSerializer


class AuditLogPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 200


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint admin pour consulter les logs d'audit.

    - GET /api/admin/audit-logs/
    - GET /api/admin/audit-logs/{id}/
    """

    queryset = AuditLog.objects.select_related("actor").all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    throttle_classes = [UserRateThrottle]  # 100/hour default
    throttle_scope = "audit-logs"
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["timestamp", "action"]
    ordering = ["-timestamp"]
    pagination_class = AuditLogPagination

    def get_queryset(self):
        """
        Filter audit logs by optional query parameters:
        - action: AuditLog.Action enum value
        - target_model: "Account" | "Client" | etc.
        - target_id: UUID or int (stringified)
        """
        qs = super().get_queryset()
        action = self.request.query_params.get("action")
        if action and action in AuditLog.Action.values:  # Validate against enum
            qs = qs.filter(action=action)
        target_model = self.request.query_params.get("target_model")
        ALLOWED_MODEL = {"Account", "Client", "Quote"}  # Whitelist models
        if target_model and target_model in ALLOWED_MODEL:
            qs = qs.filter(target_model=target_model)
        target_id = self.request.query_params.get("target_id")
        if target_id and target_id.isalnum():  # Basic UUID/int validation
            qs = qs.filter(target_id=str(target_id))

        return qs
