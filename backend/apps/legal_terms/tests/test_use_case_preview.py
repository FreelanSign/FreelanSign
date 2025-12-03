"""
TDD tests for PreviewLegalTermsUseCase.
"""

from unittest.mock import Mock

import pytest

from apps.legal_terms.application.dtos.preview_dto import PreviewLegalTermsInput
from apps.legal_terms.application.use_cases.preview_legal_terms import (
    PreviewLegalTermsUseCase,
)
from apps.legal_terms.domain.entities.legal_profile import LegalProfile
from apps.legal_terms.domain.entities.legal_template import LegalTemplate
from apps.legal_terms.domain.exceptions import (
    MissingTemplateVariablesError,
    NoActiveTemplateError,
)
from apps.legal_terms.domain.services.legal_terms_assembler import LegalTermsAssembler
from apps.legal_terms.domain.value_objects.clause_category import ClauseCategory
from apps.legal_terms.domain.value_objects.clause_content import ClauseContent
from apps.legal_terms.domain.value_objects.template_variables import TemplateVariables


@pytest.fixture
def mock_repositories():
    """Mock repositories and services."""
    profile_repo = Mock()
    template_repo = Mock()
    account_service = Mock()
    renderer = Mock()
    return profile_repo, template_repo, account_service, renderer


@pytest.fixture
def sample_template():
    """Sample template for testing."""
    return LegalTemplate(
        id="tpl-1",
        name="CGV FR",
        jurisdiction="FR",
        version="1.0.0",
        clauses=[
            {
                "identifier": "payment",
                "category": ClauseCategory.MANDATORY,
                "default_title": "Paiement",
                "default_body": "Paiement sous 30 jours.",
                "default_order": 1,
                "default_is_active": True,
            }
        ],
    )


@pytest.fixture
def sample_profile(sample_template):
    """Sample profile for testing."""
    return LegalProfile(
        id="prof-1",
        account_id="acc-1",
        template_id=sample_template.id,
        template_version=sample_template.version,
        clause_overrides={},
    )


@pytest.fixture
def sample_variables():
    """Sample template variables."""
    return TemplateVariables(
        siret="12345678901234",
        business_name="ACME",
        address="123 Main St",
        email="contact@acme.com",
        phone="+33123456789",
    )


class TestPreviewLegalTermsUseCase:
    """Tests for PreviewLegalTermsUseCase."""

    def test_returns_rendered_preview(self, mock_repositories, sample_template, sample_profile, sample_variables):
        """Use case should return rendered preview with clauses."""
        profile_repo, template_repo, account_service, renderer = mock_repositories

        # Setup mocks
        template_repo.get_active_for_jurisdiction.return_value = sample_template
        profile_repo.get_or_create_for_account.return_value = sample_profile
        account_service.get_template_variables.return_value = sample_variables
        renderer.render.return_value = ("<html>Test</html>", "Test text")

        # Create use case
        assembler = LegalTermsAssembler()
        use_case = PreviewLegalTermsUseCase(profile_repo, template_repo, account_service, renderer, assembler)

        # Execute
        input_dto = PreviewLegalTermsInput(account_id="acc-1")
        result = use_case.execute(input_dto)

        # Verify
        assert result.template_version == "1.0.0"
        assert result.rendered_html == "<html>Test</html>"
        assert result.rendered_text == "Test text"
        assert len(result.clauses) == 1
        assert result.clauses[0].identifier == "payment"

        # Verify mocks called
        template_repo.get_active_for_jurisdiction.assert_called_once_with("FR")
        profile_repo.get_or_create_for_account.assert_called_once()
        account_service.get_template_variables.assert_called_once_with("acc-1")
        renderer.render.assert_called_once()

    def test_raises_when_no_active_template(self, mock_repositories):
        """Should raise NoActiveTemplateError when no template found."""
        profile_repo, template_repo, account_service, renderer = mock_repositories

        # Setup mock - no template
        template_repo.get_active_for_jurisdiction.return_value = None

        # Create use case
        assembler = LegalTermsAssembler()
        use_case = PreviewLegalTermsUseCase(profile_repo, template_repo, account_service, renderer, assembler)

        # Execute and verify exception
        input_dto = PreviewLegalTermsInput(account_id="acc-1")
        with pytest.raises(NoActiveTemplateError) as exc_info:
            use_case.execute(input_dto)

        assert exc_info.value.jurisdiction == "FR"

    def test_raises_when_missing_template_variables(self, mock_repositories, sample_template, sample_profile):
        """Should propagate MissingTemplateVariablesError from account service."""
        profile_repo, template_repo, account_service, renderer = mock_repositories

        # Setup mocks
        template_repo.get_active_for_jurisdiction.return_value = sample_template
        profile_repo.get_or_create_for_account.return_value = sample_profile
        account_service.get_template_variables.side_effect = MissingTemplateVariablesError(["siret", "business_name"])

        # Create use case
        assembler = LegalTermsAssembler()
        use_case = PreviewLegalTermsUseCase(profile_repo, template_repo, account_service, renderer, assembler)

        # Execute and verify exception
        input_dto = PreviewLegalTermsInput(account_id="acc-1")
        with pytest.raises(MissingTemplateVariablesError) as exc_info:
            use_case.execute(input_dto)

        assert "siret" in exc_info.value.missing_variables
        assert "business_name" in exc_info.value.missing_variables

    def test_creates_profile_if_not_exists(self, mock_repositories, sample_template, sample_profile, sample_variables):
        """Should create profile via get_or_create_for_account."""
        profile_repo, template_repo, account_service, renderer = mock_repositories

        # Setup mocks
        template_repo.get_active_for_jurisdiction.return_value = sample_template
        profile_repo.get_or_create_for_account.return_value = sample_profile
        account_service.get_template_variables.return_value = sample_variables
        renderer.render.return_value = ("<html>Test</html>", "Test text")

        # Create use case
        assembler = LegalTermsAssembler()
        use_case = PreviewLegalTermsUseCase(profile_repo, template_repo, account_service, renderer, assembler)

        # Execute
        input_dto = PreviewLegalTermsInput(account_id="acc-1")
        use_case.execute(input_dto)

        # Verify get_or_create called with correct params
        profile_repo.get_or_create_for_account.assert_called_once_with(
            account_id="acc-1", template_id="tpl-1", template_version="1.0.0"
        )
