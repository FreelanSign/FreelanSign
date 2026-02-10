# apps/core/services/audit.py
from __future__ import annotations

import ipaddress
from typing import Any, Dict, Optional

from django.conf import settings
from django.http import HttpRequest

from apps.core.models.audit import AuditLog


def _get_ip_from_request(request: Optional[HttpRequest]) -> Optional[str]:
    if request is None:
        return None

    # AIDEV_NOTE: only trust X-Forwarded-For if we're behind a trusted proxy
    if settings.USE_X_FORWARDED_HOST:  # Django proxy settings
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            # validate ip format before trusting
            ip = xff.split(",")[0].strip()
            try:
                ipaddress.ip_address(ip)
                return ip
            except ValueError:
                pass  # Fall through to REMOTE_ADDR

    return request.META.get("REMOTE_ADDR")


def log_audit(
    *,
    action: str,
    actor=None,
    target_model: str,
    target_id: Any,
    request: Optional[HttpRequest] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """
    Helper central pour logger une action sensible.

    - action: une valeur de AuditLog.Action
    - actor: user (optionnel, peut être None pour des jobs async)
    - target_model: label logique ("Account", "Client", ...)
    - target_id: pk de l'objet (sera casté en str)
    - request: optionnel, pour récupérer l'IP
    - metadata: infos contextuelles minimales
    """
    if metadata is None:
        metadata = {}

    # AIDEV_NOTE: garde-fou RGPD : évite de dump un gros payload JSON "juste au cas où"
    # ici on peut éventuellement filtrer / whitelister les clés autorisées.

    ip = _get_ip_from_request(request)

    return AuditLog.objects.create(
        action=action,
        actor=actor,
        target_model=target_model,
        target_id=str(target_id),
        metadata=metadata,
        ip_address=ip,
    )
