import pytest

from apps.client.domain.errors import ClientInvalidNameError
from apps.client.domain.policies.client_policies import ensure_name_valid


def test_ensure_valid_name_ok():
    assert ensure_name_valid("  Foo  ") == "Foo"


def test_ensure_valid_name_ko():
    with pytest.raises(ClientInvalidNameError):
        ensure_name_valid("   ")
