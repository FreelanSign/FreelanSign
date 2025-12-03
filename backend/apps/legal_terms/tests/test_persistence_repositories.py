"""
TDD tests for Django repository implementations.
"""

import uuid
from re import A

import pytest

from apps.legal_terms.adapters.persistence.django_attached_terms_repository import (
    DjangoAttachedTermsRepository,
)
from apps.legal_terms.adapters.persistence.django_legal_profile_repository import (
    DjangoLegalProfileRepository,
)
from apps.legal_terms.adapters.persistence.django_legal_template_repository import (
    DjangoLegalTemplateRepository,
)
from apps.legal_terms.adapters.persistence.models import (
    AttachedTermsModel,
    LegalProfileModel,
    LegalTemplateModel,
)
from apps.legal_terms.domain.entities.attached_terms import AttachedTerms
from apps.legal_terms.domain.entities.legal_profile import LegalProfile
from apps.user.models.account import Account
from apps.user.models.models import User


@pytest.mark.django_db
class TestDjangoLegalTemplateRepository:
    """Tests for DjangoLegalTemplateRepository."""

    def test_get_active_for_jurisdiction(self):
        """Should return active template for jurisdiction."""
        # Use different jurisdiction to avoid seed data
        template_model = LegalTemplateModel.objects.create(
            name="CGV BE Test",
            jurisdiction="BE",
            version="1.0.0-test",
            clauses=[
                {
                    "identifier": "test_clause",
                    "category": "mandatory",
                    "default_title": "Test",
                    "default_body": "Test body",
                    "default_order": 1,
                    "default_is_active": True,
                }
            ],
            is_active=True,
        )

        repo = DjangoLegalTemplateRepository()
        result = repo.get_active_for_jurisdiction("BE")

        assert result is not None
        assert result.id == str(template_model.id)
        assert result.jurisdiction == "BE"
        assert result.version == "1.0.0-test"
        assert len(result.clauses) == 1

    def test_get_active_returns_none_when_not_found(self):
        """Should return None when no active template."""
        repo = DjangoLegalTemplateRepository()
        result = repo.get_active_for_jurisdiction("BE")

        assert result is None

    def test_get_by_id(self):
        """Should return template by ID."""
        template_model = LegalTemplateModel.objects.create(
            name="CGV NL",
            jurisdiction="NL",
            version="1.0.0-test",
            clauses=[],
            is_active=True,
        )

        repo = DjangoLegalTemplateRepository()
        result = repo.get_by_id(str(template_model.id))

        assert result is not None
        assert result.id == str(template_model.id)


@pytest.mark.django_db
class TestDjangoLegalProfileRepository:
    """Tests for DjangoLegalProfileRepository."""

    def test_get_by_account(self):
        """Should return profile by account ID."""
        # Create user and account
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        account = Account.objects.create(user=user, display_name="Test Business")

        # Create template
        template = LegalTemplateModel.objects.create(
            name="CGV FR",
            jurisdiction="DE",
            version="1.0.0-test",
            clauses=[],
            is_active=True,
        )

        # Create profile
        profile_model = LegalProfileModel.objects.create(
            account=account, template=template, clause_overrides={"test": "value"}
        )

        repo = DjangoLegalProfileRepository()
        result = repo.get_by_account(str(account.id))

        assert result is not None
        assert result.id == str(profile_model.id)
        assert result.account_id == str(account.id)
        assert result.template_id == str(template.id)
        assert result.clause_overrides == {"test": "value"}

    def test_get_by_account_returns_none_when_not_found(self):
        """Should return None when profile not found."""
        repo = DjangoLegalProfileRepository()
        result = repo.get_by_account("999999")  # Use integer string for Account ID

        assert result is None

    def test_save_creates_new_profile(self):
        """Should create new profile when doesn't exist."""
        # Create user and account
        user = User.objects.create_user(email="test2@example.com", password="testpass123")
        account = Account.objects.create(user=user, display_name="Test Business 2")

        # Create template
        template = LegalTemplateModel.objects.create(
            name="CGV FR",
            jurisdiction="DE",
            version="1.0.0-test",
            clauses=[],
            is_active=True,
        )

        # Create entity
        profile_id = str(uuid.uuid4())
        profile = LegalProfile(
            id=profile_id,
            account_id=str(account.id),
            template_id=str(template.id),
            template_version="1.0.0-test",
            clause_overrides={"clause1": {"is_active": False}},
        )

        repo = DjangoLegalProfileRepository()
        result = repo.save(profile)

        assert result.id == profile_id
        assert result.clause_overrides == {"clause1": {"is_active": False}}

        # Verify in DB
        saved_model = LegalProfileModel.objects.get(id=profile_id)
        assert saved_model.account_id == account.id

    def test_save_updates_existing_profile(self):
        """Should update existing profile."""
        # Create user and account
        user = User.objects.create_user(email="test3@example.com", password="testpass123")
        account = Account.objects.create(user=user, display_name="Test Business 3")

        # Create template
        template = LegalTemplateModel.objects.create(
            name="CGV FR",
            jurisdiction="DE",
            version="1.0.0-test",
            clauses=[],
            is_active=True,
        )

        # Create profile in DB
        profile_model = LegalProfileModel.objects.create(account=account, template=template, clause_overrides={})

        # Update via entity
        profile = LegalProfile(
            id=str(profile_model.id),
            account_id=str(account.id),
            template_id=str(template.id),
            template_version="1.0.0-test",
            clause_overrides={"clause1": {"custom_title": "Updated"}},
        )

        repo = DjangoLegalProfileRepository()
        result = repo.save(profile)

        assert result.clause_overrides == {"clause1": {"custom_title": "Updated"}}

        # Verify in DB
        profile_model.refresh_from_db()
        assert profile_model.clause_overrides == {"clause1": {"custom_title": "Updated"}}

    def test_get_or_create_for_account_creates_when_not_exists(self):
        """Should create profile when doesn't exist."""
        # Create user and account
        user = User.objects.create_user(email="test4@example.com", password="testpass123")
        account = Account.objects.create(user=user, display_name="Test Business 4")

        # Create template
        template = LegalTemplateModel.objects.create(
            name="CGV FR",
            jurisdiction="DE",
            version="1.0.0-test",
            clauses=[],
            is_active=True,
        )

        repo = DjangoLegalProfileRepository()
        result = repo.get_or_create_for_account(
            account_id=str(account.id),
            template_id=str(template.id),
            template_version="1.0.0-test",
        )

        assert result is not None
        assert result.account_id == str(account.id)
        assert result.template_id == str(template.id)
        assert result.clause_overrides == {}

        # Verify in DB
        assert LegalProfileModel.objects.filter(account=account).exists()

    def test_get_or_create_for_account_returns_existing(self):
        """Should return existing profile."""
        # Create user and account
        user = User.objects.create_user(email="test5@example.com", password="testpass123")
        account = Account.objects.create(user=user, display_name="Test Business 5")

        # Create template
        template = LegalTemplateModel.objects.create(
            name="CGV FR",
            jurisdiction="DE",
            version="1.0.0-test",
            clauses=[],
            is_active=True,
        )

        # Create existing profile
        existing_profile = LegalProfileModel.objects.create(
            account=account,
            template=template,
            clause_overrides={"existing": "data"},
        )

        repo = DjangoLegalProfileRepository()
        result = repo.get_or_create_for_account(
            account_id=str(account.id),
            template_id=str(template.id),
            template_version="1.0.0-test",
        )

        assert result.id == str(existing_profile.id)
        assert result.clause_overrides == {"existing": "data"}


@pytest.mark.django_db
class TestDjangoAttachedTermsRepository:
    """Tests for DjangoAttachedTermsRepository."""

    def test_save_persists_attached_terms(self):
        """Should save attached terms to database."""
        # Create minimal quote compatible with current Quote model
        from decimal import Decimal

        from apps.client.models import Client
        from apps.quote.models import Quote

        user = User.objects.create_user(email="test6@example.com", password="testpass123")
        account = Account.objects.create(user=user, display_name="Test Business 6")
        client = Client.objects.create(owner=user, account=account, name="Test Client", email="client@example.com")
        quote = Quote.objects.create(
            owner=user,
            client=client,
            account=account,
            title="Test quote",
            reference="Q-001",
            currency="EUR",
            language="fr",
            status=Quote.Status.DRAFT,
            issue_date="2024-01-01",
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
        )

        # Create attached terms entity
        terms_id = str(uuid.uuid4())
        attached_terms = AttachedTerms(
            id=terms_id,
            quote_id=str(quote.id),
            template_version="1.0.0-test",
            rendered_html="<html>CGV</html>",
            rendered_text="CGV text",
            snapshot_data={
                "template_version": "1.0.0",
                "clauses": [{"identifier": "test"}],
                "variables_used": {},
            },
        )

        repo = DjangoAttachedTermsRepository()
        result = repo.save(attached_terms)

        assert result.id == terms_id
        assert result.quote_id == str(quote.id)
        assert result.rendered_html == "<html>CGV</html>"

        # Verify in DB
        saved_model = AttachedTermsModel.objects.get(id=terms_id)
        assert saved_model.quote_id == quote.id
        assert saved_model.snapshot_data["clauses"][0]["identifier"] == "test"

    def test_get_by_quote(self):
        """Should return attached terms by quote ID."""
        # Create quote compatible with current Quote model
        from decimal import Decimal

        from apps.client.models import Client
        from apps.quote.models import Quote

        user = User.objects.create_user(email="test7@example.com", password="testpass123")
        account = Account.objects.create(user=user, display_name="Test Business 7")
        client = Client.objects.create(owner=user, account=account, name="Test Client 2", email="client2@example.com")
        quote = Quote.objects.create(
            owner=user,
            client=client,
            account=account,
            title="Test quote 2",
            reference="Q-002",
            currency="EUR",
            language="fr",
            status=Quote.Status.DRAFT,
            issue_date="2024-01-01",
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
        )

        # Create attached terms
        terms_model = AttachedTermsModel.objects.create(
            quote=quote,
            template_version="1.0.0-test",
            rendered_html="<html>Test</html>",
            rendered_text="Test",
            snapshot_data={"clauses": []},
        )

        repo = DjangoAttachedTermsRepository()
        result = repo.get_by_quote(str(quote.id))

        assert result is not None
        assert result.id == str(terms_model.id)
        assert result.quote_id == str(quote.id)

    def test_get_by_quote_returns_none_when_not_found(self):
        """Should return None when no attached terms found."""
        repo = DjangoAttachedTermsRepository()
        result = repo.get_by_quote(str(uuid.uuid4()))

        assert result is None
