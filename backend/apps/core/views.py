import logging

from django.db import connection
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring systems.
    Checks database connectivity and returns system status.
    """
    health_status = {"status": "healthy", "checks": {}}

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status["checks"]["database"] = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = "failed"
        return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # If all checks pass
    return Response(health_status, status=status.HTTP_200_OK)
