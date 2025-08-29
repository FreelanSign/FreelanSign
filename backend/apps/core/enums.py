from django.db.models import TextChoices

class QuoteStatus(TextChoices):
    DRAFT = "draft", "Draft"
    SENT = "sent", "Sent"
    VALIDATED = "validated", "Validated"
    CANCELED = "canceled", "Canceled"
    REFUSED = "refused", "Refused"
    DELETED = "deleted", "Deleted"

class AddressType(TextChoices):
    BILLUNG = "billing", "Billing"
    SHIPPING = "shipping", "Shipping"
    PRO = "pro", "Pro"

class PrestationStatus(TextChoices):
    ACTIVE = "active", "Active"
    CANCELED = "canceled", "Canceled"
    DELETED = "deleted", "Deleted"
