"""
TDD tests for AttachTermsToQuoteUseCase.
"""

from unittest.mock import Mock

import pytest

from apps.legal_terms.application.dtos.attach_dto import AttachTermsInput
from apps.legal_terms.application.use_cases.attach_terms_to_quote import (
    AttachTermsToQuoteUseCase,
)
from apps.legal_terms.domain.entities.attached_terms import AttachedTerms
from apps.legal_terms.domain.entities.legal_profile import LegalProfile
from apps.legal_terms.domain.entities.legal_template import LegalTemplate
from apps.legal_terms.domain.exceptions import (
    MissingTemplateVariablesError,
    NoActiveTemplateError,
)
from apps.legal_terms.domain.services.legal_terms_assembler import LegalTermsAssembler
from apps.legal_terms.domain.value_objects.clause_category import ClauseCategory
from apps.legal_terms.domain.value_objects.template_variables import TemplateVariables


@pytest.fixture
def mock_repositories():
    """Mock repositories and services."""
    profile_repo = Mock()
    template_repo = Mock()
    attached_terms_repo = Mock()
    account_service = Mock()
    renderer = Mock()
    return profile_repo, template_repo, attached_terms_repo, account_service, renderer


@pytest.fixture
def sample_template():
    """Sample template."""
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
                "default_body": "Paiement sous 30 jours pour {{BUSINESS_NAME}}.",
                "default_order": 1,
                "default_is_active": True,
            }
        ],
    )


@pytest.fixture
def sample_profile(sample_template):
    """Sample profile."""
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
        business_name="ACME Corp",
        address="123 Main St",
        email="contact@acme.com",
        phone="+33123456789",
    )


class TestAttachTermsToQuoteUseCase:
    """Tests for AttachTermsToQuoteUseCase."""

    def test_attaches_terms_successfully(
        self,
        mock_repositories,
        sample_template,
        sample_profile,
        sample_variables,
    ):
        """Use case should attach legal terms to quote."""
        (
            profile_repo,
            template_repo,
            attached_terms_repo,
            account_service,
            renderer,
        ) = mock_repositories

        # Setup mocks
        template_repo.get_active_for_jurisdiction.return_value = sample_template
        profile_repo.get_or_create_for_account.return_value = sample_profile
        account_service.get_template_variables.return_value = sample_variables
        renderer.render.return_value = ("<html>CGV</html>", "CGV text")

        # Mock save to return entity with same data
        def save_attached_terms(terms):
            return terms

        attached_terms_repo.save.side_effect = save_attached_terms

        # Create use case
        assembler = LegalTermsAssembler()
        use_case = AttachTermsToQuoteUseCase(
            profile_repo,
            template_repo,
            attached_terms_repo,
            account_service,
            renderer,
            assembler,
        )

        # Execute
        input_dto = AttachTermsInput(quote_id="quote-1", account_id="acc-1")
        result = use_case.execute(input_dto)

        # Verify
        assert result.template_version == "1.0.0"
        assert result.attached_terms_id is not None

        # Verify repositories called
        template_repo.get_active_for_jurisdiction.assert_called_once_with("FR")
        profile_repo.get_or_create_for_account.assert_called_once()
        account_service.get_template_variables.assert_called_once_with("acc-1")
        renderer.render.assert_called_once()
        attached_terms_repo.save.assert_called_once()

        # Verify saved attached terms has correct structure
        saved_terms = attached_terms_repo.save.call_args[0][0]
        assert saved_terms.quote_id == "quote-1"
        assert saved_terms.template_version == "1.0.0"
        assert saved_terms.rendered_html == "<html>CGV</html>"
        assert saved_terms.rendered_text == "CGV text"
        assert "clauses" in saved_terms.snapshot_data
        assert "variables_used" in saved_terms.snapshot_data

    def test_fails_when_no_active_template(self, mock_repositories):
        """Should raise NoActiveTemplateError when no template found."""
        (
            profile_repo,
            template_repo,
            attached_terms_repo,
            account_service,
            renderer,
        ) = mock_repositories

        # Setup mock - no template
        template_repo.get_active_for_jurisdiction.return_value = None

        # Create use case
        assembler = LegalTermsAssembler()
        use_case = AttachTermsToQuoteUseCase(
            profile_repo,
            template_repo,
            attached_terms_repo,
            account_service,
            renderer,
            assembler,
        )

        # Execute and verify exception
        input_dto = AttachTermsInput(quote_id="quote-1", account_id="acc-1")
        with pytest.raises(NoActiveTemplateError) as exc_info:
            use_case.execute(input_dto)

        assert exc_info.value.jurisdiction == "FR"

    def test_fails_on_missing_template_variables(self, mock_repositories, sample_template, sample_profile):
        """Should raise MissingTemplateVariablesError when variables missing."""
        (
            profile_repo,
            template_repo,
            attached_terms_repo,
            account_service,
            renderer,
        ) = mock_repositories

        # Setup mocks
        template_repo.get_active_for_jurisdiction.return_value = sample_template
        profile_repo.get_or_create_for_account.return_value = sample_profile
        account_service.get_template_variables.side_effect = MissingTemplateVariablesError(["siret"])

        # Create use case
        assembler = LegalTermsAssembler()
        use_case = AttachTermsToQuoteUseCase(
            profile_repo,
            template_repo,
            attached_terms_repo,
            account_service,
            renderer,
            assembler,
        )

        # Execute and verify exception
        input_dto = AttachTermsInput(quote_id="quote-1", account_id="acc-1")
        with pytest.raises(MissingTemplateVariablesError) as exc_info:
            use_case.execute(input_dto)

        assert "siret" in exc_info.value.missing_variables

        # Verify save was never called
        attached_terms_repo.save.assert_not_called()

    def test_creates_immutable_snapshot(self, mock_repositories, sample_template, sample_profile, sample_variables):
        """Attached terms should contain immutable snapshot with all data."""
        (
            profile_repo,
            template_repo,
            attached_terms_repo,
            account_service,
            renderer,
        ) = mock_repositories

        # Setup mocks
        template_repo.get_active_for_jurisdiction.return_value = sample_template
        profile_repo.get_or_create_for_account.return_value = sample_profile
        account_service.get_template_variables.return_value = sample_variables
        renderer.render.return_value = ("<html>CGV</html>", "CGV text")

        def save_attached_terms(terms):
            return terms

        attached_terms_repo.save.side_effect = save_attached_terms

        # Create use case
        assembler = LegalTermsAssembler()
        use_case = AttachTermsToQuoteUseCase(
            profile_repo,
            template_repo,
            attached_terms_repo,
            account_service,
            renderer,
            assembler,
        )

        # Execute
        input_dto = AttachTermsInput(quote_id="quote-1", account_id="acc-1")
        use_case.execute(input_dto)

        # Verify snapshot structure
        saved_terms = attached_terms_repo.save.call_args[0][0]
        snapshot = saved_terms.snapshot_data

        assert snapshot["template_version"] == "1.0.0"
        assert snapshot["template_name"] == "CGV FR"
        assert len(snapshot["clauses"]) == 1
        assert snapshot["clauses"][0]["identifier"] == "payment"
        assert snapshot["variables_used"]["SIRET"] == "12345678901234"
        assert snapshot["variables_used"]["BUSINESS_NAME"] == "ACME Corp"
