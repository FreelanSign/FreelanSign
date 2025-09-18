# apps/user/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .interface.views import OnboardingProfessionalView, ProfessionalUserMeView, ProfessionalUserViewSet

router = DefaultRouter()
router.register(r"professional", ProfessionalUserViewSet, basename="professional")
app_name = "user"

urlpatterns = [
    # on inclut simplement les routes de interface/urls.py
    path("", include("apps.user.interface.urls")),
    path("professional/me/", ProfessionalUserMeView.as_view(), name="professional-me"),
    path("onboarding/professional/", OnboardingProfessionalView.as_view(), name="onboarding-professional"),
]

urlpatterns += router.urls
