"""
Port for account service.
"""

from typing import Protocol

from apps.legal_terms.domain.value_objects.template_variables import TemplateVariables


class AccountService(Protocol):
    """Service port for fetching account data."""

    def get_template_variables(self, account_id: str) -> TemplateVariables:
        """
        Get template variables for an account.
        Raises MissingTemplateVariablesError if required fields are missing.
        """
        ...
