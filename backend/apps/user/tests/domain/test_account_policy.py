# apps/user/tests/domain/test_account_policy.py
"""
Tests unitaires pour les politiques du domaine Account.
Tests purs, sans dépendance Django.
"""

import pytest

from apps.user.domain.errors import (
    DuplicateAccountNameError,
    InvalidDisplayNameError,
    InvalidDomainIdError,
    InvalidLegalFormError,
    InvalidLegalIdError,
)
from apps.user.domain.policies.account_policy import AccountPolicy
from apps.user.domain.value_objects import LegalForm


class TestAccountPolicy:
    """Tests de la politique de validation des comptes (Account)."""

    # ===== Display Name Validation =====

    def test_validate_display_name_success(self):
        """Test validation d'un nom d'affichage valide."""
        AccountPolicy.validate_display_name("Ma Société")
        AccountPolicy.validate_display_name("AB")  # 2 chars minimum

    def test_validate_display_name_empty(self):
        """Test validation d'un nom vide."""
        with pytest.raises(InvalidDisplayNameError):
            AccountPolicy.validate_display_name("")

        with pytest.raises(InvalidDisplayNameError):
            AccountPolicy.validate_display_name("   ")

    def test_validate_display_name_too_short(self):
        """Test validation d'un nom trop court."""
        with pytest.raises(InvalidDisplayNameError):
            AccountPolicy.validate_display_name("A")  # < 2 chars

    def test_validate_display_name_too_long(self):
        """Test validation d'un nom trop long."""
        long_name = "X" * 256  # > 255 chars
        with pytest.raises(InvalidDisplayNameError):
            AccountPolicy.validate_display_name(long_name)

    # ===== Legal Form Validation =====

    def test_validate_legal_form_success_string(self):
        """Test validation d'une forme juridique valide (string)."""
        AccountPolicy.validate_legal_form("micro")
        AccountPolicy.validate_legal_form("eirl")
        AccountPolicy.validate_legal_form("eurl")
        AccountPolicy.validate_legal_form("sasu")
        AccountPolicy.validate_legal_form("other")

    def test_validate_legal_form_success_enum(self):
        """Test validation d'une forme juridique valide (enum)."""
        AccountPolicy.validate_legal_form(LegalForm.MICRO)
        AccountPolicy.validate_legal_form(LegalForm.EIRL)

    def test_validate_legal_form_invalid(self):
        """Test validation d'une forme juridique invalide."""
        with pytest.raises(InvalidLegalFormError):
            AccountPolicy.validate_legal_form("sarl")

        with pytest.raises(InvalidLegalFormError):
            AccountPolicy.validate_legal_form("invalid")

    # ===== Legal ID / SIRET Validation =====

    def test_validate_legal_id_success_valid_siret(self):
        """Test validation d'un SIRET valide (14 chiffres)."""
        AccountPolicy.validate_legal_id("12345678901234")  # 14 digits
        AccountPolicy.validate_legal_id("00000000000000")

    def test_validate_legal_id_success_none(self):
        """Test validation avec None (champ optionnel)."""
        AccountPolicy.validate_legal_id(None)  # Should not raise

    def test_validate_legal_id_success_empty_string(self):
        """Test validation avec string vide (considéré comme None)."""
        AccountPolicy.validate_legal_id("")  # Should not raise

    def test_validate_legal_id_invalid_too_short(self):
        """Test validation d'un SIRET trop court."""
        with pytest.raises(InvalidLegalIdError):
            AccountPolicy.validate_legal_id("1234567890123")  # 13 digits

    def test_validate_legal_id_invalid_too_long(self):
        """Test validation d'un SIRET trop long."""
        with pytest.raises(InvalidLegalIdError):
            AccountPolicy.validate_legal_id("123456789012345")  # 15 digits

    def test_validate_legal_id_invalid_non_numeric(self):
        """Test validation d'un SIRET avec caractères non-numériques."""
        with pytest.raises(InvalidLegalIdError):
            AccountPolicy.validate_legal_id("1234567890123A")

        with pytest.raises(InvalidLegalIdError):
            AccountPolicy.validate_legal_id("ABCD1234567890")

        with pytest.raises(InvalidLegalIdError):
            AccountPolicy.validate_legal_id("12345 67890123")  # avec espace

    # ===== Domain ID Validation =====

    def test_validate_domain_id_success(self):
        """Test validation d'un domain_id valide."""
        AccountPolicy.validate_domain_id(1)
        AccountPolicy.validate_domain_id(999)
        AccountPolicy.validate_domain_id(None)  # Optionnel

    def test_validate_domain_id_zero_raises(self):
        """Test validation domain_id = 0."""
        with pytest.raises(InvalidDomainIdError):
            AccountPolicy.validate_domain_id(0)

    def test_validate_domain_id_negative_raises(self):
        """Test validation domain_id négatif."""
        with pytest.raises(InvalidDomainIdError):
            AccountPolicy.validate_domain_id(-1)

        with pytest.raises(InvalidDomainIdError):
            AccountPolicy.validate_domain_id(-999)

    # ===== Composite Validation =====

    def test_validate_account_data_success(self):
        """Test validation complète de données valides."""
        AccountPolicy.validate_account_data(
            display_name="Ma Société SARL",
            legal_form="micro",
            legal_id="12345678901234",
            domain_id=5,
        )

        # Test avec champs optionnels à None
        AccountPolicy.validate_account_data(
            display_name="Freelance Designer",
            legal_form=LegalForm.EURL,
            legal_id=None,
            domain_id=None,
        )

    def test_validate_account_data_invalid_display_name(self):
        """Test validation complète avec display_name invalide."""
        with pytest.raises(InvalidDisplayNameError):
            AccountPolicy.validate_account_data(
                display_name="",  # Invalid
                legal_form="micro",
                legal_id="12345678901234",
                domain_id=1,
            )

    def test_validate_account_data_invalid_legal_id(self):
        """Test validation complète avec legal_id invalide."""
        with pytest.raises(InvalidLegalIdError):
            AccountPolicy.validate_account_data(
                display_name="Ma Société",
                legal_form="micro",
                legal_id="123",  # Too short
                domain_id=1,
            )

    # ===== Unique Display Name Validation =====

    def test_validate_unique_display_name_success(self):
        """Test validation d'un nom unique (pas de conflit)."""
        AccountPolicy.validate_unique_display_name(
            user_id=1,
            display_name="Nouveau Compte",
            existing_names=["Autre Compte", "Compte Pro"],
        )

    def test_validate_unique_display_name_duplicate_exact(self):
        """Test validation avec doublon exact."""
        with pytest.raises(DuplicateAccountNameError):
            AccountPolicy.validate_unique_display_name(
                user_id=1,
                display_name="Mon Compte",
                existing_names=["Mon Compte", "Autre"],
            )

    def test_validate_unique_display_name_case_insensitive(self):
        """Test validation case-insensitive (MyCompany = mycompany)."""
        with pytest.raises(DuplicateAccountNameError):
            AccountPolicy.validate_unique_display_name(
                user_id=1,
                display_name="MyCompany",
                existing_names=["mycompany"],  # Lowercase version
            )

        with pytest.raises(DuplicateAccountNameError):
            AccountPolicy.validate_unique_display_name(
                user_id=1,
                display_name="  FREELANCE  ",  # With spaces
                existing_names=["freelance"],
            )

    def test_validate_unique_display_name_exclude_self_update(self):
        """Test validation avec exclusion du compte en cours de mise à jour."""
        # Scénario: on update le compte ID=5, il garde son nom actuel "Mon Compte"
        # La repository layer doit FILTRER "Mon Compte" de existing_names avant d'appeler
        # Donc ici, on passe seulement "Autre" (le nom du compte ID=5 est déjà exclu)
        AccountPolicy.validate_unique_display_name(
            user_id=1,
            display_name="Mon Compte",
            existing_names=["Autre"],  # "Mon Compte" déjà exclu par la repository
            exclude_account_id=5,
        )
