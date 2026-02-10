"""
Tests for RGPD retention policy management command.

Tests cover:
- Audit log purge (> 395 days)
- Soft-deleted Account purge (> 10 years)
- Soft-deleted Client purge (> 10 years)
- Protection logic (active quotes, recent quotes)
- Dry-run mode
- Force mode
- Configuration validation
"""

from datetime import timedelta
from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from apps.client.models import Client
from apps.core.models.audit import AuditLog
from apps.quote.models import Quote
from apps.user.models.account import Account

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="retention_test@test.com", password="testpass123")


@pytest.fixture
def account(user):
    return Account.objects.create(user=user, display_name="Test Account", legal_form="micro", is_active=True)


@pytest.fixture
def client_obj(user, account):
    return Client.objects.create(owner=user, account=account, name="Test Client", email="client@test.com")


# AIDEV-NOTE: Helper function to call management command
def call_retention_policy(dry_run=False, force=False):
    """Helper to call retention policy command and capture output."""
    out = StringIO()
    err = StringIO()
    args = []
    if dry_run:
        args.append("--dry-run")
    if force:
        args.append("--force")

    call_command("apply_retention_policy", *args, stdout=out, stderr=err)
    return out.getvalue(), err.getvalue()


# ====================================================================================
# Test: Configuration Validation
# ====================================================================================


@pytest.mark.django_db
@override_settings(RETENTION_POLICY_ENABLED=False, DEBUG=False)
def test_command_fails_when_policy_disabled_in_production():
    """Policy must be explicitly enabled in production."""
    with pytest.raises(Exception) as exc_info:
        call_retention_policy()
    assert "RETENTION_POLICY_ENABLED is False" in str(exc_info.value)


@pytest.mark.django_db
@override_settings(RETENTION_POLICY_ENABLED=False, DEBUG=True)
def test_command_succeeds_with_force_flag_in_dev():
    """Force flag allows execution when policy is disabled (dev environment)."""
    out, err = call_retention_policy(force=True)
    assert "Starting retention policy" in out
    assert "applied successfully" in out


# ====================================================================================
# Test: Audit Log Purge
# ====================================================================================


@pytest.mark.django_db
@override_settings(RETENTION_POLICY_ENABLED=True, RETENTION_AUDIT_LOGS_DAYS=395)
def test_purge_old_audit_logs(user):
    """Audit logs older than 395 days should be purged."""
    old_timestamp = timezone.now() - timedelta(days=400)
    old_log1 = AuditLog.objects.create(
        action=AuditLog.Action.CLIENT_CREATED, actor=user, target_model="Client", target_id="123"
    )
    AuditLog.objects.filter(id=old_log1.id).update(timestamp=old_timestamp)

    old_log2 = AuditLog.objects.create(
        action=AuditLog.Action.ACCOUNT_CREATED,
        actor=user,
        target_model="Account",
        target_id="456",
    )
    AuditLog.objects.filter(id=old_log2.id).update(timestamp=old_timestamp)

    # Create recent audit log (< 395 days) - should NOT be purged
    recent_log = AuditLog.objects.create(
        action=AuditLog.Action.CLIENT_DELETED, actor=user, target_model="Client", target_id="789"
    )

    # Run retention policy
    out, err = call_retention_policy()

    # Verify old logs were purged
    assert not AuditLog.objects.filter(id=old_log1.id).exists()
    assert not AuditLog.objects.filter(id=old_log2.id).exists()

    # Verify recent log was NOT purged
    assert AuditLog.objects.filter(id=recent_log.id).exists()

    # Verify output
    assert "Purging 2 AuditLog records" in out
    assert "applied successfully" in out


@pytest.mark.django_db
@override_settings(RETENTION_POLICY_ENABLED=True)
def test_no_purge_when_no_old_audit_logs(user):
    """No purge when all audit logs are recent."""
    # Create only recent logs
    AuditLog.objects.create(action=AuditLog.Action.CLIENT_CREATED, actor=user, target_model="Client", target_id="123")

    out, err = call_retention_policy()

    # Verify no purge occurred
    assert "No AuditLog records older than" in out
    assert AuditLog.objects.count() == 1


# ====================================================================================
# Test: Soft-Deleted Account Purge
# ====================================================================================


@pytest.mark.django_db
@override_settings(RETENTION_POLICY_ENABLED=True, RETENTION_ACCOUNTING_YEARS=10)
def test_purge_old_soft_deleted_accounts(user):
    """Soft-deleted accounts older than 10 years should be purged."""
    # Create soft-deleted account (> 10 years)
    old_account = Account.objects.create(user=user, display_name="Old Account", legal_form="micro", is_active=False)
    old_account.is_deleted = True
    old_account.deleted_at = timezone.now() - timedelta(days=10 * 365 + 30)
    old_account.save()

    # Create recent soft-deleted account (< 10 years) - should NOT be purged
    recent_account = Account.objects.create(user=user, display_name="Recent Account", legal_form="micro", is_active=False)
    recent_account.is_deleted = True
    recent_account.deleted_at = timezone.now() - timedelta(days=365)
    recent_account.save()

    # Run retention policy
    out, err = call_retention_policy()

    # Verify old account was purged
    assert not Account.all_objects.filter(id=old_account.id).exists()

    # Verify recent account was NOT purged
    assert Account.all_objects.filter(id=recent_account.id).exists()

    # Verify output
    assert "Purging 1 soft-deleted Accounts" in out


@pytest.mark.django_db
@override_settings(RETENTION_POLICY_ENABLED=True, RETENTION_ACCOUNTING_YEARS=10)
def test_protect_account_with_active_quotes(user, account, client_obj):
    """Accounts with active quotes should be protected from purge."""
    # Soft-delete account (> 10 years)
    account.is_deleted = True
    account.deleted_at = timezone.now() - timedelta(days=10 * 365 + 30)
    account.save()

    # Create ACTIVE quote (DRAFT status)
    Quote.objects.create(
        owner=user,
        account=account,
        client=client_obj,
        title="Active Quote",
        reference="QTE-001",
        status=Quote.Status.DRAFT,
        issue_date=timezone.now().date(),
        currency="EUR",
        language="fr",
    )

    # Run retention policy
    out, err = call_retention_policy()

    # Verify account was NOT purged (protected by active quote)
    assert Account.all_objects.filter(id=account.id).exists()

    # Verify output shows protection
    assert "protected: 1" in out


@pytest.mark.django_db
@override_settings(RETENTION_POLICY_ENABLED=True, RETENTION_ACCOUNTING_YEARS=10)
def test_protect_account_with_recent_quotes(user, account, client_obj):
    """Accounts with quotes < 10 years old should be protected."""
    # Soft-delete account (> 10 years)
    account.is_deleted = True
    account.deleted_at = timezone.now() - timedelta(days=10 * 365 + 30)
    account.save()

    # Create quote with recent created_at (< 10 years)
    recent_quote = Quote.objects.create(
        owner=user,
        account=account,
        client=client_obj,
        title="Recent Quote",
        reference="QTE-002",
        status=Quote.Status.PAID,  # Even paid quotes protect if recent
        issue_date=timezone.now().date(),
        currency="EUR",
        language="fr",
    )
    # Simulate quote created < 10 years ago
    recent_quote.created_at = timezone.now() - timedelta(days=5 * 365)
    recent_quote.save()

    # Run retention policy
    out, err = call_retention_policy()

    # Verify account was NOT purged (protected by recent quote)
    assert Account.all_objects.filter(id=account.id).exists()


# ====================================================================================
# Test: Soft-Deleted Client Purge
# ====================================================================================


@pytest.mark.django_db
@override_settings(RETENTION_POLICY_ENABLED=True, RETENTION_ACCOUNTING_YEARS=10)
def test_purge_old_soft_deleted_clients(user, account):
    """Soft-deleted clients older than 10 years should be purged."""
    # Create soft-deleted client (> 10 years)
    old_client = Client.objects.create(owner=user, account=account, name="Old Client", email="old@test.com")
    old_client.is_deleted = True
    old_client.deleted_at = timezone.now() - timedelta(days=10 * 365 + 30)
    old_client.save()

    # Create recent soft-deleted client (< 10 years) - should NOT be purged
    recent_client = Client.objects.create(owner=user, account=account, name="Recent Client", email="recent@test.com")
    recent_client.is_deleted = True
    recent_client.deleted_at = timezone.now() - timedelta(days=365)
    recent_client.save()

    # Run retention policy
    out, err = call_retention_policy()

    # Verify old client was purged
    assert not Client.all_objects.filter(id=old_client.id).exists()

    # Verify recent client was NOT purged
    assert Client.all_objects.filter(id=recent_client.id).exists()

    # Verify output
    assert "Purging 1 soft-deleted Clients" in out


@pytest.mark.django_db
@override_settings(RETENTION_POLICY_ENABLED=True, RETENTION_ACCOUNTING_YEARS=10)
def test_protect_client_with_recent_quotes(user, account, client_obj):
    """Clients with quotes < 10 years old should be protected."""
    # Soft-delete client (> 10 years)
    client_obj.is_deleted = True
    client_obj.deleted_at = timezone.now() - timedelta(days=10 * 365 + 30)
    client_obj.save()

    # Create quote with recent created_at
    recent_quote = Quote.objects.create(
        owner=user,
        account=account,
        client=client_obj,
        title="Recent Quote",
        reference="QTE-003",
        status=Quote.Status.PAID,
        issue_date=timezone.now().date(),
        currency="EUR",
        language="fr",
    )
    recent_quote.created_at = timezone.now() - timedelta(days=5 * 365)
    recent_quote.save()

    # Run retention policy
    out, err = call_retention_policy()

    # Verify client was NOT purged (protected by recent quote)
    assert Client.all_objects.filter(id=client_obj.id).exists()


# ====================================================================================
# Test: Dry-Run Mode
# ====================================================================================


@pytest.mark.django_db
@override_settings(RETENTION_POLICY_ENABLED=True, RETENTION_AUDIT_LOGS_DAYS=395)
def test_dry_run_mode_no_database_changes(user):
    """Dry-run mode should show what would be deleted without making changes."""
    old_timestamp = timezone.now() - timedelta(days=400)
    old_log = AuditLog.objects.create(
        action=AuditLog.Action.CLIENT_CREATED, actor=user, target_model="Client", target_id="123"
    )
    AuditLog.objects.filter(id=old_log.id).update(timestamp=old_timestamp)

    # Run dry-run
    out, err = call_retention_policy(dry_run=True)

    # Verify no changes were made
    assert AuditLog.objects.filter(id=old_log.id).exists()

    # Verify output shows dry-run mode
    assert "DRY-RUN" in out
    assert "no database changes made" in out
    assert "Purging 1 AuditLog records" in out


# ====================================================================================
# Test: Batch Processing (Large Datasets)
# ====================================================================================


@pytest.mark.django_db
@override_settings(RETENTION_POLICY_ENABLED=True, RETENTION_AUDIT_LOGS_DAYS=395)
def test_purge_large_number_of_audit_logs(user):
    """Test batch processing with large dataset (1000+ records)."""
    old_timestamp = timezone.now() - timedelta(days=400)
    bulk_logs = [
        AuditLog(action=AuditLog.Action.CLIENT_CREATED, actor=user, target_model="Client", target_id=str(i))
        for i in range(1500)
    ]
    AuditLog.objects.bulk_create(bulk_logs)
    AuditLog.objects.all().update(timestamp=old_timestamp)

    # Run retention policy
    out, err = call_retention_policy()

    # Verify all old logs were purged
    assert AuditLog.objects.count() == 0

    # Verify output
    assert "Purging 1500 AuditLog records" in out
    assert "applied successfully" in out


# ====================================================================================
# Test: Summary Output
# ====================================================================================


@pytest.mark.django_db
@override_settings(RETENTION_POLICY_ENABLED=True, RETENTION_AUDIT_LOGS_DAYS=395, RETENTION_ACCOUNTING_YEARS=10)
def test_summary_output(user, account):
    """Verify summary shows correct purge counts."""
    old_timestamp = timezone.now() - timedelta(days=400)
    l1 = AuditLog.objects.create(action=AuditLog.Action.CLIENT_CREATED, actor=user, target_model="Client", target_id="123")
    l2 = AuditLog.objects.create(action=AuditLog.Action.CLIENT_DELETED, actor=user, target_model="Client", target_id="456")
    AuditLog.objects.filter(id__in=[l1.id, l2.id]).update(timestamp=old_timestamp)

    old_client = Client.objects.create(owner=user, account=account, name="Old Client", email="old@test.com")
    old_client.is_deleted = True
    old_client.deleted_at = timezone.now() - timedelta(days=10 * 365 + 30)
    old_client.save()

    # Run retention policy
    out, err = call_retention_policy()

    # Verify summary
    assert "Summary:" in out
    assert "AuditLog records purged: 2" in out
    assert "Clients purged: 1" in out
    assert "Total records deleted: 3" in out
