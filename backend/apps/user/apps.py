from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.user"
    label = "user"


def ready(self):
    from . import signals  # Import signals to ensure they are registered
