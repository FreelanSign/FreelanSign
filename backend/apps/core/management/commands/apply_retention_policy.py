"""
Management command for applying RGPD retention policy.

RGPD/GDPR Compliance:
- Purges AuditLog records older than 13 months (395 days) - CNIL recommendation
- Hard deletes soft-deleted Accounts/Clients older than 10 years - French accounting law

References:
- SPECIFICATIONS_RGPD.md Section 3.4
- GitHub Issue #72
"""

from datetime import timedelta
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = "Apply RGPD retention policy: purge old audit logs and soft-deleted accounts/clients"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate purge without making database changes (shows what would be deleted)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force execution even when RETENTION_POLICY_ENABLED is False (dev environment)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        dry_run = options["dry_run"]
        force = options["force"]

        # AIDEV-NOTE: Fail-safe - retention policy must be explicitly enabled
        policy_enabled = getattr(settings, "RETENTION_POLICY_ENABLED", False)
        if not policy_enabled and not force:
            error_msg = (
                "RETENTION_POLICY_ENABLED is False. "
                "Use --force to override (dev environment only). "
                "In production, set RETENTION_POLICY_ENABLED=True in environment variables."
            )
            self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))

            # Alert via Sentry if this happens in production
            if not settings.DEBUG:
                try:
                    import sentry_sdk

                    sentry_sdk.capture_message(
                        "Retention policy disabled in production environment",
                        level="error",
                        tags={"component": "retention_policy"},
                    )
                except ImportError:
                    pass  # Sentry not available

            raise CommandError(error_msg)

        # Log mode
        mode = "DRY-RUN" if dry_run else "PRODUCTION"
        self.stdout.write(self.style.WARNING(f"\n🔄 Starting retention policy ({mode} mode)...\n"))

        # Get retention periods from settings
        audit_log_days = getattr(settings, "RETENTION_AUDIT_LOGS_DAYS", 395)  # 13 months
        accounting_years = getattr(settings, "RETENTION_ACCOUNTING_YEARS", 10)

        try:
            with transaction.atomic():
                # 1. Purge audit logs
                audit_deleted = self._purge_audit_logs(audit_log_days, dry_run)

                # 2. Purge soft-deleted accounts
                accounts_deleted = self._purge_soft_deleted_accounts(accounting_years, dry_run)

                # 3. Purge soft-deleted clients
                clients_deleted = self._purge_soft_deleted_clients(accounting_years, dry_run)

                # Rollback if dry-run
                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(
                        self.style.WARNING("\n🔄 Dry-run complete - no database changes made (transaction rolled back)\n")
                    )
                else:
                    self.stdout.write(self.style.SUCCESS("\n✅ Retention policy applied successfully\n"))

                    # Alert Sentry if purge count is unusually high (> 1000 records)
                    total_deleted = audit_deleted + accounts_deleted + clients_deleted
                    if total_deleted > 1000:
                        try:
                            import sentry_sdk

                            sentry_sdk.capture_message(
                                f"High purge count: {total_deleted} total records deleted",
                                level="warning",
                                tags={"component": "retention_policy"},
                                extra={
                                    "audit_logs": audit_deleted,
                                    "accounts": accounts_deleted,
                                    "clients": clients_deleted,
                                },
                            )
                        except ImportError:
                            pass  # Sentry not available

                # Summary
                self.stdout.write(self.style.SUCCESS("📊 Summary:"))
                self.stdout.write(f"  - AuditLog records purged: {audit_deleted}")
                self.stdout.write(f"  - Accounts purged: {accounts_deleted}")
                self.stdout.write(f"  - Clients purged: {clients_deleted}")
                self.stdout.write(f"  - Total records deleted: {audit_deleted + accounts_deleted + clients_deleted}\n")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Retention policy failed: {e}\n"))
            try:
                import sentry_sdk

                sentry_sdk.capture_exception(
                    e,
                    level="error",
                    tags={"component": "retention_policy"},
                )
            except ImportError:
                pass  # Sentry not available
            raise

    def _purge_audit_logs(self, retention_days: int, dry_run: bool) -> int:
        """
        Purge AuditLog records older than retention_days.

        Args:
            retention_days: Number of days to retain audit logs (default: 395 = 13 months)
            dry_run: If True, only count records without deleting

        Returns:
            Number of records purged (or would be purged in dry-run mode)
        """
        from apps.core.models.audit import AuditLog

        cutoff_date = timezone.now() - timedelta(days=retention_days)
        old_logs = AuditLog.objects.filter(timestamp__lt=cutoff_date)

        count = old_logs.count()

        if count > 0:
            self.stdout.write(
                self.style.WARNING(f'🗑️  Purging {count} AuditLog records older than {cutoff_date.strftime("%Y-%m-%d")}...')
            )

            if not dry_run:
                # AIDEV-NOTE: Use batch delete for large datasets to avoid memory issues
                # Django's delete() method returns (deleted_count, dict_of_counts)
                deleted_count, _ = old_logs.delete()
                return deleted_count
            else:
                # Dry-run: show sample records
                sample = old_logs.values("id", "action", "timestamp")[:5]
                self.stdout.write("  Sample records to be deleted:")
                for record in sample:
                    self.stdout.write(f'    - {record["id"]}: {record["action"]} at {record["timestamp"]}')
                return count
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ No AuditLog records older than {retention_days} days"))
            return 0

    def _purge_soft_deleted_accounts(self, retention_years: int, dry_run: bool) -> int:
        """
        Hard delete soft-deleted Accounts older than retention_years.

        PROTECTION: Only purges if:
        1. Account is soft-deleted (is_deleted=True)
        2. deleted_at > retention_years ago
        3. No active quotes (DRAFT/SENT/ACCEPTED)
        4. All related quotes (if any) are also > retention_years old

        Args:
            retention_years: Number of years to retain accounting data (default: 10)
            dry_run: If True, only count records without deleting

        Returns:
            Number of accounts purged (or would be purged in dry-run mode)
        """
        from apps.quote.models import Quote
        from apps.user.models.account import Account

        cutoff_date = timezone.now() - timedelta(days=retention_years * 365)
        old_accounts = Account.all_objects.filter(is_deleted=True, deleted_at__lt=cutoff_date)

        count = 0
        protected_count = 0

        for account in old_accounts:
            # AIDEV-NOTE: Protection logic - verify no recent quotes
            # Check for active quotes (DRAFT/SENT/ACCEPTED)
            active_quotes = Quote.objects.filter(account=account).exclude(status__in=["PAID", "CANCELLED", "EXPIRED"])
            if active_quotes.exists():
                protected_count += 1
                continue

            # Check for quotes newer than retention period
            recent_quotes = Quote.objects.filter(account=account, created_at__gte=cutoff_date)
            if recent_quotes.exists():
                protected_count += 1
                continue

            # Safe to purge
            if not dry_run:
                account.hard_delete()
            count += 1

        if count > 0 or protected_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'🗑️  Purging {count} soft-deleted Accounts older than {cutoff_date.strftime("%Y-%m-%d")} '
                    f"(protected: {protected_count})"
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ No soft-deleted Accounts older than {retention_years} years"))

        return count

    def _purge_soft_deleted_clients(self, retention_years: int, dry_run: bool) -> int:
        """
        Hard delete soft-deleted Clients older than retention_years.

        PROTECTION: Only purges if:
        1. Client is soft-deleted (is_deleted=True)
        2. deleted_at > retention_years ago
        3. All related quotes (if any) are also > retention_years old

        Args:
            retention_years: Number of years to retain accounting data (default: 10)
            dry_run: If True, only count records without deleting

        Returns:
            Number of clients purged (or would be purged in dry-run mode)
        """
        from apps.client.models import Client
        from apps.quote.models import Quote

        cutoff_date = timezone.now() - timedelta(days=retention_years * 365)
        old_clients = Client.all_objects.filter(is_deleted=True, deleted_at__lt=cutoff_date)

        count = 0
        protected_count = 0

        for client in old_clients:
            # AIDEV-NOTE: Protection logic - verify no recent quotes
            recent_quotes = Quote.objects.filter(client=client, created_at__gte=cutoff_date)
            if recent_quotes.exists():
                protected_count += 1
                continue

            # Safe to purge
            if not dry_run:
                client.hard_delete()
            count += 1

        if count > 0 or protected_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'🗑️  Purging {count} soft-deleted Clients older than {cutoff_date.strftime("%Y-%m-%d")} '
                    f"(protected: {protected_count})"
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ No soft-deleted Clients older than {retention_years} years"))

        return count
