# apps/core/middleware/request_logging.py
import logging
import time
import uuid

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


def _uid(request):
    user = getattr(request, "user", None)
    return getattr(user, "id", None) if user is not None else None


class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.req_id = req_id
        logger.info(
            "request.start",
            extra={
                "req": req_id,
                "user": _uid(request),  # ← safe
                "path": getattr(request, "path", None),
            },
        )

    def process_response(self, request, response):
        req_id = getattr(request, "req_id", None)
        if req_id:
            response["X-Request-ID"] = req_id
        logger.info(
            "request.end",
            extra={
                "req": req_id,
                "user": _uid(request),  # ← safe
                "path": getattr(request, "path", None),
            },
        )
        return response

    def process_exception(self, request, exception):
        logger.exception(
            "request.exception",
            extra={
                "req": getattr(request, "req_id", None),
                "user": _uid(request),  # ← safe
                "path": getattr(request, "path", None),
            },
        )
        return None
