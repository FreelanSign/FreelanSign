# apps/user/application/use_cases/anonymize_account_use_case.py
"""
Use case for anonymizing account data (RGPD Article 17 - Right to Erasure).

Implements "Droit à l'Oubli" by:
1. Soft deleting the account
2. Anonymizing personal data (account, user, profile)
3. Preserving legal/accounting data (quotes) for 10-year retention
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

from apps.core.models.audit import AuditLog
from apps.core.services.audit import log_audit
from apps.user.models.account import Account

User = get_user_model()


def anonymize_account_for_deletion(
    account_id: str,
    actor: Optional[User] = None,
    request: Optional[HttpRequest] = None,
) -> dict:
    """
    Anonymize account data for RGPD compliance (Article 17).

    This function implements the "Right to Erasure" by anonymizing personal data
    while preserving legal/accounting information (quotes, amounts) for the
    required 10-year retention period.

    Args:
        account_id: UUID of the account to anonymize
        actor: User initiating the action (optional, for audit trail)
        request: HTTP request (optional, for IP logging in audit)

    Returns:
        dict: Result with status and message
            {
                'success': bool,
                'account_id': str,
                'message': str
            }

    Raises:
        Account.DoesNotExist: If account not found

    Example:
        >>> result = anonymize_account_for_deletion(
        ...     account_id='123e4567-e89b-12d3-a456-426614174000',
        ...     actor=request.user,
        ...     request=request
        ... )
        >>> print(result['success'])
        True
    """
    # Fetch account with related user and profile
    account = Account.all_objects.select_related("user", "user__profile").get(id=account_id)
    user = account.user
    profile = user.profile

    # Use transaction to ensure atomicity
    with transaction.atomic():
        # 1. Soft delete and anonymize Account
        account.is_active = False
        account.display_name = f"Compte supprimé [{account.id}]"
        account.legal_id = None  # Anonymize SIRET
        account.save(update_fields=["is_active", "display_name", "legal_id"])

        # 2. Anonymize User
        user.email = f"deleted_{user.id}@anonymized.local"
        user.first_name = "Utilisateur"
        user.last_name = "Supprimé"
        user.is_active = False
        user.save(update_fields=["email", "first_name", "last_name", "is_active"])

        # 3. Anonymize Profile
        profile.phone = None
        profile.avatar_url = None
        profile.save(update_fields=["phone", "avatar_url"])

        # 4. Quotes are preserved (legal requirement - 10 years)
        # They will reference the anonymized account/client data

        # 5. Create audit log
        log_audit(
            action=AuditLog.Action.ACCOUNT_ANONYMIZED,
            actor=actor,
            target_model="Account",
            target_id=account.id,
            request=request,
            metadata={
                "user_id": str(user.id),
                "original_display_name": (
                    account.display_name if "supprimé" not in account.display_name else "Already anonymized"
                ),
            },
        )

    return {
        "success": True,
        "account_id": str(account.id),
        "message": f"Account {account.id} successfully anonymized for RGPD compliance",
    }
