# apps/legal_terms/admin.py
from django.contrib import admin

from apps.legal_terms.adapters.persistence.models import (
    AttachedTermsModel,
    LegalProfileModel,
    LegalTemplateModel,
)


@admin.register(LegalTemplateModel)
class LegalTemplateAdmin(admin.ModelAdmin):
    """
    Admin for legal templates.
    Phase 8: Editable by staff only (no public UI).
    Templates define the structure of legal terms for different jurisdictions.
    """

    list_display = ("name", "jurisdiction", "version", "is_active", "created_at", "updated_at")
    list_filter = ("jurisdiction", "is_active")
    search_fields = ("name", "jurisdiction", "version")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "jurisdiction",
                    "version",
                    "is_active",
                )
            },
        ),
        ("Clauses", {"fields": ("clauses",)}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show all templates, ordered by most recent first
        return qs.order_by("-created_at")


@admin.register(LegalProfileModel)
class LegalProfileAdmin(admin.ModelAdmin):
    """
    Admin for legal profiles.
    Phase 8: Visible but mostly read-only (to debug support cases).
    Profiles link accounts to templates and store clause customizations.
    """

    list_display = ("account", "template", "get_jurisdiction", "created_at", "updated_at")
    list_filter = ("template__jurisdiction",)
    search_fields = ("account__display_name", "account__user__email")
    readonly_fields = ("created_at", "updated_at", "clause_overrides")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("account", "template")}),
        ("Customizations (Read-Only)", {"fields": ("clause_overrides",), "classes": ("collapse",)}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_jurisdiction(self, obj):
        return obj.template.jurisdiction if obj.template else "-"

    get_jurisdiction.short_description = "Jurisdiction"
    get_jurisdiction.admin_order_field = "template__jurisdiction"

    def has_add_permission(self, request):
        # Profiles should be created via API, not in admin
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Allow deletion only for superusers
        return request.user.is_superuser


@admin.register(AttachedTermsModel)
class AttachedTermsAdmin(admin.ModelAdmin):
    """
    Admin for attached terms (snapshots).
    Phase 8: Read-only, for debugging and audit purposes.
    These are immutable snapshots of legal terms attached to quotes.
    """

    list_display = ("quote_reference", "template_version", "created_at")
    list_filter = ("created_at",)
    search_fields = ("quote__reference", "template_version")
    readonly_fields = (
        "quote",
        "template_version",
        "rendered_html",
        "rendered_text",
        "snapshot_data",
        "created_at",
    )
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("quote", "template_version")}),
        ("Rendered Content", {"fields": ("rendered_html", "rendered_text")}),
        ("Snapshot Data", {"fields": ("snapshot_data",), "classes": ("collapse",)}),
        ("Metadata", {"fields": ("created_at",)}),
    )

    def quote_reference(self, obj):
        return obj.quote.reference if obj.quote else "-"

    quote_reference.short_description = "Quote Reference"
    quote_reference.admin_order_field = "quote__reference"

    def has_add_permission(self, request):
        # AttachedTerms are created automatically, never manually
        return False

    def has_change_permission(self, request, obj=None):
        # Snapshots are immutable
        return False

    def has_delete_permission(self, request, obj=None):
        # Allow deletion only for superusers (for cleanup)
        return request.user.is_superuser
