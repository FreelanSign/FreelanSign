# apps/client/interface/urls.py
from rest_framework.routers import DefaultRouter

from .views import StandardClientViewSet

router = DefaultRouter()
router.register(r"", StandardClientViewSet, basename="client")

urlpatterns = router.urls
