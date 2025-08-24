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
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

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

@extend_schema(
    tags=["Auth"],
    summary="Refresh access token (with rotation and reuse detection)",
    request=TokenRefreshSerializer,
    responses={200: TokenRefreshSerializer, 401: OpenApiResponse({"detail": "Reuse Token detected!"})},
)
class SecureAuthRefreshView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        raw = serializer.validated_data.get("refresh")
        try:
            # on inspecte le refresh en entrée
            presented_token = RefreshToken(raw)
            jti = presented_token["jti"]
            # 1) reuse detection
            try:
                ot = OutstandingToken.objects.get(jti=jti)
                if BlacklistedToken.objects.filter(token=ot).exists():
                    for t in OutstandingToken.objects.filter(user=ot.user):
                        BlacklistedToken.objects.get_or_create(token=t)
                    return Response({"detail": "Reuse Token detected!"}, status=status.HTTP_401_UNAUTHORIZED)
            except OutstandingToken.DoesNotExist:
                pass

            # 2) cas nominal on délègue au SimpleJwt
            data = serializer.validated_data
            return Response(data, status=status.HTTP_200_OK)
        except TokenError:
            # Token mal formé/expiré -> réponse standard
            return Response({"detail": "Token is invalid or expired"}, status=status.HTTP_401_UNAUTHORIZED)
