import pytest

from apps.client.application.dto.client_inputs import CreateClientInput
from apps.client.application.usecases.create_client import CreateClient
from apps.client.domain.errors import ClientAlreadyExistsError


class FakeClient:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "fake-uuid")
        self.owner_id = kwargs.get("owner_id")
        self.name = kwargs.get("name")
        self.email = kwargs.get("email", "")
        self.phone = kwargs.get("phone", "")
        self.address = kwargs.get("address", "")
        self.vat_number = kwargs.get("vat_number", "")
        self.metadata = kwargs.get("metadata", {})

    @property
    def created_at(self):
        from datetime import datetime

        return datetime(2025, 1, 1, 12, 0, 0)

    @property
    def updated_at(self):
        from datetime import datetime

        return datetime(2025, 1, 1, 12, 0, 0)


class FakeClientRepository:
    def __init__(self):
        self.clients = []
        self.create_called = False

    def create(self, data: dict) -> FakeClient:
        self.create_called = True
        client = FakeClient(**data)
        self.clients.append(client)
        return client

    def exists_by_owner_name(self, owner_id: int, name: str) -> bool:
        return any(c.owner_id == owner_id and c.name == name for c in self.clients)


class TestCreateClientUseCase:
    def test_create_client_success(self):
        """Should create client when name is unique for owner"""
        repo = FakeClientRepository()
        use_case = CreateClient(repo=repo)

        inp = CreateClientInput(
            owner_id=1,
            name="New Client",
            email="client@example.com",
            phone="123456",
            address="Paris",
            vat_number="FR123",
            metadata={"key": "value"},
        )

        result = use_case.execute(inp)

        assert result.name == "New Client"
        assert result.email == "client@example.com"
        assert result.phone == "123456"
        assert result.owner_id == 1
        assert repo.create_called is True

    def test_create_client_raises_error_when_duplicate_name(self):
        """Should raise ClientAlreadyExistsError when client name exists for owner"""
        repo = FakeClientRepository()
        # Pre-create a client
        repo.create({"owner_id": 1, "name": "Existing Client"})

        use_case = CreateClient(repo=repo)

        inp = CreateClientInput(owner_id=1, name="Existing Client", email="new@example.com")

        with pytest.raises(ClientAlreadyExistsError) as exc:
            use_case.execute(inp)

        assert "Client already exists: Existing Client" in str(exc.value)

    def test_create_client_allows_duplicate_name_for_different_owner(self):
        """Should allow same name for different owners"""
        repo = FakeClientRepository()
        # Pre-create a client for owner 1
        repo.create({"owner_id": 1, "name": "Shared Name"})

        use_case = CreateClient(repo=repo)

        # Should succeed for owner 2
        inp = CreateClientInput(owner_id=2, name="Shared Name", email="owner2@example.com")

        result = use_case.execute(inp)

        assert result.name == "Shared Name"
        assert result.owner_id == 2
