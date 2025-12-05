# apps/legal_terms/tests/test_admin.py
"""
Phase 8: Minimal admin smoke tests.
Verifies that admin interfaces are properly registered and accessible.
"""
import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from apps.legal_terms.adapters.persistence.models import (
    AttachedTermsModel,
    LegalProfileModel,
    LegalTemplateModel,
)
from apps.legal_terms.admin import (
    AttachedTermsAdmin,
    LegalProfileAdmin,
    LegalTemplateAdmin,
)

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Create a superuser for admin tests."""
    return User.objects.create_superuser(email="admin@test.com", password="admin123")


@pytest.fixture
def staff_user(db):
    """Create a staff user for permission tests."""
    return User.objects.create_user(email="staff@test.com", password="staff123", is_staff=True)


@pytest.mark.django_db
class TestLegalTemplateAdmin:
    """Smoke tests for LegalTemplateAdmin."""

    def test_admin_registered(self):
        """Verify LegalTemplateModel is registered in admin."""
        from django.contrib import admin

        assert admin.site.is_registered(LegalTemplateModel)

    def test_list_display_fields(self):
        """Verify list_display has expected fields."""
        admin_instance = LegalTemplateAdmin(LegalTemplateModel, AdminSite())
        assert "name" in admin_instance.list_display
        assert "jurisdiction" in admin_instance.list_display
        assert "version" in admin_instance.list_display
        assert "is_active" in admin_instance.list_display

    def test_readonly_fields(self):
        """Verify created_at and updated_at are readonly."""
        admin_instance = LegalTemplateAdmin(LegalTemplateModel, AdminSite())
        assert "created_at" in admin_instance.readonly_fields
        assert "updated_at" in admin_instance.readonly_fields


@pytest.mark.django_db
class TestLegalProfileAdmin:
    """Smoke tests for LegalProfileAdmin."""

    def test_admin_registered(self):
        """Verify LegalProfileModel is registered in admin."""
        from django.contrib import admin

        assert admin.site.is_registered(LegalProfileModel)

    def test_list_display_fields(self):
        """Verify list_display has expected fields."""
        admin_instance = LegalProfileAdmin(LegalProfileModel, AdminSite())
        assert "account" in admin_instance.list_display
        assert "template" in admin_instance.list_display

    def test_readonly_fields(self):
        """Verify profile fields are readonly for debugging."""
        admin_instance = LegalProfileAdmin(LegalProfileModel, AdminSite())
        assert "clause_overrides" in admin_instance.readonly_fields
        assert "created_at" in admin_instance.readonly_fields
        assert "updated_at" in admin_instance.readonly_fields

    def test_add_permission_restricted(self, staff_user):
        """Verify only superusers can add profiles in admin."""
        admin_instance = LegalProfileAdmin(LegalProfileModel, AdminSite())

        # Create a mock request with staff user
        class MockRequest:
            def __init__(self, user):
                self.user = user

        staff_request = MockRequest(staff_user)
        assert not admin_instance.has_add_permission(staff_request)


@pytest.mark.django_db
class TestAttachedTermsAdmin:
    """Smoke tests for AttachedTermsAdmin."""

    def test_admin_registered(self):
        """Verify AttachedTermsModel is registered in admin."""
        from django.contrib import admin

        assert admin.site.is_registered(AttachedTermsModel)

    def test_list_display_fields(self):
        """Verify list_display has expected fields."""
        admin_instance = AttachedTermsAdmin(AttachedTermsModel, AdminSite())
        assert "quote_reference" in admin_instance.list_display
        assert "template_version" in admin_instance.list_display

    def test_all_fields_readonly(self):
        """Verify all fields are readonly (snapshots are immutable)."""
        admin_instance = AttachedTermsAdmin(AttachedTermsModel, AdminSite())
        assert "quote" in admin_instance.readonly_fields
        assert "template_version" in admin_instance.readonly_fields
        assert "rendered_html" in admin_instance.readonly_fields
        assert "snapshot_data" in admin_instance.readonly_fields

    def test_no_add_permission(self, admin_user):
        """Verify AttachedTerms cannot be added manually."""
        admin_instance = AttachedTermsAdmin(AttachedTermsModel, AdminSite())

        class MockRequest:
            def __init__(self, user):
                self.user = user

        admin_request = MockRequest(admin_user)
        assert not admin_instance.has_add_permission(admin_request)

    def test_no_change_permission(self, admin_user):
        """Verify AttachedTerms cannot be changed (immutable snapshots)."""
        admin_instance = AttachedTermsAdmin(AttachedTermsModel, AdminSite())

        class MockRequest:
            def __init__(self, user):
                self.user = user

        admin_request = MockRequest(admin_user)
        assert not admin_instance.has_change_permission(admin_request)
