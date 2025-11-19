# apps/user/application/ports/token_sender.py

from typing import Protocol


class TokenSender(Protocol):
    """
    Port: TokenSender
    Defines the contract for sending password reset links.
    """

    def send_reset_link(self, email: str, token: str) -> None:
        """
        Sends a password reset link to the user.
        Should include a URL containing the token.

        Args:
            email: Target email address.
            token: Reset token (signed, time-limited).
        """
        ...
