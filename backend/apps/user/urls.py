from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.user.interface.views import AccountViewSet, UserViewSet

app_name = "user"

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")
router.register(r"accounts", AccountViewSet, basename="account")

urlpatterns = [
    path("", include(router.urls)),
]
