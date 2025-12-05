"""
URL routing for legal terms API.
"""

from django.urls import path

from apps.legal_terms.interface.api.views import (
    LegalProfileView,
    LegalTermsPreviewView,
)

app_name = "legal_terms"

urlpatterns = [
    path("profile/", LegalProfileView.as_view(), name="legal-profile"),
    path("preview/", LegalTermsPreviewView.as_view(), name="legal-preview"),
]
