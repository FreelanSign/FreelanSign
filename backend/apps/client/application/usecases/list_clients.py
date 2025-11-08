from apps.client.application.dto.client_inputs import ListClientsInput
from apps.client.application.dto.client_viewmodels import ClientListViewModel, ClientViewModel
from apps.client.application.ports.client_repository import ClientRepository


class ListClients:
    def __init__(self, repo: ClientRepository):
        self.repo = repo

    def execute(self, inp: ListClientsInput) -> ClientListViewModel:
        qs = self.repo.list(owner_id=inp.owner_id, search=inp.search, ordering=inp.ordering)
        items = [
            ClientViewModel(
                id=str(o.id),
                owner_id=o.owner_id,
                name=o.name,
                email=o.email or None,
                phone=o.phone or None,
                address=o.address or None,
                vat_number=o.vat_number or None,
                metadata=o.metadata or {},
                created_at=o.created_at.isoformat(),
                updated_at=o.updated_at.isoformat(),
            )
            for o in qs
        ]
        return ClientListViewModel(items=items, total_count=len(items))
