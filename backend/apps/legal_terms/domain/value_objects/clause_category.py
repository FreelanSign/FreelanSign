"""
Clause category enum for legal terms.
"""
from enum import Enum


class ClauseCategory(str, Enum):
    """Category of a legal clause."""

    MANDATORY = "mandatory"
    OPTIONAL = "optional"
