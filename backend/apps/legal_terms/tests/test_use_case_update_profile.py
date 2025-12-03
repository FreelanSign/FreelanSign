"""
TDD tests for UpdateLegalProfileUseCase.
"""

from unittest.mock import Mock

import pytest

from apps.legal_terms.application.dtos.legal_profile_dto import UpdateClauseInput
from apps.legal_terms.application.use_cases.update_legal_profile import (
    UpdateLegalProfileUseCase,
)
from apps.legal_terms.domain.entities.legal_profile import LegalProfile
from apps.legal_terms.domain.entities.legal_template import LegalTemplate
from apps.legal_terms.domain.exceptions import (
    ClauseNotFoundError,
    MandatoryClauseModificationError,
)
from apps.legal_terms.domain.value_objects.clause_category import ClauseCategory


@pytest.fixture
def mock_repositories():
    """Mock repositories."""
    profile_repo = Mock()
    template_repo = Mock()
    return profile_repo, template_repo


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
                "default_body": "Paiement sous 30 jours.",
                "default_order": 1,
                "default_is_active": True,
            },
            {
                "identifier": "warranty",
                "category": ClauseCategory.OPTIONAL,
                "default_title": "Garantie",
                "default_body": "Garantie 12 mois.",
                "default_order": 2,
                "default_is_active": True,
            },
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


class TestUpdateLegalProfileUseCase:
    """Tests for UpdateLegalProfileUseCase."""

    def test_applies_overrides(self, mock_repositories, sample_template, sample_profile):
        """Use case should apply clause overrides to profile."""
        profile_repo, template_repo = mock_repositories

        # Setup mocks
        profile_repo.get_by_account.return_value = sample_profile
        template_repo.get_by_id.return_value = sample_template
        profile_repo.save.return_value = sample_profile

        # Create use case
        use_case = UpdateLegalProfileUseCase(profile_repo, template_repo)

        # Execute
        updates = [UpdateClauseInput(identifier="warranty", custom_title="Garantie personnalisée")]
        result = use_case.execute("acc-1", updates)

        # Verify
        assert result.account_id == "acc-1"
        assert "warranty" in result.clause_overrides
        assert result.clause_overrides["warranty"]["custom_title"] == "Garantie personnalisée"

        # Verify save was called
        profile_repo.save.assert_called_once()

    def test_raises_when_profile_not_found(self, mock_repositories):
        """Should raise ValueError when profile not found."""
        profile_repo, template_repo = mock_repositories

        # Setup mock - no profile
        profile_repo.get_by_account.return_value = None

        # Create use case
        use_case = UpdateLegalProfileUseCase(profile_repo, template_repo)

        # Execute and verify
        with pytest.raises(ValueError) as exc_info:
            use_case.execute("acc-1", [])

        assert "No legal profile found" in str(exc_info.value)

    def test_raises_when_clause_not_found(self, mock_repositories, sample_template, sample_profile):
        """Should raise ClauseNotFoundError when updating non-existent clause."""
        profile_repo, template_repo = mock_repositories

        # Setup mocks
        profile_repo.get_by_account.return_value = sample_profile
        template_repo.get_by_id.return_value = sample_template

        # Create use case
        use_case = UpdateLegalProfileUseCase(profile_repo, template_repo)

        # Execute with invalid identifier
        updates = [UpdateClauseInput(identifier="nonexistent", custom_title="Test")]
        with pytest.raises(ClauseNotFoundError) as exc_info:
            use_case.execute("acc-1", updates)

        assert exc_info.value.identifier == "nonexistent"

    def test_prevents_disabling_mandatory_clause(self, mock_repositories, sample_template, sample_profile):
        """Should raise exception when attempting to disable mandatory clause."""
        profile_repo, template_repo = mock_repositories

        # Setup mocks
        profile_repo.get_by_account.return_value = sample_profile
        template_repo.get_by_id.return_value = sample_template

        # Create use case
        use_case = UpdateLegalProfileUseCase(profile_repo, template_repo)

        # Execute with attempt to disable mandatory clause
        updates = [UpdateClauseInput(identifier="payment", is_active=False)]
        with pytest.raises(MandatoryClauseModificationError) as exc_info:
            use_case.execute("acc-1", updates)

        assert exc_info.value.identifier == "payment"

    def test_allows_disabling_optional_clause(self, mock_repositories, sample_template, sample_profile):
        """Should allow disabling optional clauses."""
        profile_repo, template_repo = mock_repositories

        # Setup mocks
        profile_repo.get_by_account.return_value = sample_profile
        template_repo.get_by_id.return_value = sample_template
        profile_repo.save.return_value = sample_profile

        # Create use case
        use_case = UpdateLegalProfileUseCase(profile_repo, template_repo)

        # Execute - disable optional clause
        updates = [UpdateClauseInput(identifier="warranty", is_active=False)]
        result = use_case.execute("acc-1", updates)

        # Verify
        assert "warranty" in result.clause_overrides
        assert result.clause_overrides["warranty"]["is_active"] is False

    def test_applies_multiple_updates(self, mock_repositories, sample_template, sample_profile):
        """Should apply multiple clause updates in one call."""
        profile_repo, template_repo = mock_repositories

        # Setup mocks
        profile_repo.get_by_account.return_value = sample_profile
        template_repo.get_by_id.return_value = sample_template
        profile_repo.save.return_value = sample_profile

        # Create use case
        use_case = UpdateLegalProfileUseCase(profile_repo, template_repo)

        # Execute with multiple updates
        updates = [
            UpdateClauseInput(identifier="payment", custom_title="Titre modifié"),
            UpdateClauseInput(identifier="warranty", is_active=False),
        ]
        result = use_case.execute("acc-1", updates)

        # Verify both updates applied
        assert "payment" in result.clause_overrides
        assert "warranty" in result.clause_overrides
