# apps/user/adapters/providers/brevo_api_token_sender.py

import json
import logging
import urllib.error
import urllib.request

from apps.user.application.ports.token_sender import TokenSender

logger = logging.getLogger(__name__)


class BrevoApiTokenSender(TokenSender):
    """
    Sends reset tokens via Brevo's transactional email HTTP API.
    Uses stdlib urllib to avoid external dependencies.
    """

    API_URL = "https://api.brevo.com/v3/smtp/email"

    def __init__(self, reset_base_url: str, from_email: str, api_key: str):
        self.reset_base_url = reset_base_url
        self.from_email = from_email
        self.api_key = api_key

    def send_reset_link(self, email: str, token: str) -> None:
        link = f"{self.reset_base_url}?token={token}"
        payload = json.dumps(
            {
                "sender": {"email": self.from_email},
                "to": [{"email": email}],
                "subject": "Password Reset Instructions",
                "textContent": (
                    "Hello,\n\n"
                    f"To reset your password, click here:\n{link}\n\n"
                    "If you did not request this, ignore this email."
                ),
            }
        ).encode("utf-8")

        logger.info("Sending password reset email to %s via Brevo API", email)

        req = urllib.request.Request(
            self.API_URL,
            data=payload,
            headers={
                "api-key": self.api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                logger.info("Brevo API response: %s", resp.status)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            logger.error("Brevo API error %s for %s: %s", exc.code, email, body)
            raise
        except Exception as exc:
            logger.error("Failed to send password reset email to %s: %s", email, exc)
            raise
