# apps/quote/application/ports/email_sender.py
from __future__ import annotations
from typing import Protocol

class EmailSender(Protocol):
    """
    Send an email with (optionally) a PDF attachment.
    The concrete implementation (SMTP/Sendgrid/etc.) lives in adapters/.
    """

    def send_quote(
        self,
        *,
        recipients: list[str],
        subject: str,
        body_html: str,
        attachments: list[tuple[str, bytes]] | None = None,
    ) -> None:
        """
        :param recipients: list of email addresses.
        :param subject: The subject of the email.
        :param body_html: The HTML body of the email.
        :param attachments: The attachments of the email.
        """
        ...
