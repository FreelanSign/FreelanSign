# apps/user/application/usecases/reset_password.py
import logging

from django.core import signing

from apps.user.application.dto.user_inputs import ResetPasswordInput
from apps.user.application.errors import RepositoryError, UserNotFoundError
from apps.user.application.ports.user_repository import UserRepository
from apps.user.domain.policies.user_policy import UserPolicy

logger = logging.getLogger(__name__)


class ResetPassword:
    """
    Use case: reset a password from a token.
    """

    SIGNER_SALT = "user.reset"

    def __init__(self, user_repository: UserRepository, token_max_age_sec: int):
        self.user_repository = user_repository
        self.token_max_age_sec = token_max_age_sec

    def execute(self, input_dto: ResetPasswordInput) -> None:
        """
        Resets the user's password if the token is valid and not expired.

        Args:
            input_dto: ResetPasswordInput(token, new_password)

        Raises:
            UserNotFoundError: If the user ID in the token is invalid.
            InvalidPasswordError: If the password does not meet policy.
            RepositoryError: For technical issues.
        """
        try:
            payload = signing.loads(
                input_dto.token,
                salt=self.SIGNER_SALT,
                max_age=self.token_max_age_sec,
            )
        except signing.BadSignature:
            logging.warning("ResetPassword: invalid token")
            raise UserNotFoundError()

        user_id = payload.get("user_id")
        if not user_id:
            logger.warning("ResetPassword: missing user_id in token")
        logger.info("ResetPassword: token valid for user_id=%s", user_id)

        # Validate password policy
        UserPolicy.validate_password(input_dto.new_password)

        # Reset password
        try:
            self.user_repository.update_password(user_id=user_id, new_password=input_dto.new_password)
            logger.info("ResetPassword: password updated for user_id=%s", user_id)
        except Exception as e:
            logger.exception("ResetPassword: technical error for user_id=%s", user_id)
            raise RepositoryError("Failed to reset password", original_error=e)
