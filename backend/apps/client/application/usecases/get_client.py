from apps.client.application.dto.client_inputs import GetClientInput
from apps.client.application.dto.client_viewmodels import ClientViewModel
from apps.client.application.ports.client_repository import ClientRepository


class GetClient:
    def __init__(self, repo: ClientRepository):
        self.repo = repo

    def execute(self, inp: GetClientInput) -> ClientViewModel | None:
        obj = self.repo.get_by_id(inp.client_id)
        if obj is None:
            return None
        return ClientViewModel(
            id=str(obj.id),
            owner_id=obj.owner_id,
            account_id=obj.account_id,  # Phase 5
            name=obj.name,
            email=obj.email or None,
            phone=obj.phone or None,
            address=obj.address or None,
            vat_number=obj.vat_number or None,
            metadata=obj.metadata or {},
            created_at=obj.created_at.isoformat(),
            updated_at=obj.updated_at.isoformat(),
        )
