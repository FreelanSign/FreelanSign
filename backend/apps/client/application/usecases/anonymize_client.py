# apps/client/application/use_cases/anonymize_client_use_case.py
"""
Use case for anonymizing client data (RGPD Article 17 - Right to Erasure).

Implements "Droit à l'Oubli" by:
1. Soft deleting the client
2. Anonymizing personal data
3. Preserving quote references for 10-year legal retention
4. Creating audit log for traceability

@author: AI Assistant
@since: 2025-12-12
@version: 1.0
@reference: SPECIFICATIONS_RGPD.md Section 3.3
"""

from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone

from apps.client.models import Client
from apps.core.models.audit import AuditLog
from apps.core.services.audit import log_audit

User = get_user_model()


def anonymize_client_for_deletion(
    client_id: str,
    actor: Optional[User] = None,
    request: Optional[HttpRequest] = None,
) -> dict:
    """
    Anonymize client data for RGPD compliance (Article 17).

    This function implements the "Right to Erasure" by anonymizing personal data
    while preserving quote references for the required 10-year retention period.

    Args:
        client_id: UUID of the client to anonymize
        actor: User initiating the action (optional, for audit trail)
        request: HTTP request (optional, for IP logging in audit)

    Returns:
        dict: Result with status and message
            {
                'success': bool,
                'client_id': str,
                'message': str
            }

    Raises:
        Client.DoesNotExist: If client not found

    Example:
        >>> result = anonymize_client_for_deletion(
        ...     client_id='123e4567-e89b-12d3-a456-426614174000',
        ...     actor=request.user,
        ...     request=request
        ... )
        >>> print(result['success'])
        True
    """
    # Fetch client (including soft-deleted ones)
    client = Client.all_objects.get(id=client_id)

    # Use transaction to ensure atomicity
    with transaction.atomic():
        # 1. Soft delete client
        if not client.is_deleted:
            client.is_deleted = True
            client.deleted_at = timezone.now()

        # 2. Anonymize personal data
        client.name = f"Client supprimé [{client.id}]"
        client.email = f"deleted_{client.id}@anonymized.local"
        client.phone = ""
        client.address_line1 = ""
        client.address_line2 = ""
        client.city = ""
        client.postal_code = ""
        client.country = ""
        client.company = ""
        client.vat_number = ""
        client.metadata = {}

        # Save all changes
        client.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
                "name",
                "email",
                "phone",
                "address_line1",
                "address_line2",
                "city",
                "postal_code",
                "country",
                "company",
                "vat_number",
                "metadata",
            ]
        )

        # 3. Quotes are preserved (legal requirement - 10 years)
        # They will still reference this client with anonymized data

        # 4. Create audit log
        log_audit(
            action=AuditLog.Action.CLIENT_ANONYMIZED,
            actor=actor,
            target_model="Client",
            target_id=client.id,
            request=request,
            metadata={
                "account_id": str(client.account_id),
                "original_name": client.name if "supprimé" not in client.name else "Already anonymized",
            },
        )

    return {
        "success": True,
        "client_id": str(client.id),
        "message": f"Client {client.id} successfully anonymized for RGPD compliance",
    }
