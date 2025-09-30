# apps/core/exceptions.py
from __future__ import annotations

import logging
import traceback
from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler

logger = logging.getLogger(__name__)


def _get_req_id(request) -> str | None:
    # si ton middleware met req.id dans request (ou dans META), adapte ici
    return getattr(request, "req_id", None) or request.META.get("HTTP_X_REQUEST_ID")


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    """
    - Logge la stacktrace avec le request_id si dispo
    - Renvoie un JSON uniforme, avec 'request_id'
    """
    request = context.get("request")
    view = context.get("view")
    req_id = _get_req_id(request) if request else None

    logger.exception(
        "api.unhandled_exception",
        extra={
            "req_id": req_id,
            "path": request.path if request else None,
            "view": f"{view.__class__.__name__}" if view else None,
            "method": request.method if request else None,
        },
    )

    # Laisse DRF formater si c'est une APIException; sinon, format maison
    response = drf_default_handler(exc, context)
    if response is not None:
        # on ajoute le request_id
        data = dict(response.data)
        data["request_id"] = req_id
        response.data = data
        return response

    # Cas exception générique non-DRF
    payload = {
        "detail": "Internal server error",
        "request_id": req_id,
    }
    # En dev, optionnel: renvoyer un mini extrait pour aller plus vite
    from django.conf import settings

    if getattr(settings, "SHOW_ERRORS_IN_RESPONSE", False):
        payload["error"] = str(exc)
        payload["trace"] = traceback.format_exc().splitlines()[-3:]  # 3 dernières lignes

    return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
