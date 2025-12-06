"""
AccountService adapter for fetching account data.
"""

from apps.legal_terms.domain.exceptions import MissingTemplateVariablesError
from apps.legal_terms.domain.value_objects.template_variables import TemplateVariables
from apps.user.models.account import Account


class AccountServiceAdapter:
    """
    Adapter for AccountService port.

    Fetches template variables from Account and User models.
    MVP implementation pulls from existing fields.

    TODO (Future): Move all legal fields to Account model as per backlog.
    """

    def get_template_variables(self, account_id: str) -> TemplateVariables:
        """
        Get template variables for an account.

        Args:
            account_id: Account ID

        Returns:
            TemplateVariables with all required fields

        Raises:
            MissingTemplateVariablesError: If required fields are missing
        """
        try:
            account = Account.objects.select_related("user", "user__profile").get(id=account_id)
        except Account.DoesNotExist:
            raise MissingTemplateVariablesError([f"Account {account_id}"])

        # Collect fields and check for missing required ones
        missing_fields = []

        # SIRET from Account.legal_id
        siret = account.legal_id
        if not siret:
            missing_fields.append("SIRET (Account.legal_id)")

        # Business name from Account.display_name
        business_name = account.display_name
        if not business_name:
            missing_fields.append("Business name (Account.display_name)")

        # Email from User.email
        email = account.user.email
        if not email:
            missing_fields.append("Email (User.email)")

        # Phone from Profile.phone (optional but we'll require it for MVP)
        phone = getattr(account.user, "profile", None) and account.user.profile.phone
        if not phone:
            missing_fields.append("Phone (Profile.phone)")

        # Address - Not yet in Account model (MVP limitation)
        # TODO: Add address field to Account model
        # For now, we use a placeholder to avoid blocking users
        # This allows the legal terms preview to work without requiring address data
        address = "Adresse à compléter"  # Placeholder until address field is added to Account model

        # If any required fields are missing, raise error
        if missing_fields:
            raise MissingTemplateVariablesError(missing_fields)

        return TemplateVariables(
            siret=siret,
            business_name=business_name,
            address=address,
            email=email,
            phone=phone,
        )
