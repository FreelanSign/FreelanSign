from apps.client.application.dto.client_inputs import CreateClientInput
from apps.client.application.dto.client_viewmodels import ClientViewModel
from apps.client.application.ports.client_repository import ClientRepository
from apps.client.domain.policies.client_policies import (
    ensure_name_valid,
    ensure_unique_name_within_account,
    ensure_unique_name_within_owner,
    normalize_email,
    normalize_phone_number,
)


class CreateClient:
    def __init__(self, repo: ClientRepository):
        self.repo = repo

    def execute(self, inp: CreateClientInput) -> ClientViewModel:
        name = ensure_name_valid(inp.name)
        # Phase 5: Check uniqueness within account
        ensure_unique_name_within_account(inp.account_id, name, self.repo.exists_by_account_name)
        # ensure_unique_name_within_owner(inp.owner_id, name, self.repo.exists_by_owner_name)

        phone = normalize_phone_number(inp.phone or None)
        email = normalize_email(inp.email or None)
        data = {
            "owner_id": inp.owner_id,
            "account_id": inp.account_id,  # Phase 5
            "name": name,
            "email": email,
            "phone": phone,
            "address": inp.address or "",
            "vat_number": inp.vat_number or "",
            "metadata": inp.metadata or {},
        }
        obj = self.repo.create(data)
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
