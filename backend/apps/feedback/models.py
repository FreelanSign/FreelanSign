# apps/feedback/models.py
import uuid

from django.conf import settings
from django.db import models


class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ("BUG", "Bug"),
        ("SUGGESTION", "Suggestion"),
        ("QUESTION", "Question"),
        ("KUDOS", "Kudos"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    message = models.TextField()
    email = models.EmailField()
    page_url = models.URLField(max_length=500, blank=True, default="")
    app_version = models.CharField(max_length=50, blank=True, default="")
    user_agent = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"

    def __str__(self):
        return f"[{self.category}] {self.email} — {self.message[:50]}"
