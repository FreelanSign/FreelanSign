# apps/user/admin.py
from django.contrib import admin

from .models.models import ProfessionalUser, Profile


@admin.register(ProfessionalUser)
class ProfessionalUserAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "domaine", "tjm_cents", "status_juridique", "created_at")
    search_fields = ("user__email", "name", "number_pro")
    list_filter = ("status_juridique", "domaine")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("service_types",)
