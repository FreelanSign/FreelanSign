from apps.client.application.dto.client_inputs import UpdateClientInput
from apps.client.application.dto.client_viewmodels import ClientViewModel
from apps.client.application.ports.client_repository import ClientRepository
from apps.client.domain.policies.client_policies import ensure_name_valid, normalize_email, normalize_phone_number


class UpdateClient:
    def __init__(self, repo: ClientRepository):
        self.repo = repo

    def execute(self, inp: UpdateClientInput) -> ClientViewModel:
        payload = {}
        if inp.name is not None:
            payload["name"] = ensure_name_valid(inp.name)
        if inp.email is not None:
            payload["email"] = normalize_email(inp.email or None)
        if inp.phone is not None:
            payload["phone"] = normalize_phone_number(inp.phone or None)
        if inp.address is not None:
            payload["address"] = inp.address
        if inp.vat_number is not None:
            payload["vat_number"] = inp.vat_number
        if inp.metadata is not None:
            payload["metadata"] = inp.metadata

        obj = self.repo.update(inp.client_id, payload)
        return self._to_vm(obj)

    def _to_vm(self, obj) -> ClientViewModel:
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
