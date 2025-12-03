"""
TDD tests for domain entities.
"""

import pytest

from apps.legal_terms.domain.entities.attached_terms import AttachedTerms
from apps.legal_terms.domain.entities.legal_profile import LegalProfile
from apps.legal_terms.domain.entities.legal_template import LegalTemplate
from apps.legal_terms.domain.exceptions import (
    ClauseNotFoundError,
    MandatoryClauseModificationError,
)
from apps.legal_terms.domain.value_objects.clause_category import ClauseCategory


class TestLegalTemplate:
    """Tests for LegalTemplate entity."""

    def test_get_clause_returns_clause_data(self):
        """get_clause should return clause data by identifier."""
        template = LegalTemplate(
            id="tpl-1",
            name="Test Template",
            jurisdiction="FR",
            version="1.0.0",
            clauses=[
                {"identifier": "clause1", "category": ClauseCategory.MANDATORY},
                {"identifier": "clause2", "category": ClauseCategory.OPTIONAL},
            ],
        )

        clause = template.get_clause("clause1")
        assert clause["identifier"] == "clause1"

    def test_get_clause_raises_on_not_found(self):
        """get_clause should raise ClauseNotFoundError if identifier not found."""
        template = LegalTemplate(
            id="tpl-1",
            name="Test Template",
            jurisdiction="FR",
            version="1.0.0",
            clauses=[],
        )

        with pytest.raises(ClauseNotFoundError) as exc_info:
            template.get_clause("nonexistent")

        assert exc_info.value.identifier == "nonexistent"

    def test_is_mandatory_clause(self):
        """is_mandatory_clause should correctly identify mandatory clauses."""
        template = LegalTemplate(
            id="tpl-1",
            name="Test Template",
            jurisdiction="FR",
            version="1.0.0",
            clauses=[
                {"identifier": "mandatory", "category": ClauseCategory.MANDATORY},
                {"identifier": "optional", "category": ClauseCategory.OPTIONAL},
            ],
        )

        assert template.is_mandatory_clause("mandatory") is True
        assert template.is_mandatory_clause("optional") is False

    def test_get_mandatory_clause_identifiers(self):
        """get_mandatory_clause_identifiers should return set of mandatory IDs."""
        template = LegalTemplate(
            id="tpl-1",
            name="Test Template",
            jurisdiction="FR",
            version="1.0.0",
            clauses=[
                {"identifier": "m1", "category": ClauseCategory.MANDATORY},
                {"identifier": "o1", "category": ClauseCategory.OPTIONAL},
                {"identifier": "m2", "category": ClauseCategory.MANDATORY},
            ],
        )

        mandatory_ids = template.get_mandatory_clause_identifiers()
        assert mandatory_ids == {"m1", "m2"}


class TestLegalProfile:
    """Tests for LegalProfile entity."""

    def test_get_override_returns_none_when_not_set(self):
        """get_override should return None when no override exists."""
        profile = LegalProfile(
            id="prof-1",
            account_id="acc-1",
            template_id="tpl-1",
            template_version="1.0.0",
        )

        assert profile.get_override("clause1") is None

    def test_set_override_stores_override(self):
        """set_override should store override data."""
        profile = LegalProfile(
            id="prof-1",
            account_id="acc-1",
            template_id="tpl-1",
            template_version="1.0.0",
        )

        profile.set_override(
            identifier="clause1",
            is_mandatory=False,
            custom_title="Custom Title",
        )

        override = profile.get_override("clause1")
        assert override is not None
        assert override["custom_title"] == "Custom Title"

    def test_set_override_raises_on_disabling_mandatory(self):
        """set_override should raise when attempting to disable mandatory clause."""
        profile = LegalProfile(
            id="prof-1",
            account_id="acc-1",
            template_id="tpl-1",
            template_version="1.0.0",
        )

        with pytest.raises(MandatoryClauseModificationError) as exc_info:
            profile.set_override(
                identifier="mandatory_clause",
                is_mandatory=True,
                is_active=False,
            )

        assert exc_info.value.identifier == "mandatory_clause"

    def test_remove_override_deletes_override(self):
        """remove_override should delete existing override."""
        profile = LegalProfile(
            id="prof-1",
            account_id="acc-1",
            template_id="tpl-1",
            template_version="1.0.0",
            clause_overrides={"clause1": {"custom_title": "Test"}},
        )

        profile.remove_override("clause1")
        assert profile.get_override("clause1") is None

    def test_has_customization(self):
        """has_customization should return True when overrides exist."""
        profile = LegalProfile(
            id="prof-1",
            account_id="acc-1",
            template_id="tpl-1",
            template_version="1.0.0",
        )

        assert profile.has_customization() is False

        profile.set_override("clause1", is_mandatory=False, custom_title="Test")
        assert profile.has_customization() is True


class TestAttachedTerms:
    """Tests for AttachedTerms entity."""

    def test_get_clause_count(self):
        """get_clause_count should return number of clauses in snapshot."""
        terms = AttachedTerms(
            id="att-1",
            quote_id="quote-1",
            template_version="1.0.0",
            rendered_html="<html></html>",
            rendered_text="text",
            snapshot_data={
                "clauses": [
                    {"identifier": "c1"},
                    {"identifier": "c2"},
                    {"identifier": "c3"},
                ]
            },
        )

        assert terms.get_clause_count() == 3

    def test_get_mandatory_clause_count(self):
        """get_mandatory_clause_count should count mandatory clauses."""
        terms = AttachedTerms(
            id="att-1",
            quote_id="quote-1",
            template_version="1.0.0",
            rendered_html="<html></html>",
            rendered_text="text",
            snapshot_data={
                "clauses": [
                    {"identifier": "c1", "is_mandatory": True},
                    {"identifier": "c2", "is_mandatory": False},
                    {"identifier": "c3", "is_mandatory": True},
                ]
            },
        )

        assert terms.get_mandatory_clause_count() == 2

    def test_get_customized_clause_count(self):
        """get_customized_clause_count should count customized clauses."""
        terms = AttachedTerms(
            id="att-1",
            quote_id="quote-1",
            template_version="1.0.0",
            rendered_html="<html></html>",
            rendered_text="text",
            snapshot_data={
                "clauses": [
                    {"identifier": "c1", "was_customized": True},
                    {"identifier": "c2", "was_customized": False},
                    {"identifier": "c3", "was_customized": True},
                ]
            },
        )

        assert terms.get_customized_clause_count() == 2
