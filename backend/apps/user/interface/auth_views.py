# apps/user/interface/auth_views.py

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


@extend_schema(
    tags=["Auth"],
    summary="Login with email and password",
    description="Obtain JWT tokens using email and password.",
    request=TokenObtainPairSerializer,
    responses={200: TokenObtainPairSerializer},
)
class AuthLoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"


@extend_schema(
    tags=["Auth"],
    summary="Refresh access token",
    request=TokenRefreshSerializer,
    responses={200: TokenRefreshSerializer},
)
class AuthRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"
