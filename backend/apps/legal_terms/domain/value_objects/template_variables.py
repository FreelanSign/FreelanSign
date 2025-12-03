"""
Template variables value object.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateVariables:
    """Variables needed for legal template substitution."""

    siret: str
    business_name: str
    address: str
    email: str
    phone: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for template rendering."""
        return {
            "SIRET": self.siret,
            "BUSINESS_NAME": self.business_name,
            "ADDRESS": self.address,
            "EMAIL": self.email,
            "PHONE": self.phone,
        }
