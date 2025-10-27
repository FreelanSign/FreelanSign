# apps/user/application/errors.py
"""
Erreurs de la couche application (use cases).
"""


class UserApplicationError(Exception):
    """Erreur de base pour les use cases user."""

    def __init__(self, message: str, code: str = "APPLICATION_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class UserNotFoundError(UserApplicationError):
    """Utilisateur introuvable."""

    def __init__(self, user_id: int = None, email: str = None):
        if user_id:
            msg = f"Utilisateur {user_id} introuvable"
        elif email:
            msg = f"Utilisateur avec l'email {email} introuvable"
        else:
            msg = "Utilisateur introuvable"

        super().__init__(msg, code="USER_NOT_FOUND")
        self.user_id = user_id
        self.email = email


class ProfileNotFoundError(UserApplicationError):
    """Profil introuvable."""

    def __init__(self, user_id: int):
        super().__init__(f"Profil introuvable pour l'utilisateur {user_id}", code="PROFILE_NOT_FOUND")
        self.user_id = user_id


class ProfessionalNotFoundError(UserApplicationError):
    """Professionnel introuvable."""

    def __init__(self, user_id: int = None, professional_id: int = None):
        if user_id:
            msg = f"Professionnel introuvable pour l'utilisateur {user_id}"
        elif professional_id:
            msg = f"Professionnel {professional_id} introuvable"
        else:
            msg = "Professionnel introuvable"

        super().__init__(msg, code="PROFESSIONAL_NOT_FOUND")
        self.user_id = user_id
        self.professional_id = professional_id


class DuplicateEmailError(UserApplicationError):
    """Email déjà utilisé."""

    def __init__(self, email: str):
        super().__init__(f"Un utilisateur avec l'email {email} existe déjà", code="DUPLICATE_EMAIL")
        self.email = email


class IncorrectPasswordError(UserApplicationError):
    """Mot de passe incorrect."""

    def __init__(self):
        super().__init__("Mot de passe actuel incorrect", code="INCORRECT_PASSWORD")


class AuthenticationFailedError(UserApplicationError):
    """Échec d'authentification."""

    def __init__(self, reason: str = ""):
        msg = "Échec d'authentification"
        if reason:
            msg += f": {reason}"
        super().__init__(msg, code="AUTHENTICATION_FAILED")


class RepositoryError(UserApplicationError):
    """Erreur générique du repository."""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message, code="REPOSITORY_ERROR")
        self.original_error = original_error


class UnauthorizedOperationError(UserApplicationError):
    """Opération non autorisée."""

    def __init__(self, message: str):
        super().__init__(message, code="UNAUTHORIZED_OPERATION")
