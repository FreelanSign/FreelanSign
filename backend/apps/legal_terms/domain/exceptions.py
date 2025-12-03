"""
Domain exceptions for legal_terms bounded context.
"""


class LegalTermsError(Exception):
    """Base exception for legal_terms domain."""


class MandatoryClauseModificationError(LegalTermsError):
    """Raised when attempting to modify/disable a mandatory clause."""

    def __init__(self, identifier: str):
        super().__init__(f"Cannot modify or disable mandatory clause: {identifier}")
        self.identifier = identifier


class ClauseNotFoundError(LegalTermsError):
    """Raised when a clause identifier is not found."""

    def __init__(self, identifier: str):
        super().__init__(f"Clause not found: {identifier}")
        self.identifier = identifier


class MissingTemplateVariablesError(LegalTermsError):
    """Raised when required template variables are missing."""

    def __init__(self, missing_variables: list[str]):
        super().__init__(f"Missing required template variables: {', '.join(missing_variables)}")
        self.missing_variables = missing_variables


class NoActiveTemplateError(LegalTermsError):
    """Raised when no active template is found for jurisdiction."""

    def __init__(self, jurisdiction: str):
        super().__init__(f"No active template found for jurisdiction: {jurisdiction}")
        self.jurisdiction = jurisdiction


class InvalidClauseOrderError(LegalTermsError):
    """Raised when clause order is invalid."""

    def __init__(self, message: str):
        super().__init__(message)
