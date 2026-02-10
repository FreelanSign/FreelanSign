# apps/feedback/admin.py
from django.contrib import admin

from apps.feedback.models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("category", "email", "message_preview", "page_url", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("email", "message")
    readonly_fields = ("id", "user", "email", "category", "message", "page_url", "app_version", "user_agent", "created_at")
    ordering = ("-created_at",)

    def message_preview(self, obj):
        return obj.message[:80] + "..." if len(obj.message) > 80 else obj.message

    message_preview.short_description = "Message"
