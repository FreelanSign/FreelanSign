# apps/user/interface/auth_views.py
import logging
from datetime import datetime, timezone
from threading import Thread

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

from apps.user.adapters.persistence.django_user_repository import DjangoUserRepository
from apps.user.adapters.providers.logging_token_sender import LoggingTokenSender
from apps.user.adapters.providers.smtp_token_provider import SmtpTokenSender
from apps.user.application.dto.user_inputs import ResetPasswordInput
from apps.user.application.usecases.request_password_reset import RequestPasswordReset
from apps.user.application.usecases.reset_password import ResetPassword
from apps.user.application.usecases.send_verification_email import SendVerificationEmail
from apps.user.application.usecases.verify_email import InvalidVerificationTokenError, VerifyEmail
from apps.user.interface.errors_handler import UserErrorHandler
from config import settings

from .serializers import LogoutSerializer, RequestPasswordResetSerializer, ResetPasswordSerializer, VerifyEmailSerializer

logger = logging.getLogger(__name__)


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
    },
)
class AuthLogoutView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    def post(self, request):
        ser = LogoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            token = RefreshToken(ser.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            pass  # Token already invalid/expired — user is already logged out
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


@extend_schema(
    tags=["Auth"],
    summary="Request password reset",
    description="Sends a reset link to the user if the email exists. The token is valid for 30 minutes.",
    responses={
        200: OpenApiResponse({"detail": "If the email exists, a reset link was sent."}),
        400: OpenApiResponse({"email": ["This field is required."]}),
    },
)
class RequestPasswordResetView(APIView):
    """
    RequestPasswordResetView handles password reset token generation.

    Public endpoint (no auth). If the email matches a user, a reset link
    is sent via the configured TokenSender.
    """

    permission_classes = [AllowAny]
    throttle_classes = {
        ScopedRateThrottle,
    }
    throttle_scope = "auth"

    def post(self, request):
        """
        Accepts an email and triggers the password reset process.

        Returns:
            200 OK - Always, even if the email is unknown (for security).
            400 Bad Request - If the email field is missing or invalid.
        """
        logger.info("RAW BODY: %s", request.body)
        logger.info("REQUEST DATA: %s", request.data)

        ser = RequestPasswordResetSerializer(data=request.data)
        if not ser.is_valid():
            logger.warning("Invalid password reset request: %s", ser.errors)
            return Response(
                {
                    "error": "INVALID_INPUT",
                    "message": "Invalid request payload",
                    "detail": ser.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info("Validated input: %s", ser.validated_data)

        try:
            use_case = RequestPasswordReset(
                user_repository=DjangoUserRepository(),
                token_sender=SmtpTokenSender(
                    reset_base_url=settings.RESET_PASSWORD_URL,
                    from_email=settings.EMAIL_FROM,
                ),
            )
            # Execute password reset in background thread (non-blocking)
            thread = Thread(
                target=use_case.execute,
                kwargs={"email": ser.validated_data["email"]},
                daemon=True,
            )
            thread.start()

            return Response(
                {"detail": "If the email exists, a reset link was sent."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return UserErrorHandler.handle_error(e)


from drf_spectacular.utils import OpenApiResponse, extend_schema


@extend_schema(
    tags=["Auth"],
    summary="Reset password using token",
    description=(
        "Accepts a signed token (from the password reset email) and a new password. "
        "If the token is valid and not expired (2 hours), the user's password is updated. "
        "This endpoint does not require authentication."
    ),
    request=ResetPasswordSerializer,
    responses={
        200: OpenApiResponse({"detail": "Password has been reset."}),
        400: OpenApiResponse({"token": ["This field is required."], "new_password": ["This field is required."]}),
        404: OpenApiResponse({"error": "USER_NOT_FOUND", "message": "User not found", "detail": "..."}),
        422: OpenApiResponse({"error": "INVALID_PASSWORD", "message": "Password too weak", "detail": "..."}),
    },
)
class ResetPasswordView(APIView):
    """
    ResetPasswordView handles password reset via signed token.

    This public endpoint accepts a reset token and a new password.
    If the token is valid and not expired, the password is updated.
    No authentication is required to use this endpoint.
    """

    permission_classes = [AllowAny]
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"

    def post(self, request):
        """
        Validates the signed token and updates the user's password.

        Returns:
            200 OK - Password has been successfully reset.
            400 Bad Request - Missing or invalid fields.
            404 Not Found - Invalid or expired token.
            422 Unprocessable Entity - Password does not meet complexity rules.
        """
        ser = ResetPasswordSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            input_dto = ResetPasswordInput(
                token=ser.validated_data["token"],
                new_password=ser.validated_data["new_password"],
            )

            use_case = ResetPassword(
                user_repository=DjangoUserRepository(),
                token_max_age_sec=2 * 3600,  # 🔐 2 hours validity
            )
            use_case.execute(input_dto)

            return Response({"detail": "Password has been reset."}, status=status.HTTP_200_OK)

        except Exception as e:
            return UserErrorHandler.handle_error(e)


@extend_schema(
    tags=["Auth"],
    summary="Verify email address",
    request=VerifyEmailSerializer,
    responses={
        200: OpenApiResponse({"detail": "Email verified."}),
        400: OpenApiResponse({"detail": "Token invalide ou expire"}),
    },
)
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        ser = VerifyEmailSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            use_case = VerifyEmail(user_repository=DjangoUserRepository())
            use_case.execute(token=ser.validated_data["token"])
            return Response({"detail": "Email verified."}, status=status.HTTP_200_OK)
        except InvalidVerificationTokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Auth"],
    summary="Resend verification email",
    responses={
        200: OpenApiResponse({"detail": "Verification email sent."}),
    },
)
class ResendVerificationEmailView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        user = request.user
        if user.email_verified:
            return Response({"detail": "Email already verified."}, status=status.HTTP_200_OK)

        try:
            # Send verification email in background thread (non-blocking)
            thread = Thread(
                target=SendVerificationEmail(
                    verification_base_url=settings.EMAIL_VERIFICATION_URL,
                    from_email=settings.EMAIL_FROM,
                ).execute,
                kwargs={"user_id": user.id, "email": user.email},
                daemon=True,
            )
            thread.start()
            return Response({"detail": "Verification email sent."}, status=status.HTTP_200_OK)
        except Exception as e:
            return UserErrorHandler.handle_error(e)
