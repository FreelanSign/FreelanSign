from django.apps import AppConfig


class QuoteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.quote"
    verbose_name = "Quotes"

    def ready(self):
        from . import signals # noqa: F401
