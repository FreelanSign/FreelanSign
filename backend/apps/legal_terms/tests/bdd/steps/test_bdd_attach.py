"""
BDD tests for attaching legal terms to quotes.
"""

from unittest.mock import Mock

import pytest
from pytest_bdd import given, parsers, scenario, scenarios, then, when

from apps.legal_terms.application.dtos.attach_dto import AttachTermsInput
from apps.legal_terms.application.use_cases.attach_terms_to_quote import (
    AttachTermsToQuoteUseCase,
)
from apps.legal_terms.domain.entities.legal_profile import LegalProfile
from apps.legal_terms.domain.entities.legal_template import LegalTemplate
from apps.legal_terms.domain.exceptions import (
    MissingTemplateVariablesError,
    NoActiveTemplateError,
)
from apps.legal_terms.domain.services.legal_terms_assembler import LegalTermsAssembler
from apps.legal_terms.domain.value_objects.clause_category import ClauseCategory
from apps.legal_terms.domain.value_objects.template_variables import TemplateVariables

# Charge tous les scénarios du feature file
scenarios("../features/attach_legal_terms_to_quote.feature")


# Fixtures
@pytest.fixture
def context():
    """Shared context for BDD scenarios."""
    return {
        "template": None,
        "profile": None,
        "account_id": None,
        "quote_id": None,
        "result": None,
        "error": None,
        "attached_terms_created": False,
    }


@pytest.fixture
def mock_repos():
    """Mock repositories and services."""
    return {
        "profile_repo": Mock(),
        "template_repo": Mock(),
        "attached_terms_repo": Mock(),
        "account_service": Mock(),
        "renderer": Mock(),
    }


@pytest.fixture
def use_case(mock_repos):
    """Create use case with mocked dependencies."""
    assembler = LegalTermsAssembler()
    return AttachTermsToQuoteUseCase(
        profile_repository=mock_repos["profile_repo"],
        template_repository=mock_repos["template_repo"],
        attached_terms_repository=mock_repos["attached_terms_repo"],
        account_service=mock_repos["account_service"],
        template_renderer=mock_repos["renderer"],
        assembler=assembler,
    )


# Scenarios
@scenario(
    "../features/attach_legal_terms_to_quote.feature",
    "Successfully attach legal terms to quote with valid account data",
)
def test_successful_attach():
    """Test successful attachment of legal terms."""
    pass


@scenario(
    "../features/attach_legal_terms_to_quote.feature",
    "Fail to attach legal terms when template variables are missing",
)
def test_fail_missing_variables():
    """Test failure when template variables missing."""
    pass


@scenario(
    "../features/attach_legal_terms_to_quote.feature",
    "Fail to attach legal terms when no active template exists",
)
def test_fail_no_template():
    """Test failure when no active template."""
    pass


@scenario(
    "../features/attach_legal_terms_to_quote.feature",
    "Attach legal terms with profile customizations",
)
def test_attach_with_customizations():
    """Test attachment with profile customizations."""
    pass


# Background steps
@given(parsers.parse('an active legal template exists for jurisdiction "{jurisdiction}"'))
def active_template_exists(context, mock_repos, jurisdiction):
    """Create active template."""
    template = LegalTemplate(
        id="tpl-1",
        name=f"CGV {jurisdiction}",
        jurisdiction=jurisdiction,
        version="1.0.0",
        clauses=[
            {
                "identifier": "payment",
                "category": ClauseCategory.MANDATORY,
                "default_title": "Paiement",
                "default_body": "Paiement sous 30 jours pour {{BUSINESS_NAME}}.",
                "default_order": 1,
                "default_is_active": True,
            },
            {
                "identifier": "warranty",
                "category": ClauseCategory.OPTIONAL,
                "default_title": "Garantie",
                "default_body": "Garantie standard.",
                "default_order": 2,
                "default_is_active": True,
            },
        ],
    )
    context["template"] = template
    mock_repos["template_repo"].get_active_for_jurisdiction.return_value = template


@given("the template has mandatory and optional clauses")
def template_has_clauses(context):
    """Verify template has both types of clauses."""
    template = context["template"]
    assert template is not None
    assert len(template.clauses) >= 2


# Given steps
@given(parsers.parse('an account with ID "{account_id}" exists'))
def account_exists(context, account_id):
    """Set account ID."""
    context["account_id"] = account_id


@given("the account has all required legal fields")
def account_has_required_fields(context, mock_repos):
    """Mock account service to return valid variables."""
    variables = TemplateVariables(
        siret="12345678901234",
        business_name="ACME Corp",
        address="123 Main St",
        email="contact@acme.com",
        phone="+33123456789",
    )
    mock_repos["account_service"].get_template_variables.return_value = variables


@given("a legal profile exists for the account")
def profile_exists(context, mock_repos):
    """Create legal profile."""
    template = context["template"]
    account_id = context["account_id"]
    profile = LegalProfile(
        id="prof-1",
        account_id=account_id,
        template_id=template.id,
        template_version=template.version,
        clause_overrides={},
    )
    context["profile"] = profile
    mock_repos["profile_repo"].get_or_create_for_account.return_value = profile


@given(parsers.parse('the account is missing required field "{field_name}"'))
def account_missing_field(context, mock_repos, field_name):
    """Mock account service to raise missing variables error."""
    mock_repos["account_service"].get_template_variables.side_effect = MissingTemplateVariablesError([field_name])


@given(parsers.parse('no active legal template exists for jurisdiction "{jurisdiction}"'))
def no_active_template(mock_repos, jurisdiction):
    """Mock no active template."""
    mock_repos["template_repo"].get_active_for_jurisdiction.return_value = None


@given(parsers.parse('the profile has custom overrides for clause "{clause_id}"'))
def profile_has_overrides(context, clause_id):
    """Add custom overrides to profile."""
    profile = context["profile"]
    profile.clause_overrides[clause_id] = {
        "custom_title": "Garantie personnalisée",
        "custom_body": "Garantie modifiée.",
    }


# When steps
@when(parsers.parse('I attach legal terms to quote "{quote_id}"'))
def attach_legal_terms(context, mock_repos, use_case, quote_id):
    """Execute attach use case."""
    context["quote_id"] = quote_id

    # Mock renderer
    mock_repos["renderer"].render.return_value = ("<html>CGV</html>", "CGV text")

    # Mock save to return entity
    def save_terms(terms):
        context["attached_terms_created"] = True
        return terms

    mock_repos["attached_terms_repo"].save.side_effect = save_terms

    try:
        input_dto = AttachTermsInput(quote_id=quote_id, account_id=context["account_id"])
        result = use_case.execute(input_dto)
        context["result"] = result
    except Exception as e:
        context["error"] = e


@when(parsers.parse('I attempt to attach legal terms to quote "{quote_id}"'))
def attempt_attach_legal_terms(context, mock_repos, use_case, quote_id):
    """Attempt to execute attach use case (expects failure)."""
    context["quote_id"] = quote_id

    # Mock renderer (may not be called if earlier error)
    mock_repos["renderer"].render.return_value = ("<html>CGV</html>", "CGV text")

    # Mock save to track if called
    def save_terms(terms):
        context["attached_terms_created"] = True
        return terms

    mock_repos["attached_terms_repo"].save.side_effect = save_terms

    try:
        input_dto = AttachTermsInput(quote_id=quote_id, account_id=context["account_id"])
        result = use_case.execute(input_dto)
        context["result"] = result
    except Exception as e:
        context["error"] = e


# Then steps
@then("the legal terms should be successfully attached")
def verify_successful_attach(context):
    """Verify successful attachment."""
    assert context["error"] is None
    assert context["result"] is not None
    assert context["attached_terms_created"] is True


@then("the attached terms should have a valid snapshot")
def verify_valid_snapshot(context, mock_repos):
    """Verify snapshot was created."""
    saved_terms = mock_repos["attached_terms_repo"].save.call_args[0][0]
    assert saved_terms.snapshot_data is not None
    assert "clauses" in saved_terms.snapshot_data
    assert "template_version" in saved_terms.snapshot_data
    assert "variables_used" in saved_terms.snapshot_data


@then("the snapshot should contain all mandatory clauses")
def verify_mandatory_clauses(context, mock_repos):
    """Verify mandatory clauses in snapshot."""
    saved_terms = mock_repos["attached_terms_repo"].save.call_args[0][0]
    clauses = saved_terms.snapshot_data["clauses"]
    mandatory_clauses = [c for c in clauses if c["is_mandatory"]]
    assert len(mandatory_clauses) >= 1
    assert any(c["identifier"] == "payment" for c in mandatory_clauses)


@then("the snapshot should include the template version")
def verify_template_version(context, mock_repos):
    """Verify template version in snapshot."""
    saved_terms = mock_repos["attached_terms_repo"].save.call_args[0][0]
    assert saved_terms.template_version == "1.0.0"
    assert saved_terms.snapshot_data["template_version"] == "1.0.0"


@then(parsers.parse('the attached terms should be linked to quote "{quote_id}"'))
def verify_quote_link(context, mock_repos, quote_id):
    """Verify attached terms linked to quote."""
    saved_terms = mock_repos["attached_terms_repo"].save.call_args[0][0]
    assert saved_terms.quote_id == quote_id


@then("the attach operation should fail")
def verify_operation_failed(context):
    """Verify operation failed."""
    assert context["error"] is not None


@then("a MissingTemplateVariablesError should be raised")
def verify_missing_variables_error(context):
    """Verify correct exception type."""
    assert isinstance(context["error"], MissingTemplateVariablesError)


@then(parsers.parse('the error should mention "{field_name}"'))
def verify_error_mentions_field(context, field_name):
    """Verify error mentions specific field."""
    assert field_name in context["error"].missing_variables


@then("no attached terms should be created")
def verify_no_terms_created(context):
    """Verify no terms were saved."""
    assert context["attached_terms_created"] is False


@then("a NoActiveTemplateError should be raised")
def verify_no_template_error(context):
    """Verify correct exception type."""
    assert isinstance(context["error"], NoActiveTemplateError)


@then("the snapshot should reflect the custom overrides")
def verify_custom_overrides(context, mock_repos):
    """Verify customizations in snapshot."""
    saved_terms = mock_repos["attached_terms_repo"].save.call_args[0][0]
    clauses = saved_terms.snapshot_data["clauses"]
    warranty_clause = next((c for c in clauses if c["identifier"] == "warranty"), None)
    assert warranty_clause is not None
    assert warranty_clause["title"] == "Garantie personnalisée"
    assert warranty_clause["body"] == "Garantie modifiée."


@then('the customized clause should have "was_customized" set to true')
def verify_was_customized_flag(context, mock_repos):
    """Verify was_customized flag."""
    saved_terms = mock_repos["attached_terms_repo"].save.call_args[0][0]
    clauses = saved_terms.snapshot_data["clauses"]
    warranty_clause = next((c for c in clauses if c["identifier"] == "warranty"), None)
    assert warranty_clause["was_customized"] is True
