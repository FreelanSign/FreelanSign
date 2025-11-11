# apps/user/application/usecases/request_password_reset.py
import logging
from datetime import timedelta

from django.core import signing
from django.utils import timezone

from apps.user.application.ports.token_sender import TokenSender
from apps.user.application.ports.user_repository import UserRepository

logger = logging.getLogger(__name__)


class RequestPasswordReset:
    """
    Use case: request password reset by email.
    If user exists, send a signed token via TokenSender.
    """

    TOKEN_EXPIRATION_HOURS = 2
    SIGNER_SALT = "user.reset"

    def __init__(self, user_repository: UserRepository, token_sender: TokenSender):
        self.user_repository = user_repository
        self.token_sender = token_sender

    def execute(self, email: str) -> None:
        """
        Executes the password reset request.
        Sends an email if the user exists, silently skips otherwise.

        Args:
            email: User's email.
        """
        email_clean = (email or "").strip().lower()
        logger.info("RequestPasswordReset: received request for email=%s", email_clean)

        user = self.user_repository.get_by_email(email=email_clean)
        if not user:
            logger.info("RequestPasswordReset: no user found for email=%s", email_clean)
            return

        payload = {
            "user_id": user.id,
            "ts": timezone.now().timestamp(),
        }

        token = signing.dumps(payload, salt=self.SIGNER_SALT)
        logger.debug("RequestPasswordReset: generated token for user_id=%s", user.id)
        self.token_sender.send_reset_link(email=user.email, token=token)
        logger.info("RequestPasswordReset: link sent for user_id=%s", user.id)
