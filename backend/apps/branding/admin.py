# apps/branding/admin.py
from django.contrib import admin

from .models import BrandTheme


@admin.register(BrandTheme)
class BrandThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "account", "is_active", "created_at", "updated_at")
    search_fields = ("name", "account__email")
    list_filter = ("is_active",)
    ordering = ("-created_at",)

    fieldsets = (
        ("Basic Information", {"fields": ("id", "account", "name", "is_active")}),
        ("Customization", {"fields": ("colors", "typography", "spacing", "logo")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
