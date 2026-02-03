# apps/user/domain/errors.py
"""
Erreurs métier du domaine user.
Ces erreurs sont pures, sans dépendance à Django.
"""


class UserDomainError(Exception):
    """Erreur de base pour le domaine user."""

    def __init__(self, message: str, code: str = "USER_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class UserPolicyError(UserDomainError):
    """Erreur de politique liée aux utilisateurs."""

    def __init__(self, message: str):
        super().__init__(message, code="USER_POLICY_ERROR")


class InvalidEmailError(UserPolicyError):
    """Email invalide."""

    def __init__(self, email: str):
        super().__init__(f"Email invalide: '{email}'")


class InvalidPasswordError(UserPolicyError):
    """Mot de passe invalide."""

    def __init__(self, reason: str = ""):
        msg = "Mot de passe invalide"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class InvalidPhoneError(UserPolicyError):
    """Numéro de téléphone invalide."""

    def __init__(self, phone: str):
        super().__init__(f"Numéro de téléphone invalide: '{phone}'")


class InvalidRoleError(UserPolicyError):
    """Rôle invalide."""

    def __init__(self, role: str):
        super().__init__(f"Rôle invalide: '{role}'")


class UnauthorizedRoleAssignmentError(UserPolicyError):
    """Attribution de rôle non autorisée."""

    def __init__(self, role: str, reason: str = ""):
        msg = f"Attribution du rôle '{role}' non autorisée"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class ProfilePolicyError(UserDomainError):
    """Erreur de politique liée aux profils."""

    def __init__(self, message: str):
        super().__init__(message, code="PROFILE_POLICY_ERROR")


class InvalidNameError(ProfilePolicyError):
    """Nom invalide."""

    def __init__(self, name: str, field: str = "name"):
        super().__init__(f"{field.capitalize()} invalide: '{name}'")


# Erreurs pour ProfessionalUser
class ProfessionalPolicyError(UserDomainError):
    """Erreur de politique liée aux professionnels."""

    def __init__(self, message: str):
        super().__init__(message, code="PROFESSIONAL_POLICY_ERROR")


class InvalidTJMError(ProfessionalPolicyError):
    """TJM invalide."""

    def __init__(self, tjm_cents: int):
        super().__init__(f"TJM invalide: {tjm_cents} centimes (doit être >= 0)")


class InvalidStatusJuridiqueError(ProfessionalPolicyError):
    """Statut juridique invalide."""

    def __init__(self, status: str):
        super().__init__(f"Statut juridique invalide: '{status}'")


class DuplicateProfessionalError(ProfessionalPolicyError):
    """Un profil professionnel existe déjà pour cet utilisateur."""

    def __init__(self, user_id: int):
        super().__init__(f"Un profil professionnel existe déjà pour l'utilisateur {user_id}")


# Erreurs pour Account
class AccountPolicyError(UserDomainError):
    """Erreur de politique liée aux comptes professionnels (Account)."""

    def __init__(self, message: str):
        super().__init__(message, code="ACCOUNT_POLICY_ERROR")


class InvalidDisplayNameError(AccountPolicyError):
    """Nom d'affichage invalide."""

    def __init__(self, name: str, reason: str = ""):
        msg = f"Nom d'affichage invalide: '{name}'"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class InvalidLegalFormError(AccountPolicyError):
    """Forme juridique invalide."""

    def __init__(self, legal_form: str):
        super().__init__(f"Forme juridique invalide: '{legal_form}'")


class InvalidLegalIdError(AccountPolicyError):
    """Identifiant légal (SIRET) invalide."""

    def __init__(self, legal_id: str, reason: str = ""):
        msg = f"Identifiant légal invalide: '{legal_id}'"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class InvalidDomainIdError(AccountPolicyError):
    """ID de domaine invalide."""

    def __init__(self, domain_id: int | None):
        super().__init__(f"ID de domaine invalide: {domain_id} (doit être > 0)")


class DuplicateAccountNameError(AccountPolicyError):
    """Un compte avec ce nom existe déjà pour cet utilisateur."""

    def __init__(self, user_id: int, display_name: str):
        super().__init__(f"Un compte nommé '{display_name}' existe déjà pour l'utilisateur {user_id}")


class AccountNotFoundError(AccountPolicyError):
    """Compte non trouvé."""

    def __init__(self, account_id: int, context: str = ""):
        msg = f"Compte {account_id} non trouvé"
        if context:
            msg += f" ({context})"
        super().__init__(msg)


class QuotaExceededError(AccountPolicyError):
    """Quota de compte dépassé (plan gratuit/limité)."""

    def __init__(self, message: str):
        super().__init__(message)
