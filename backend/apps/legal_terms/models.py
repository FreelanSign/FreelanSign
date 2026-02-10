"""
Models for legal_terms app.
Re-exports models from adapters/persistence for Django discovery.
"""

from apps.legal_terms.adapters.persistence.models import (
    AttachedTermsModel,
    LegalProfileModel,
    LegalTemplateModel,
)

__all__ = ["LegalTemplateModel", "LegalProfileModel", "AttachedTermsModel"]
