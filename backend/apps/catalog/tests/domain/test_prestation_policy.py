# apps/catalog/tests/domain/test_prestation_policy.py
"""
Tests unitaires pour les politiques du domaine.
Tests purs, sans dépendance Django.
"""
import pytest

from apps.catalog.domain.errors import (
    InvalidPrestationNameError,
    InvalidRateError,
    InvalidStatusTransitionError,
    InvalidWeightDaysError,
)
from apps.catalog.domain.policies.prestation_policy import (
    PrestationPolicy,
    PrestationStatus,
)


class TestPrestationPolicy:
    """Tests de la politique de validation des prestations."""

    def test_validate_name_success(self):
        """Test validation d'un nom valide."""
        # Ne doit pas lever d'exception
        PrestationPolicy.validate_name("Développement Web")
        PrestationPolicy.validate_name("Dev")  # 3 chars minimum

    def test_validate_name_too_short(self):
        """Test validation d'un nom trop court."""
        with pytest.raises(InvalidPrestationNameError):
            PrestationPolicy.validate_name("AB")  # < 3 chars

    def test_validate_name_empty(self):
        """Test validation d'un nom vide."""
        with pytest.raises(InvalidPrestationNameError):
            PrestationPolicy.validate_name("")

        with pytest.raises(InvalidPrestationNameError):
            PrestationPolicy.validate_name("   ")

    def test_validate_name_too_long(self):
        """Test validation d'un nom trop long."""
        long_name = "X" * 121  # > 120 chars
        with pytest.raises(InvalidPrestationNameError):
            PrestationPolicy.validate_name(long_name)

    def test_validate_weight_days_success(self):
        """Test validation de jours-homme valides."""
        PrestationPolicy.validate_weight_days(1)
        PrestationPolicy.validate_weight_days(100)

    def test_validate_weight_days_invalid(self):
        """Test validation de jours-homme invalides."""
        with pytest.raises(InvalidWeightDaysError):
            PrestationPolicy.validate_weight_days(0)

        with pytest.raises(InvalidWeightDaysError):
            PrestationPolicy.validate_weight_days(-5)

    def test_validate_rate_cents_success(self):
        """Test validation de tarifs valides."""
        PrestationPolicy.validate_rate_cents(0)
        PrestationPolicy.validate_rate_cents(120000)

    def test_validate_rate_cents_invalid(self):
        """Test validation de tarifs invalides."""
        with pytest.raises(InvalidRateError):
            PrestationPolicy.validate_rate_cents(-100)

    def test_can_transition_draft_to_active(self):
        """Test transition DRAFT -> ACTIVE."""
        assert PrestationPolicy.can_transition_to(PrestationStatus.DRAFT, PrestationStatus.ACTIVE)

    def test_can_transition_draft_to_archived(self):
        """Test transition DRAFT -> ARCHIVED."""
        assert PrestationPolicy.can_transition_to(PrestationStatus.DRAFT, PrestationStatus.ARCHIVED)

    def test_cannot_transition_draft_to_draft(self):
        """Test transition DRAFT -> DRAFT (même statut autorisé)."""
        assert PrestationPolicy.can_transition_to(PrestationStatus.DRAFT, PrestationStatus.DRAFT)

    def test_can_transition_active_to_archived(self):
        """Test transition ACTIVE -> ARCHIVED."""
        assert PrestationPolicy.can_transition_to(PrestationStatus.ACTIVE, PrestationStatus.ARCHIVED)

    def test_cannot_transition_active_to_draft(self):
        """Test transition ACTIVE -> DRAFT (non autorisée)."""
        assert not PrestationPolicy.can_transition_to(PrestationStatus.ACTIVE, PrestationStatus.DRAFT)

    def test_can_transition_archived_to_active(self):
        """Test transition ARCHIVED -> ACTIVE (réactivation)."""
        assert PrestationPolicy.can_transition_to(PrestationStatus.ARCHIVED, PrestationStatus.ACTIVE)

    def test_validate_status_transition_success(self):
        """Test validation de transitions valides."""
        PrestationPolicy.validate_status_transition(PrestationStatus.DRAFT, PrestationStatus.ACTIVE)

    def test_validate_status_transition_invalid(self):
        """Test validation de transitions invalides."""
        with pytest.raises(InvalidStatusTransitionError):
            PrestationPolicy.validate_status_transition(PrestationStatus.ACTIVE, PrestationStatus.DRAFT)

    def test_validate_prestation_data_success(self):
        """Test validation complète de données valides."""
        PrestationPolicy.validate_prestation_data(
            name="Développement Web", weight_days=5, rate_cents=120000, status=PrestationStatus.DRAFT
        )

    def test_validate_prestation_data_invalid_name(self):
        """Test validation complète avec nom invalide."""
        with pytest.raises(InvalidPrestationNameError):
            PrestationPolicy.validate_prestation_data(name="AB", weight_days=5, rate_cents=120000)

    def test_validate_prestation_data_invalid_weight(self):
        """Test validation complète avec weight_days invalide."""
        with pytest.raises(InvalidWeightDaysError):
            PrestationPolicy.validate_prestation_data(name="Développement Web", weight_days=0, rate_cents=120000)
