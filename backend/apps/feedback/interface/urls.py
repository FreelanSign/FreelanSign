# apps/feedback/interface/urls.py
from django.urls import path

from apps.feedback.interface.views import CreateFeedbackView

urlpatterns = [
    path("", CreateFeedbackView.as_view(), name="feedback-create"),
]
