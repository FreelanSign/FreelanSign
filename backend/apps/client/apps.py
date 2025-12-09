from django.apps import AppConfig


class ClientConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.client"
    label = "client"

    def ready(self):
        """Import signals when Django starts."""
        import apps.client.signals  # noqa: F401
