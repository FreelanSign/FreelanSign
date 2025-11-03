# apps/branding/apps.py
from django.apps import AppConfig


class BrandingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.branding"
    verbose_name = "Branding"

    def ready(self):
        """Import signals to ensure they are registered."""
        # TODO: Import signals to ensure they are registered.
        # from apps.branding import signals
        pass
