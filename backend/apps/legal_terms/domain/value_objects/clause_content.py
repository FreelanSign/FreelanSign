"""
Clause content value object.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ClauseContent:
    """Represents the content of a legal clause."""

    identifier: str
    title: str
    body: str
    order: int
    is_mandatory: bool
    was_customized: bool = False
