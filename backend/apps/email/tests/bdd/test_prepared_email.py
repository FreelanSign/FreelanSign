# backend/apps/email/tests/bdd/test_prepared_email.py
import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.django_db

scenarios("features/get_prepared_email.feature")
