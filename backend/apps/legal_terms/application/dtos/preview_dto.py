"""
DTOs for legal terms preview functionality.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PreviewLegalTermsInput:
    """Input for previewing legal terms."""

    account_id: str


@dataclass(frozen=True)
class ClausePreviewDTO:
    """Preview data for a single clause."""

    identifier: str
    title: str
    body: str
    order: int
    is_mandatory: bool
    was_customized: bool


@dataclass(frozen=True)
class PreviewLegalTermsOutput:
    """Output with rendered preview of legal terms."""

    clauses: list[ClausePreviewDTO]
    rendered_html: str
    rendered_text: str
    template_version: str
