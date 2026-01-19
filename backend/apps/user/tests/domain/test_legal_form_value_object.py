# apps/user/tests/domain/test_legal_form_value_object.py
"""
Tests unitaires pour LegalForm value object.
Tests purs, sans dépendance Django.
"""

import pytest

from apps.user.domain.value_objects import LegalForm


class TestLegalForm:
    """Tests pour l'enum LegalForm."""

    def test_legal_form_values(self):
        """Test que tous les statuts juridiques attendus existent."""
        assert hasattr(LegalForm, "MICRO")
        assert hasattr(LegalForm, "EIRL")
        assert hasattr(LegalForm, "EURL")
        assert hasattr(LegalForm, "SASU")
        assert hasattr(LegalForm, "OTHER")

    def test_legal_form_string_values(self):
        """Test que les valeurs sont bien des strings en lowercase."""
        assert LegalForm.MICRO.value == "micro"
        assert LegalForm.EIRL.value == "eirl"
        assert LegalForm.EURL.value == "eurl"
        assert LegalForm.SASU.value == "sasu"
        assert LegalForm.OTHER.value == "other"

    def test_legal_form_membership(self):
        """Test que les valeurs peuvent être vérifiées."""
        valid_forms = [form.value for form in LegalForm]
        assert "micro" in valid_forms
        assert "eirl" in valid_forms
        assert "eurl" in valid_forms
        assert "sasu" in valid_forms
        assert "other" in valid_forms
        assert "invalid" not in valid_forms
