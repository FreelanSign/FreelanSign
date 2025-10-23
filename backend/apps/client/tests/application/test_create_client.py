from types import SimpleNamespace

from apps.client.application.dto.client_inputs import CreateClientInput
from apps.client.application.usecases.create_client import CreateClient


class InMemoryRepo:
    def __init__(self):
        self.saved = []

    def create(self, data):
        obj = SimpleNamespace(
            id="uuid-1",
            owner_id=data["owner_id"],
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            address=data["address"],
            vat_number=data["vat_number"],
            metadata=data["metadata"],
            created_at=__import__("datetime").datetime.now(),
            updated_at=__import__("datetime").datetime.now(),
        )
        self.saved.append(obj)
        return obj


def test_create_client_minimal():
    uc = CreateClient(InMemoryRepo())
    vm = uc.execute(CreateClientInput(owner_id=1, name=" ACME "))
    assert vm.name == "ACME"
    assert vm.owner_id == 1
