# apps/user/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models.models import ProfessionalUser, Profile

User = get_user_model()


@admin.register(ProfessionalUser)
class ProfessionalUserAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "domaine", "tjm_cents", "status_juridique", "created_at")
    search_fields = ("user__email", "name", "number_pro")
    list_filter = ("status_juridique", "domaine")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("service_types",)


# Custom User and Profile admin registrations
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-date_joined",)
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("last_login", "date_joined")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user_email", "phone", "role", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name", "phone")
    list_filter = ("role",)  # role est un TextChoices sur Profile -> ok
    readonly_fields = ("created_at", "updated_at")

    def user_email(self, obj):
        return obj.user.email

    user_email.admin_order_field = "user__email"
    user_email.short_description = "Email"
