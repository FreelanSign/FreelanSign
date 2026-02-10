"""
Smoke tests for legal_terms app.
Verify app is properly configured and can run migrations.
"""

import pytest
from django.apps import apps


@pytest.mark.django_db
class TestLegalTermsAppSmoke:
    """Smoke tests to verify legal_terms app is configured correctly."""

    def test_app_is_installed(self):
        """Verify legal_terms app is installed."""
        assert apps.is_installed("apps.legal_terms")

    def test_app_config_loads(self):
        """Verify legal_terms AppConfig loads without errors."""
        app_config = apps.get_app_config("legal_terms")
        assert app_config is not None
        assert app_config.name == "apps.legal_terms"
