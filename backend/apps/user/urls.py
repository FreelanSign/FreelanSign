from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.user.interface.views import AccountViewSet, OnboardingProfessionalView, ProfessionalUserMeView, UserViewSet

app_name = "user"

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")
router.register(r"accounts", AccountViewSet, basename="account")  # Phase 4

urlpatterns = [
    path("", include(router.urls)),  # user/ CRUD
    path("professional/me/", ProfessionalUserMeView.as_view(), name="professional-me"),
    path("onboarding-professional/", OnboardingProfessionalView.as_view(), name="onboarding-professional"),
]
