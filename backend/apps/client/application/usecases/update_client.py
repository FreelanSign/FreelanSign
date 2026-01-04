from apps.client.application.dto.client_inputs import UpdateClientInput
from apps.client.application.dto.client_viewmodels import ClientViewModel
from apps.client.application.ports.client_repository import ClientRepository
from apps.client.domain.policies.client_policies import (
    ensure_name_valid,
    normalize_email,
    normalize_phone_number,
    validate_country_code,
)


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
        # Structured address fields
        if inp.address_line1 is not None:
            payload["address_line1"] = inp.address_line1
        if inp.address_line2 is not None:
            payload["address_line2"] = inp.address_line2
        if inp.city is not None:
            payload["city"] = inp.city
        if inp.postal_code is not None:
            payload["postal_code"] = inp.postal_code
        if inp.country is not None:
            payload["country"] = validate_country_code(inp.country or None)
        if inp.company is not None:
            payload["company"] = inp.company
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
            # Structured address fields
            address_line1=obj.address_line1 or None,
            address_line2=obj.address_line2 or None,
            city=obj.city or None,
            postal_code=obj.postal_code or None,
            country=obj.country or None,
            company=obj.company or None,
            vat_number=obj.vat_number or None,
            metadata=obj.metadata or {},
            created_at=obj.created_at.isoformat(),
            updated_at=obj.updated_at.isoformat(),
        )
