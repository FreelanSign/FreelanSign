# apps/user/application/usecases/send_verification_email.py
import logging

from django.core import signing
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger(__name__)

SIGNER_SALT = "user.email-verify"
TOKEN_EXPIRATION_HOURS = 2


class SendVerificationEmail:
    def __init__(self, *, verification_base_url: str, from_email: str):
        self.verification_base_url = verification_base_url
        self.from_email = from_email

    def execute(self, *, user_id: int, email: str) -> None:
        payload = {
            "user_id": user_id,
            "email": email,
            "ts": timezone.now().timestamp(),
        }
        token = signing.dumps(payload, salt=SIGNER_SALT)
        link = f"{self.verification_base_url}?token={token}"

        subject = "Verifiez votre adresse email - FreelanSign"
        body = (
            "Bonjour,\n\n"
            "Merci de votre inscription sur FreelanSign.\n"
            f"Pour verifier votre adresse email, cliquez sur ce lien :\n{link}\n\n"
            "Ce lien est valable 2 heures.\n\n"
            "Si vous n'avez pas cree de compte, ignorez cet email."
        )

        EmailMessage(
            subject=subject,
            body=body,
            from_email=self.from_email,
            to=[email],
        ).send()

        logger.info("Verification email sent to %s for user_id=%s", email, user_id)
