"""
TDD tests for domain value objects.
"""

from apps.legal_terms.domain.value_objects.clause_category import ClauseCategory
from apps.legal_terms.domain.value_objects.clause_content import ClauseContent
from apps.legal_terms.domain.value_objects.rendered_clause import RenderedClause
from apps.legal_terms.domain.value_objects.template_variables import TemplateVariables


class TestClauseCategory:
    """Tests for ClauseCategory enum."""

    def test_clause_category_values(self):
        """ClauseCategory should have MANDATORY and OPTIONAL values."""
        assert ClauseCategory.MANDATORY == "mandatory"
        assert ClauseCategory.OPTIONAL == "optional"


class TestClauseContent:
    """Tests for ClauseContent value object."""

    def test_clause_content_is_frozen(self):
        """ClauseContent should be immutable (frozen dataclass)."""
        clause = ClauseContent(
            identifier="test",
            title="Title",
            body="Body",
            order=1,
            is_mandatory=True,
            was_customized=False,
        )

        try:
            clause.title = "New Title"
            assert False, "Should not be able to modify frozen dataclass"
        except AttributeError:
            pass

    def test_clause_content_defaults(self):
        """ClauseContent should have default for was_customized."""
        clause = ClauseContent(
            identifier="test",
            title="Title",
            body="Body",
            order=1,
            is_mandatory=True,
        )

        assert clause.was_customized is False


class TestRenderedClause:
    """Tests for RenderedClause value object."""

    def test_rendered_clause_is_frozen(self):
        """RenderedClause should be immutable."""
        clause = RenderedClause(
            identifier="test",
            title="Title",
            body="Body",
            order=1,
            is_mandatory=True,
            was_customized=False,
        )

        try:
            clause.body = "New Body"
            assert False, "Should not be able to modify frozen dataclass"
        except AttributeError:
            pass


class TestTemplateVariables:
    """Tests for TemplateVariables value object."""

    def test_template_variables_is_frozen(self):
        """TemplateVariables should be immutable."""
        vars = TemplateVariables(
            siret="12345",
            business_name="ACME",
            address="123 Main St",
            email="test@example.com",
            phone="+33123456789",
        )

        try:
            vars.siret = "99999"
            assert False, "Should not be able to modify frozen dataclass"
        except AttributeError:
            pass

    def test_to_dict_returns_proper_format(self):
        """to_dict should return variables in template-ready format."""
        vars = TemplateVariables(
            siret="12345678901234",
            business_name="ACME Corp",
            address="123 Main St, Paris",
            email="contact@acme.com",
            phone="+33123456789",
        )

        result = vars.to_dict()

        assert result == {
            "SIRET": "12345678901234",
            "BUSINESS_NAME": "ACME Corp",
            "ADDRESS": "123 Main St, Paris",
            "EMAIL": "contact@acme.com",
            "PHONE": "+33123456789",
        }
