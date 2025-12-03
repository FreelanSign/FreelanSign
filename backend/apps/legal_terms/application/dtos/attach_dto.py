"""
DTOs for attaching legal terms to quotes.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AttachTermsInput:
    """Input for attaching legal terms to a quote."""

    quote_id: str
    account_id: str


@dataclass(frozen=True)
class AttachTermsOutput:
    """Output after attaching legal terms."""

    attached_terms_id: str
    template_version: str
