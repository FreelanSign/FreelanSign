"""
Rendered clause value object.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RenderedClause:
    """Represents a rendered legal clause with all variables substituted."""

    identifier: str
    title: str
    body: str
    order: int
    is_mandatory: bool
    was_customized: bool
