# apps/catalog/interface/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AreaViewSet, PrestationViewSet

app_name = "catalog"

router = DefaultRouter()
# basename simples et prévisibles
router.register(r"areas", AreaViewSet, basename="areas")
router.register(r"prestations", PrestationViewSet, basename="prestations")

urlpatterns = [
    path("", include(router.urls)),
]
