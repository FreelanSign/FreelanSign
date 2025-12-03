"""
TDD tests for LegalTermsAssembler domain service.
"""
import pytest

from apps.legal_terms.domain.entities.legal_profile import LegalProfile
from apps.legal_terms.domain.entities.legal_template import LegalTemplate
from apps.legal_terms.domain.services.legal_terms_assembler import LegalTermsAssembler
from apps.legal_terms.domain.value_objects.clause_category import ClauseCategory


@pytest.fixture
def base_template():
    """Fixture for base legal template."""
    return LegalTemplate(
        id="tpl-1",
        name="CGV Auto-Entrepreneur FR",
        jurisdiction="FR",
        version="1.0.0",
        clauses=[
            {
                "identifier": "payment_terms",
                "category": ClauseCategory.MANDATORY,
                "default_title": "Conditions de paiement",
                "default_body": "Le paiement est dû sous 30 jours.",
                "default_order": 1,
                "default_is_active": True,
            },
            {
                "identifier": "warranty",
                "category": ClauseCategory.OPTIONAL,
                "default_title": "Garantie",
                "default_body": "Garantie standard de 12 mois.",
                "default_order": 2,
                "default_is_active": True,
            },
            {
                "identifier": "liability",
                "category": ClauseCategory.MANDATORY,
                "default_title": "Responsabilité",
                "default_body": "Limitation de responsabilité.",
                "default_order": 3,
                "default_is_active": True,
            },
            {
                "identifier": "optional_clause",
                "category": ClauseCategory.OPTIONAL,
                "default_title": "Clause optionnelle",
                "default_body": "Clause optionnelle inactive par défaut.",
                "default_order": 4,
                "default_is_active": False,
            },
        ],
        is_active=True,
    )


@pytest.fixture
def empty_profile(base_template):
    """Fixture for empty profile with no overrides."""
    return LegalProfile(
        id="prof-1",
        account_id="acc-1",
        template_id=base_template.id,
        template_version=base_template.version,
        clause_overrides={},
    )


@pytest.fixture
def assembler():
    """Fixture for LegalTermsAssembler."""
    return LegalTermsAssembler()


class TestLegalTermsAssembler:
    """Tests for LegalTermsAssembler domain service."""

    def test_mandatory_clauses_always_included(self, assembler, base_template, empty_profile):
        """Mandatory clauses must always be included in assembled result."""
        result = assembler.assemble(base_template, empty_profile)

        mandatory_identifiers = {"payment_terms", "liability"}
        result_identifiers = {clause.identifier for clause in result}

        assert mandatory_identifiers.issubset(result_identifiers)

    def test_mandatory_clauses_cannot_be_disabled(self, assembler, base_template, empty_profile):
        """Mandatory clauses remain active even if profile attempts to disable them."""
        # Attempt to disable mandatory clause in profile
        empty_profile.clause_overrides["payment_terms"] = {"is_active": False}

        result = assembler.assemble(base_template, empty_profile)
        payment_clause = next(c for c in result if c.identifier == "payment_terms")

        # Should still be included despite override attempting to disable
        assert payment_clause is not None

    def test_optional_clause_can_be_disabled(self, assembler, base_template, empty_profile):
        """Optional clauses can be disabled via profile."""
        # Disable optional clause
        empty_profile.clause_overrides["warranty"] = {"is_active": False}

        result = assembler.assemble(base_template, empty_profile)
        result_identifiers = {clause.identifier for clause in result}

        assert "warranty" not in result_identifiers

    def test_optional_clause_can_be_enabled(self, assembler, base_template, empty_profile):
        """Optional clauses that are inactive by default can be enabled."""
        # Enable inactive optional clause
        empty_profile.clause_overrides["optional_clause"] = {"is_active": True}

        result = assembler.assemble(base_template, empty_profile)
        result_identifiers = {clause.identifier for clause in result}

        assert "optional_clause" in result_identifiers

    def test_profile_overrides_title_and_body(self, assembler, base_template, empty_profile):
        """Profile can override title and body of clauses."""
        custom_title = "Titre personnalisé"
        custom_body = "Contenu personnalisé."
        empty_profile.clause_overrides["warranty"] = {
            "custom_title": custom_title,
            "custom_body": custom_body,
        }

        result = assembler.assemble(base_template, empty_profile)
        warranty_clause = next(c for c in result if c.identifier == "warranty")

        assert warranty_clause.title == custom_title
        assert warranty_clause.body == custom_body
        assert warranty_clause.was_customized is True

    def test_profile_overrides_order(self, assembler, base_template, empty_profile):
        """Profile can override clause order."""
        empty_profile.clause_overrides["liability"] = {"custom_order": 0}

        result = assembler.assemble(base_template, empty_profile)

        # liability should now be first
        assert result[0].identifier == "liability"
        assert result[0].order == 0

    def test_clauses_sorted_by_order(self, assembler, base_template, empty_profile):
        """Assembled clauses should be sorted by order."""
        result = assembler.assemble(base_template, empty_profile)

        for i in range(len(result) - 1):
            assert result[i].order <= result[i + 1].order

    def test_default_active_optional_clauses_included(self, assembler, base_template, empty_profile):
        """Optional clauses with default_is_active=True are included by default."""
        result = assembler.assemble(base_template, empty_profile)
        result_identifiers = {clause.identifier for clause in result}

        assert "warranty" in result_identifiers

    def test_default_inactive_optional_clauses_excluded(self, assembler, base_template, empty_profile):
        """Optional clauses with default_is_active=False are excluded by default."""
        result = assembler.assemble(base_template, empty_profile)
        result_identifiers = {clause.identifier for clause in result}

        assert "optional_clause" not in result_identifiers

    def test_was_customized_flag_set_correctly(self, assembler, base_template, empty_profile):
        """was_customized flag should be set when title or body is overridden."""
        # No customization
        result = assembler.assemble(base_template, empty_profile)
        payment_clause = next(c for c in result if c.identifier == "payment_terms")
        assert payment_clause.was_customized is False

        # With customization
        empty_profile.clause_overrides["payment_terms"] = {"custom_title": "New Title"}
        result = assembler.assemble(base_template, empty_profile)
        payment_clause = next(c for c in result if c.identifier == "payment_terms")
        assert payment_clause.was_customized is True

    def test_create_snapshot_data(self, assembler, base_template, empty_profile):
        """create_snapshot_data should produce valid snapshot structure."""
        clauses = assembler.assemble(base_template, empty_profile)
        variables_dict = {"SIRET": "12345", "BUSINESS_NAME": "ACME"}

        snapshot = assembler.create_snapshot_data(clauses, base_template, variables_dict)

        assert snapshot["template_version"] == "1.0.0"
        assert snapshot["template_name"] == "CGV Auto-Entrepreneur FR"
        assert len(snapshot["clauses"]) == len(clauses)
        assert snapshot["variables_used"] == variables_dict

        # Verify clause structure
        first_clause = snapshot["clauses"][0]
        assert "identifier" in first_clause
        assert "title" in first_clause
        assert "body" in first_clause
        assert "order" in first_clause
        assert "is_mandatory" in first_clause
        assert "was_customized" in first_clause
