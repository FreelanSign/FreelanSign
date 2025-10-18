# apps/quote/interface/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import QuotePreviewPdfView, QuoteViewSet

app_name = "quote"
router = DefaultRouter()
router.register(r"", QuoteViewSet, basename="quote")

urlpatterns = [
    # endpoint pour la prévisualisation PDF
    path("preview-pdf/", QuotePreviewPdfView.as_view(), name="quote_preview_pdf"),
    # routes par défaut
] + router.urls
