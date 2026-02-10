import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from apps.client.models import Client
from apps.core.models.audit import AuditLog
from apps.core.services.audit import log_audit
from apps.user.models.account import Account

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user_audit@test.com", password="testpass123")


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(email="admin_audit@test.com", password="testpass123", is_staff=True)


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def api_request_factory():
    return APIRequestFactory()


@pytest.fixture
def user_account(user):
    return Account.objects.create(user=user, display_name="Audit Account", legal_form="micro", is_active=True)


@pytest.fixture
def client_obj(user, user_account):
    return Client.objects.create(owner=user, account=user_account, name="Client To Delete", email="client@test.com")


@pytest.mark.django_db
def test_auditlog_model_casts_target_id(user):
    log = AuditLog.objects.create(
        action=AuditLog.Action.ACCOUNT_CREATED,
        actor=user,
        target_model="Account",
        target_id="123",
    )

    assert log.id is not None
    assert log.target_id == "123"


@pytest.mark.django_db
def test_log_audit_without_request_sets_ip_none():
    log = log_audit(
        action=AuditLog.Action.CLIENT_CREATED,
        actor=None,
        target_model="Client",
        target_id=42,
    )

    assert log.ip_address is None
    assert log.metadata == {}
    assert log.target_id == "42"


@pytest.mark.django_db
def test_log_audit_with_request_extracts_ip(api_request_factory):
    request = api_request_factory.get("/", HTTP_X_FORWARDED_FOR="203.0.113.1, 70.0.0.1")
    # Sécurité : si le header est absent, on tomberait sur REMOTE_ADDR=127.0.0.1
    request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.1, 70.0.0.1"

    log = log_audit(
        action=AuditLog.Action.CLIENT_CREATED,
        actor=None,
        target_model="Client",
        target_id=99,
        request=request,
        metadata={"foo": "bar"},
    )

    assert log.ip_address == "203.0.113.1"
    assert log.metadata == {"foo": "bar"}
    assert log.target_id == "99"


@pytest.mark.django_db
def test_account_creation_emits_audit_log(api_client, user):
    api_client.force_authenticate(user=user)
    payload = {"display_name": "New Audit Account", "legal_form": "sasu"}

    response = api_client.post("/api/user/accounts/", payload)

    assert response.status_code == status.HTTP_201_CREATED
    account_id = response.data["id"]

    log = AuditLog.objects.filter(
        action=AuditLog.Action.ACCOUNT_CREATED,
        target_model="Account",
        target_id=str(account_id),
    ).first()

    assert log is not None
    assert log.actor == user


@pytest.mark.django_db
def test_client_deletion_emits_audit_log(api_client, user, client_obj):
    api_client.force_authenticate(user=user)

    response = api_client.delete(f"/api/clients/{client_obj.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    log = AuditLog.objects.filter(
        action=AuditLog.Action.CLIENT_DELETED,
        target_model="Client",
        target_id=str(client_obj.id),
    ).first()

    assert log is not None
    assert log.actor == user


@pytest.mark.django_db
def test_admin_can_list_audit_logs(api_client, admin_user, user):
    AuditLog.objects.create(
        action=AuditLog.Action.ACCOUNT_CREATED,
        actor=user,
        target_model="Account",
        target_id="abc",
    )
    AuditLog.objects.create(
        action=AuditLog.Action.CLIENT_CREATED,
        actor=user,
        target_model="Client",
        target_id="def",
    )

    api_client.force_authenticate(user=admin_user)
    url = reverse("audit-log-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    results = response.data.get("results", response.data)
    assert len(results) == 2


@pytest.mark.django_db
def test_non_admin_forbidden_on_audit_logs(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("audit-log-list")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
