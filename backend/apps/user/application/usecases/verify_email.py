# apps/user/application/usecases/verify_email.py
import logging

from django.core import signing

from apps.user.application.ports.user_repository import UserRepository

logger = logging.getLogger(__name__)

SIGNER_SALT = "user.email-verify"
TOKEN_MAX_AGE_SEC = 2 * 3600  # 2 hours


class InvalidVerificationTokenError(Exception):
    pass


class VerifyEmail:
    def __init__(self, *, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, *, token: str) -> None:
        try:
            payload = signing.loads(token, salt=SIGNER_SALT, max_age=TOKEN_MAX_AGE_SEC)
        except (signing.BadSignature, signing.SignatureExpired) as e:
            logger.warning("Invalid or expired verification token: %s", e)
            raise InvalidVerificationTokenError("Token invalide ou expire")

        user_id = payload.get("user_id")
        if not user_id:
            raise InvalidVerificationTokenError("Token invalide")

        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise InvalidVerificationTokenError("Utilisateur introuvable")

        self.user_repository.set_email_verified(user_id, verified=True)
        logger.info("Email verified for user_id=%s", user_id)
