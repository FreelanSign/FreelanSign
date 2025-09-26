# apps/core/middleware/request_logging.py
import logging
import time
import uuid

logger = logging.getLogger("apps.core.middleware.request_logging")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())
        start = time.time()
        user_id = None
        try:
            user_id = getattr(request.user, "id", None)
        except Exception:
            pass

        logger.info(
            "request.start %s",
            request.path,
            extra={
                "request_id": request.request_id,
                "user_id": user_id,
                "method": request.method,
                "params": dict(request.GET),
            },
        )

        response = self.get_response(request)

        duration_ms = int((time.time() - start) * 1000)
        logger.info(
            "request.end %s",
            request.path,
            extra={
                "request_id": request.request_id,
                "user_id": user_id,
                "status_code": getattr(response, "status_code", None),
                "duration_ms": duration_ms,
            },
        )
        return response
