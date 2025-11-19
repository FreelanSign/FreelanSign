# apps/user/adapters/providers/smtp_token_provider.py

import logging

from django.core.mail import EmailMessage

from apps.user.application.ports.token_sender import TokenSender

logger = logging.getLogger(__name__)


class SmtpTokenSender(TokenSender):
    """
    Sends reset tokens via email using Django's SMTP backend.
    """

    def __init__(self, reset_base_url: str, from_email: str):
        self.reset_base_url = reset_base_url
        self.from_email = from_email

    def send_reset_link(self, email: str, token: str) -> None:
        link = f"{self.reset_base_url}?token={token}"
        subject = "Password Reset Instructions"
        body = (
            "Hello,\n\n" f"To reset your password, click here:\n{link}\n\n" "If you did not request this, ignore this email."
        )

        logger.info("Sending password reset email to %s: %s", email, link)

        EmailMessage(
            subject=subject,
            body=body,
            from_email=self.from_email,
            to=[email],
        ).send()
