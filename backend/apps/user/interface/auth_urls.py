# apps/user/interface/auth_urls.py
from django.urls import path

from apps.user.interface.auth_views import (
    AuthLoginView,
    AuthLogoutView,
    RequestPasswordResetView,
    ResendVerificationEmailView,
    ResetPasswordView,
    SecureAuthRefreshView,
    VerifyEmailView,
)

urlpatterns = [
    path("login/", AuthLoginView.as_view(), name="auth-login"),
    path("logout/", AuthLogoutView.as_view(), name="auth-logout"),
    path("refresh/", SecureAuthRefreshView.as_view(), name="auth-refresh"),
    path("request-password-reset/", RequestPasswordResetView.as_view(), name="auth-request-password-reset"),
    path("reset-password/", ResetPasswordView.as_view(), name="auth-reset-password"),
    path("verify-email/", VerifyEmailView.as_view(), name="auth-verify-email"),
    path("resend-verification/", ResendVerificationEmailView.as_view(), name="auth-resend-verification"),
]
