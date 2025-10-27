# apps/user/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.user.interface.views import (
    OnboardingProfessionalView,
    ProfessionalUserMeView,
    UserViewSet,
)

app_name = "user"

router = DefaultRouter()
# Users CRUD-like (list, create, me, etc.)
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    # /api/user/ -> router (UserViewSet)
    path("", include(router.urls)),
    # Professional "me"
    path("professional/me/", ProfessionalUserMeView.as_view(), name="professional-me"),
    # Onboarding pro
    path("onboarding-professional/", OnboardingProfessionalView.as_view(), name="onboarding-professional"),
]
