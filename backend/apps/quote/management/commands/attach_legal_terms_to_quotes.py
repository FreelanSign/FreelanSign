"""
Django management command to attach legal terms to quotes that don't have them.

Usage:
    python manage.py attach_legal_terms_to_quotes [--dry-run]

This command is useful for migrating old quotes that were created before
the legal terms feature was implemented.
"""

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.legal_terms.adapters.persistence.django_attached_terms_repository import DjangoAttachedTermsRepository
from apps.legal_terms.adapters.persistence.django_legal_profile_repository import DjangoLegalProfileRepository
from apps.legal_terms.adapters.persistence.django_legal_template_repository import DjangoLegalTemplateRepository
from apps.legal_terms.adapters.rendering.template_renderer import TemplateRenderer
from apps.legal_terms.adapters.services.account_service import AccountServiceAdapter
from apps.legal_terms.application.dtos.attach_dto import AttachTermsInput
from apps.legal_terms.application.use_cases.attach_terms_to_quote import AttachTermsToQuoteUseCase
from apps.legal_terms.domain.services.legal_terms_assembler import LegalTermsAssembler
from apps.quote.models import Quote

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Attach legal terms to quotes that don't have them"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without actually doing it",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # Find quotes without legal terms
        self.stdout.write("Finding quotes without legal terms...")

        # Get all quote IDs
        all_quote_ids = set(Quote.objects.values_list("id", flat=True))
        self.stdout.write(f"Total quotes: {len(all_quote_ids)}")

        # Get quote IDs that already have legal terms
        attached_terms_repo = DjangoAttachedTermsRepository()
        quotes_with_terms = set()
        for quote_id in all_quote_ids:
            try:
                attached_terms = attached_terms_repo.get_by_quote(str(quote_id))
                if attached_terms:
                    quotes_with_terms.add(quote_id)
            except Exception:
                # Quote doesn't have legal terms
                pass

        # Calculate quotes without terms
        quotes_without_terms = all_quote_ids - quotes_with_terms
        self.stdout.write(self.style.SUCCESS(f"Quotes with legal terms: {len(quotes_with_terms)}"))
        self.stdout.write(self.style.WARNING(f"Quotes without legal terms: {len(quotes_without_terms)}"))

        if not quotes_without_terms:
            self.stdout.write(self.style.SUCCESS("All quotes already have legal terms!"))
            return

        # Build use case
        use_case = AttachTermsToQuoteUseCase(
            attached_terms_repository=DjangoAttachedTermsRepository(),
            profile_repository=DjangoLegalProfileRepository(),
            template_repository=DjangoLegalTemplateRepository(),
            account_service=AccountServiceAdapter(),
            template_renderer=TemplateRenderer(),
            assembler=LegalTermsAssembler(),
        )

        # Process each quote
        success_count = 0
        error_count = 0
        skipped_count = 0

        for quote_id in quotes_without_terms:
            try:
                # Get quote to find account_id
                quote = Quote.objects.get(id=quote_id)

                # Get account_id
                if hasattr(quote, "account_id") and quote.account_id:
                    account_id = quote.account_id
                elif hasattr(quote, "account") and quote.account:
                    account_id = quote.account.id
                else:
                    self.stdout.write(self.style.WARNING(f"  ⚠ Quote {quote_id} has no account, skipping"))
                    skipped_count += 1
                    continue

                if dry_run:
                    self.stdout.write(
                        f"  [DRY RUN] Would attach legal terms to quote {quote.reference} (account_id={account_id})"
                    )
                    success_count += 1
                else:
                    # Attach legal terms
                    with transaction.atomic():
                        output = use_case.execute(AttachTermsInput(quote_id=str(quote_id), account_id=account_id))
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✓ Attached legal terms to quote {quote.reference} "
                                f"(template_version={output.template_version})"
                            )
                        )
                        success_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Error processing quote {quote_id}: {str(e)}"))
                logger.error(
                    "attach_legal_terms_to_quotes.error quote_id=%s error=%s",
                    quote_id,
                    str(e),
                    exc_info=True,
                )
                error_count += 1

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"Successfully processed: {success_count}"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {error_count}"))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count}"))
        self.stdout.write("=" * 60)

        if dry_run:
            self.stdout.write(self.style.WARNING("\nThis was a DRY RUN. Run without --dry-run to apply changes."))
