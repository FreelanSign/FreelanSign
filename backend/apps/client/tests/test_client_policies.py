import pytest

from apps.client.domain.errors import ClientAlreadyExistsError
from apps.client.domain.policies.client_policies import ensure_unique_name_within_owner


class TestEnsureUniqueNameWithinOwner:
    def test_raises_error_when_name_exists_for_owner(self):
        """Should raise ClientAlreadyExistsError when client name already exists for owner"""

        def exists_fn(owner_id: int, name: str) -> bool:
            return owner_id == 1 and name == "Existing Client"

        with pytest.raises(ClientAlreadyExistsError) as exc:
            ensure_unique_name_within_owner(owner_id=1, name="Existing Client", exists_by_owner_name=exists_fn)

        assert "Client already exists: Existing Client" in str(exc.value)
        assert exc.value.code == "CLIENT_ALREADY_EXISTS"

    def test_passes_when_name_does_not_exist(self):
        """Should pass when client name does not exist for owner"""

        def exists_fn(owner_id: int, name: str) -> bool:
            return False

        # Should not raise
        ensure_unique_name_within_owner(owner_id=1, name="New Client", exists_by_owner_name=exists_fn)

    def test_passes_when_name_exists_for_different_owner(self):
        """Should pass when same name exists but for different owner"""

        def exists_fn(owner_id: int, name: str) -> bool:
            return owner_id == 2 and name == "Shared Name"

        # Should not raise for owner_id=1
        ensure_unique_name_within_owner(owner_id=1, name="Shared Name", exists_by_owner_name=exists_fn)
