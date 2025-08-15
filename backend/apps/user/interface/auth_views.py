# apps/user/interface/auth_views.py

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import LogoutSerializer


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


@extend_schema(
    tags=["Auth"],
    summary="Logout (invalidate refresh token)",
    request=LogoutSerializer,
    responses={
        204: OpenApiResponse({"detail": "Logged out successfully"}),
        400: OpenApiResponse({"refresh": ["Invalid token"]}),
    },
)
class AuthLogoutView(APIView):
    """Logout the user by invalidating the refresh token."""

    permission_classes = (IsAuthenticated,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    def post(self, request):
        ser = LogoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            token = RefreshToken(ser.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            return Response({"refresh": ["Invalid token"]}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Logged out successfully"}, status=status.HTTP_204_NO_CONTENT)
