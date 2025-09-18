from django.contrib import admin

from .models import Area, Prestation, PrestationStatus


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Prestation)
class PrestationAdmin(admin.ModelAdmin):
    """Interface d'administration pour les prestations."""

    list_display = ("name", "area", "status", "weight_days", "default_rate_cents")
    list_filter = ("area", "status")
    search_fields = ("name", "description")
    ordering = ("area__name", "name")
    autocomplete_fields = ("area",)
    actions = ("mark_active", "mark_archived", "mark_draft")

    @admin.action(description="Marquer sélection comme ACTIVE")
    def mark_active(self, request, queryset):
        queryset.update(status=PrestationStatus.ACTIVE)

    @admin.action(description="Marquer sélection comme ARCHIVED")
    def mark_archived(self, request, queryset):
        queryset.update(status=PrestationStatus.ARCHIVED)

    @admin.action(description="Marquer sélection comme DRAFT")
    def mark_draft(self, request, queryset):
        queryset.update(status=PrestationStatus.DRAFT)
