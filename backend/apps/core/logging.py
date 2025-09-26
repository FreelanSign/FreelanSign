# apps/core/logging.py
import logging


class RequestLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = self.extra.copy()
        if "extra" in kwargs:
            extra.update(kwargs["extra"])
        kwargs["extra"] = extra
        return msg, kwargs


def get_logger(name=__name__, request=None):
    logger = logging.getLogger(name)
    extra = {}
    if request is not None:
        extra["request_id"] = getattr(request, "request_id", None)
        try:
            extra["user_id"] = getattr(request.user, "id", None)
        except Exception:
            extra["user_id"] = None
    return RequestLoggerAdapter(logger, extra)


class ContextFilter(logging.Filter):
    """
    Ajoute des attributs request_id / user_id par défaut si absents pour éviter KeyError
    dans les formatters qui les référencent.
    """

    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = None
        if not hasattr(record, "user_id"):
            record.user_id = None
        return True
