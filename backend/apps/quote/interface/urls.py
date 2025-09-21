# apps/quote/interface/urls.py
from rest_framework.routers import DefaultRouter

from .views import QuoteViewSet

app_name = "quote"
router = DefaultRouter()
router.register(r"", QuoteViewSet, basename="quote")

urlpatterns = router.urls
