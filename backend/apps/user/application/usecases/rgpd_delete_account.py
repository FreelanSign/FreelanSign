# apps/user/application/usecases/rgpd_delete_account.py
"""Use case: Suppression RGPD d'un compte professionnel (soft delete avec cascade)."""
from apps.user.application.errors import CannotDeleteAccountError
from apps.user.domain.errors import AccountNotFoundError
from apps.user.models.account import Account as AccountModel


class RGPDDeleteAccount:
    """
    Use case pour la suppression RGPD d'un compte (soft delete avec cascade).

    Supprime le compte (is_deleted=True) et cascade vers tous les Clients.
    Bloque si des Quotes actives (DRAFT, SENT, ACCEPTED) existent.

    AIDEV-NOTE: Ce use case travaille directement avec le modèle Django
    car delete() est une opération d'infrastructure (pas de logique métier).

    @author: @Bertrand2808
    @since: 2025-12-09
    @version: 1.0
    """

    def execute(self, account_id: int) -> None:
        """
        Suppression RGPD d'un compte avec cascade vers Clients.

        Args:
            account_id: ID du compte à supprimer

        Raises:
            AccountNotFoundError: Si le compte n'existe pas
            CannotDeleteAccountError: Si des Quotes actives existent
        """
        # 1. Récupérer le modèle Django directement
        # AIDEV-NOTE: Travaille avec AccountModel car delete() est infrastructure
        try:
            account = AccountModel.objects.get(id=account_id)
        except AccountModel.DoesNotExist:
            raise AccountNotFoundError(account_id)

        # 2. Appeler la méthode delete() du modèle (soft delete avec cascade)
        # La méthode Account.delete() gère :
        # - Vérification des Quotes actives (ValueError si bloqué)
        # - Cascade vers Clients
        # - Transaction atomique
        try:
            account.delete()
        except ValueError as e:
            # ValueError levée par Account.delete() si Quotes actives
            raise CannotDeleteAccountError(account_id, str(e)) from e
