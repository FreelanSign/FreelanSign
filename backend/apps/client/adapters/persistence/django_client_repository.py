import logging
from typing import Iterable, Optional

from django.db.models import Q

from apps.client.application.errors import RepositoryError
from apps.client.application.ports.client_repository import ClientRepository
from apps.client.models import Client

logger = logging.getLogger(__name__)


class DjangoClientRepository(ClientRepository):
    def create(self, data: dict) -> Client:
        try:
            return Client.objects.create(**data)
        except Exception as e:
            logger.exception("Erreur create client")
            raise RepositoryError("Erreur technique lors de la création du client", original_error=e)

    def update(self, client_id: str, data: dict) -> Client:
        try:
            obj = Client.objects.get(id=client_id)
            for k, v in data.items():
                setattr(obj, k, v)
            obj.save()
            return obj
        except Client.DoesNotExist:
            raise RepositoryError(f"Client {client_id} introuvable")
        except Exception as e:
            logger.exception("Erreur update client %s", client_id)
            raise RepositoryError("Erreur technique lors de la mise à jour du client", original_error=e)

    def get_by_id(self, client_id: str) -> Optional[Client]:
        try:
            return Client.objects.select_related("owner").get(id=client_id)
        except Client.DoesNotExist:
            return None
        except Exception as e:
            logger.exception("Erreur get_by_id client %s", client_id)
            raise RepositoryError("Erreur technique lors de la récupération du client", original_error=e)

    def list(
        self, owner_id: Optional[int], account_id: Optional[int], search: Optional[str], ordering: Optional[str]
    ) -> Iterable[Client]:
        try:
            qs = Client.objects.all().select_related("owner", "account")
            if account_id is not None:
                qs = qs.filter(account_id=account_id)
            elif owner_id is not None:
                qs = qs.filter(owner_id=owner_id)

            if search:
                qs = qs.filter(Q(name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search))
            if ordering:
                qs = qs.order_by(*[o.strip() for o in ordering.split(",")])
            return qs
        except Exception as e:
            logger.exception("Erreur list clients")
            raise RepositoryError("Erreur technique lors du listing des clients", original_error=e)

    def delete(self, client_id: str) -> None:
        try:
            Client.objects.filter(id=client_id).delete()
        except Exception as e:
            logger.exception("Erreur delete client %s", client_id)
            raise RepositoryError("Erreur technique lors de la suppression du client", original_error=e)

    def exists_by_owner_name(self, owner_id: int, name: str) -> bool:
        # Deprecated: use exists_by_account_name
        try:
            return Client.objects.filter(owner_id=owner_id, name=name).exists()
        except Exception as e:
            logger.exception("Erreur exists_by_owner_name owner_id=%s name=%s", owner_id, name)
            raise RepositoryError("Erreur technique lors de la vérification d'existence du client", original_error=e)

    def exists_by_account_name(self, account_id: int, name: str) -> bool:
        try:
            return Client.objects.filter(account_id=account_id, name=name).exists()
        except Exception as e:
            logger.exception("Erreur exists_by_account_name account_id=%s name=%s", account_id, name)
            raise RepositoryError("Erreur technique lors de la vérification d'existence du client", original_error=e)
