# apps/branding/application/usecases/delete_theme.py
from __future__ import annotations

from apps.branding.application.dto.theme_inputs import DeleteThemeDTO
from apps.branding.application.errors import ActiveThemeConflictError
from apps.branding.application.ports.logo_storage import LogoStorage
from apps.branding.application.ports.theme_repository import ThemeRepository
from apps.branding.domain.policies.theme_policy import validate_theme_ownership


class DeleteThemeUseCase:
    """Use case for deleting a brand theme."""

    def __init__(self, theme_repository: ThemeRepository, logo_storage: LogoStorage):
        self.theme_repository = theme_repository
        self.logo_storage = logo_storage

    def execute(self, dto: DeleteThemeDTO) -> None:
        """
        Delete a brand theme.

        Args:
            dto: The delete theme DTO.

        Raise:
            ThemeOwnershipError: If the theme is not owned by the professional.
            ActiveThemeConflictError: If the theme is the active theme.
            RepositoryError: If the theme deletion fails.
        """
        # 1. Get existing theme
        theme = self.theme_repository.get_by_id(theme_id=dto.theme_id, account_id=dto.account_id)

        # 2. Validate ownership
        validate_theme_ownership(theme_account_id=theme.account_id, requester_account_id=dto.account_id)

        # 3. Prevent deleting active theme
        if theme.is_active:
            raise ActiveThemeConflictError("You cannot delete the active theme.")

        # 4. Delete logo if exists
        if theme.logo_url:
            try:
                self.logo_storage.delete_logo(logo_url=theme.logo_url)
            except Exception:
                # Log error but continue
                pass

        # 5. Delete theme via repository
        self.theme_repository.delete_theme(theme_id=dto.theme_id, account_id=dto.account_id)
