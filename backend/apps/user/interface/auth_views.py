# apps/user/interface/auth_views.py
from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

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
    summary="Logout (invalidate refresh token)",
    request=LogoutSerializer,
    responses={
        204: OpenApiResponse({"detail": "Logged out successfully"}),
        400: OpenApiResponse({"refresh": ["Invalid token"]}),
    },
)
class AuthLogoutView(APIView):
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
    responses={
        200: TokenRefreshSerializer,
        401: OpenApiResponse({"detail": "Token reuse detected"}),
        400: OpenApiResponse({"refresh": ["This field is required."]}),
    },
)
class SecureAuthRefreshView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    def _get_presented(self, raw: str) -> RefreshToken:
        """Decode un refresh token brut en Raise TokenError si invalide/expiré."""
        return RefreshToken(raw)

    def _is_blacklisted(self, jti: str) -> bool:
        """Vérifie si un token est blacklisté."""
        try:
            ot = OutstandingToken.objects.get(jti=jti)
            return BlacklistedToken.objects.filter(token=ot).exists()
        except OutstandingToken.DoesNotExist:
            return False

    def _ensure_outstanding_token(self, presented: RefreshToken) -> OutstandingToken:
        """Assure qu'un OutstandingToken existe pour ce resfresh token."""
        jti = presented["jti"]
        user_id = presented["user_id"]
        exp = datetime.fromtimestamp(presented["exp"], tz=timezone.utc)
        iat = datetime.fromtimestamp(presented["iat"], tz=timezone.utc)
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise TokenError("User not found")

        # Créer (si besoin) l'outstanding token
        ot, created = OutstandingToken.objects.get_or_create(
            jti=jti,
            defaults={
                "user": user,
                "token": str(presented),
                "created_at": iat,
                "expires_at": exp,
            },
        )
        return ot

    def _blacklist_token(self, outstanding_token: OutstandingToken) -> None:
        """Blackliste un OutstandingToken."""
        BlacklistedToken.objects.get_or_create(token=outstanding_token)

    def _revoke_all_user_token(self, user) -> None:
        """Révoque tous les tokens d'un utilisateur (blacklist)."""
        user_tokens = OutstandingToken.objects.filter(user=user)
        for token in user_tokens:
            self._blacklist_token(token)

    def post(self, request):
        raw = request.data.get("refresh")
        if not raw:
            return Response({"refresh": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        # Validation du token
        try:
            presented = self._get_presented(raw)
        except TokenError:
            return Response({"detail": "Token is invalid or expired"}, status=status.HTTP_401_UNAUTHORIZED)

        jti = presented["jti"]

        # Vérification si le token est déjà blacklisté
        if self._is_blacklisted(jti):
            # Révoque toute la "session" restante de l'utilisateur par sûreté
            try:
                ot = OutstandingToken.objects.get(jti=jti)
                self._revoke_all_user_token(ot.user)
            except OutstandingToken.DoesNotExist:
                # Rien à révoquer si on ne suit pas ce jti, la 401 reste correcte
                pass
            return Response({"detail": "Token reuse detected"}, status=status.HTTP_401_UNAUTHORIZED)

        # Assurer que l'Outstanding token existe avant la rotation
        try:
            outstanding_token = self._ensure_outstanding_token(presented)
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        # Effectuer la rotation
        serializer = TokenRefreshSerializer(data={"refresh": raw})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response({"detail": "Token is invalid or expired"}, status=status.HTTP_401_UNAUTHORIZED)

        data = serializer.validated_data

        # Blacklister l'ancien token après rotation réussie
        self._blacklist_token(outstanding_token)

        new_refresh = data.get("refresh")
        if new_refresh:
            try:
                new_presented = self._get_presented(new_refresh)
                self._ensure_outstanding_token(new_presented)
            except TokenError:
                pass

        return Response(data, status=status.HTTP_200_OK)
