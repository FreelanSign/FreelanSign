# apps/user/adapters/providers/logging_token_sender.py
import logging
from urllib.parse import urlencode

from apps.user.application.ports.token_sender import TokenSender

logger = logging.getLogger(__name__)


class LoggingTokenSender(TokenSender):
    """
    Logging-based TokenSender for development/testing.
    Logs the reset URL instead of sending an actual email.
    """

    def __init__(self, reset_base_url: str):
        self.rset_base_url = reset_base_url.strip("/")

    def send_reset_link(self, email: str, token: str) -> None:
        """
        Logs the password reset link with the signed token.
        """
        url = f"{self.rset_base_url}?{urlencode({'token': token})}"
        logger.info("Sending password reset link to %s: %s", email, url)
