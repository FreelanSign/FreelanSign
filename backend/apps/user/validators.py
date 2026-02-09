# apps/user/validators.py
import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    """
    Validates that the password contains at least:
    - 8 characters
    - 1 uppercase letter
    - 1 lowercase letter
    - 1 digit
    """

    def validate(self, password, user=None):
        errors = []
        if len(password) < 8:
            errors.append(_("Le mot de passe doit contenir au moins 8 caracteres."))
        if not re.search(r"[A-Z]", password):
            errors.append(_("Le mot de passe doit contenir au moins une majuscule."))
        if not re.search(r"[a-z]", password):
            errors.append(_("Le mot de passe doit contenir au moins une minuscule."))
        if not re.search(r"\d", password):
            errors.append(_("Le mot de passe doit contenir au moins un chiffre."))
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _("Le mot de passe doit contenir au moins 8 caracteres, " "une majuscule, une minuscule et un chiffre.")
