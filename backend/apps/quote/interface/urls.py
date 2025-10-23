# apps/quote/interface/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QuotePreviewPdfView, QuoteViewSet

app_name = "quote"
router = DefaultRouter()
router.register(r"", QuoteViewSet, basename="quote")

urlpatterns = [
    # endpoint pour la prévisualisation PDF
    path("preview-pdf/", QuotePreviewPdfView.as_view(), name="quote-preview-pdf"),
    # routes par défaut via router (inclut automatiquement l'action download_pdf)
    path("", include(router.urls)),
]
