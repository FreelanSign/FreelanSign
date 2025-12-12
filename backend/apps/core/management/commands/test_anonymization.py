# apps/core/management/commands/test_anonymization.py
"""
Management command for testing RGPD anonymization functions.

This command allows testing account and client anonymization in dev/staging
environments with appropriate safety checks.

Usage:
    python manage.py test_anonymization --account <uuid>
    python manage.py test_anonymization --client <uuid>

@author: AI Assistant
@since: 2025-12-12
@version: 1.0
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.client.application.usecases.anonymize_client import (
    anonymize_client_for_deletion,
)
from apps.client.models import Client
from apps.user.application.usecases.anonymize_account import (
    anonymize_account_for_deletion,
)
from apps.user.models.account import Account

User = get_user_model()


class Command(BaseCommand):
    help = "Test RGPD anonymization functions in dev/staging environments"

    def add_arguments(self, parser):
        parser.add_argument(
            "--account",
            type=str,
            help="UUID of the account to anonymize",
        )
        parser.add_argument(
            "--client",
            type=str,
            help="UUID of the client to anonymize",
        )
        parser.add_argument(
            "--non-interactive",
            action="store_true",
            help="Skip confirmation prompts (use with caution)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force execution even in non-DEBUG mode (DANGEROUS - use only in staging)",
        )

    def handle(self, *args, **options):
        account_id = options.get("account")
        client_id = options.get("client")
        non_interactive = options.get("non_interactive", False)
        force = options.get("force", False)

        # Safety check 1: Ensure DEBUG mode (unless forced)
        if not settings.DEBUG and not force:
            raise CommandError(
                "❌ This command can only be run in DEBUG mode (dev environment). "
                "Use --force flag for staging (with extreme caution)."
            )

        # Safety check 2: At least one argument required
        if not account_id and not client_id:
            raise CommandError("❌ You must specify either --account <uuid> or --client <uuid>")

        # Safety check 3: Cannot specify both
        if account_id and client_id:
            raise CommandError("❌ You can only specify one of --account or --client at a time")

        # Process account anonymization
        if account_id:
            self._anonymize_account(account_id, non_interactive, force)

        # Process client anonymization
        if client_id:
            self._anonymize_client(client_id, non_interactive, force)

    def _anonymize_account(self, account_id: str, non_interactive: bool, force: bool):
        """Anonymize an account after confirmation."""
        try:
            # Fetch account (including soft-deleted ones)
            account = Account.all_objects.select_related("user", "user__profile").get(id=account_id)
        except Account.DoesNotExist:
            raise CommandError(f"❌ Account with ID {account_id} not found")

        # Display account info
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.WARNING("⚠️  ACCOUNT ANONYMIZATION"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"Account ID:       {account.id}")
        self.stdout.write(f"Display Name:     {account.display_name}")
        self.stdout.write(f"User Email:       {account.user.email}")
        self.stdout.write(f"User Name:        {account.user.first_name} {account.user.last_name}")
        self.stdout.write(f"Is Active:        {account.is_active}")
        self.stdout.write(f"Is Deleted:       {account.is_deleted}")

        # Count related quotes
        quotes_count = account.quotes.count()
        self.stdout.write(f"Related Quotes:   {quotes_count}")

        self.stdout.write("\n" + "-" * 60)
        self.stdout.write(self.style.WARNING("⚠️  PERSONAL DATA WILL BE ANONYMIZED:"))
        self.stdout.write(f"  • Account display_name → 'Compte supprimé [{account.id}]'")
        self.stdout.write("  • Account legal_id → None")
        self.stdout.write(f"  • User email → 'deleted_{account.user.id}@anonymized.local'")
        self.stdout.write("  • User first_name → 'Utilisateur'")
        self.stdout.write("  • User last_name → 'Supprimé'")
        self.stdout.write("  • Profile phone → None")
        self.stdout.write("  • Profile avatar_url → None")
        self.stdout.write("\n" + "-" * 60)
        self.stdout.write(self.style.SUCCESS("✓ LEGAL DATA WILL BE PRESERVED:"))
        self.stdout.write(f"  • {quotes_count} quote(s) will remain intact")
        self.stdout.write("  • All amounts, references, dates preserved")
        self.stdout.write("=" * 60 + "\n")

        # Confirmation (unless non-interactive)
        if not non_interactive:
            confirm = input("⚠️  Are you sure you want to anonymize this account? (yes/no): ")
            if confirm.lower() != "yes":
                self.stdout.write(self.style.WARNING("❌ Anonymization cancelled"))
                return

        # Perform anonymization
        try:
            result = anonymize_account_for_deletion(account_id=account_id, actor=None)

            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("✅ ACCOUNT ANONYMIZED SUCCESSFULLY"))
            self.stdout.write("=" * 60)
            self.stdout.write(f"Account ID:  {result['account_id']}")
            self.stdout.write(f"Message:     {result['message']}")
            self.stdout.write("=" * 60 + "\n")

        except Exception as e:
            raise CommandError(f"❌ Anonymization failed: {str(e)}")

    def _anonymize_client(self, client_id: str, non_interactive: bool, force: bool):
        """Anonymize a client after confirmation."""
        try:
            # Fetch client (including soft-deleted ones)
            client = Client.all_objects.select_related("account", "owner").get(id=client_id)
        except Client.DoesNotExist:
            raise CommandError(f"❌ Client with ID {client_id} not found")

        # Display client info
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.WARNING("⚠️  CLIENT ANONYMIZATION"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"Client ID:        {client.id}")
        self.stdout.write(f"Name:             {client.name}")
        self.stdout.write(f"Email:            {client.email}")
        self.stdout.write(f"Phone:            {client.phone}")
        self.stdout.write(f"Account:          {client.account.display_name}")
        self.stdout.write(f"Is Deleted:       {client.is_deleted}")

        # Count related quotes
        quotes_count = client.quotes.count()
        self.stdout.write(f"Related Quotes:   {quotes_count}")

        self.stdout.write("\n" + "-" * 60)
        self.stdout.write(self.style.WARNING("⚠️  PERSONAL DATA WILL BE ANONYMIZED:"))
        self.stdout.write(f"  • Client name → 'Client supprimé [{client.id}]'")
        self.stdout.write(f"  • Client email → 'deleted_{client.id}@anonymized.local'")
        self.stdout.write("  • Client phone → ''")
        self.stdout.write("  • Client address → ''")
        self.stdout.write("  • Client vat_number → ''")
        self.stdout.write("  • Client metadata → {}")
        self.stdout.write("\n" + "-" * 60)
        self.stdout.write(self.style.SUCCESS("✓ LEGAL DATA WILL BE PRESERVED:"))
        self.stdout.write(f"  • {quotes_count} quote(s) will remain intact")
        self.stdout.write("  • All amounts, references, dates preserved")
        self.stdout.write("=" * 60 + "\n")

        # Confirmation (unless non-interactive)
        if not non_interactive:
            confirm = input("⚠️  Are you sure you want to anonymize this client? (yes/no): ")
            if confirm.lower() != "yes":
                self.stdout.write(self.style.WARNING("❌ Anonymization cancelled"))
                return

        # Perform anonymization
        try:
            result = anonymize_client_for_deletion(client_id=client_id, actor=None)

            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("✅ CLIENT ANONYMIZED SUCCESSFULLY"))
            self.stdout.write("=" * 60)
            self.stdout.write(f"Client ID:   {result['client_id']}")
            self.stdout.write(f"Message:     {result['message']}")
            self.stdout.write("=" * 60 + "\n")

        except Exception as e:
            raise CommandError(f"❌ Anonymization failed: {str(e)}")
