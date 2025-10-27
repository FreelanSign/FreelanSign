# apps/quote/adapters/email/django_email_sender.py
class DjangoEmailSender:
    def send_quote(self, *, recipients: list[str], subject: str, body_html: str, attachments: list[tuple[str, bytes]]):
        # No-op pour les tests
        # TODO: @Bertrand2808: Implement the actual email sending
        return None
