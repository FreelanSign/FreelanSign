# apps/quote/tests/conftest.py
from decimal import Decimal
from types import SimpleNamespace

import pytest
from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist
from django.db import IntegrityError
from datetime import date


# ---------- client_model resolver (robust) -----------
@pytest.fixture
def client_model():
    candidates = [
        ("client", "Client"),
        ("clients", "Client"),
        ("app_client", "Client"),
        ("apps.client", "Client"),
        ("apps.clients", "Client"),
        ("accounts", "Client"),
        ("crm", "Client"),
    ]
    for app_label, model_name in candidates:
        try:
            model = django_apps.get_model(app_label, model_name)
            if model is not None:
                return model
        except LookupError:
            continue
    raise LookupError(
        "Could not find Client model. Please adjust the 'candidates' list in "
        "apps/quote/tests/conftest.py or import your Client model directly into the test."
    )


# ---------- user_factory fixture (robust) -------------------------------------
@pytest.fixture
def user_factory(db):
    User = get_user_model()

    PROFILE_CANDIDATES = [
        ("accounts", "Profile"),
        ("users", "Profile"),
        ("app_user", "Profile"),
        ("apps.user", "Profile"),
        ("profiles", "Profile"),
        ("core", "Profile"),
        ("accounts", "UserProfile"),
    ]

    def _create(**kwargs):
        profile_attrs = {}
        for k in list(kwargs.keys()):
            if k.startswith("profile__"):
                profile_attrs[k.split("__", 1)[1]] = kwargs.pop(k)

        email = kwargs.pop("email", None) or f"testuser_{User.objects.count()+1}@example.test"
        password = kwargs.pop("password", None) or "password123"

        user = User.objects.create_user(email=email, password=password, **kwargs)

        # Try to find a concrete Profile model and create DB profile if possible
        profile_model = None
        for app_label, model_name in PROFILE_CANDIDATES:
            try:
                mdl = django_apps.get_model(app_label, model_name)
                if mdl is not None:
                    profile_model = mdl
                    break
            except LookupError:
                continue

        if profile_model and profile_attrs:
            link_field = None
            for f in profile_model._meta.get_fields():
                remote = getattr(f, "remote_field", None)
                if remote:
                    # remote.model might be a class or string
                    try:
                        remote_model = remote.model
                    except Exception:
                        remote_model = None
                    if remote_model is get_user_model() or (
                        isinstance(remote_model, str) and remote_model.lower().endswith(get_user_model().__name__.lower())
                    ):
                        link_field = f
                        break
            if link_field is None:
                for candidate_name in ("user", "owner", "account"):
                    try:
                        link_field = profile_model._meta.get_field(candidate_name)
                        break
                    except FieldDoesNotExist:
                        continue

            create_kwargs = {}
            if link_field:
                create_kwargs[link_field.name] = user
            if "default_tax_rate" in profile_attrs:
                profile_attrs["default_tax_rate"] = Decimal(str(profile_attrs["default_tax_rate"]))
            create_kwargs.update(profile_attrs)
            try:
                profile_model.objects.create(**create_kwargs)
            except Exception:
                user.__dict__["profile"] = SimpleNamespace(**profile_attrs)
        else:
            if profile_attrs:
                if "default_tax_rate" in profile_attrs:
                    profile_attrs["default_tax_rate"] = Decimal(str(profile_attrs["default_tax_rate"]))
                user.__dict__["profile"] = SimpleNamespace(**profile_attrs)

        return user

    return _create

# ---------- user_factory fixture (robust) -------------------------------------
@pytest.fixture
def authenticated_user(db):
    User = get_user_model()
    user = User.objects.create_user(
        email="tester@example.com",     # <-- garde l'email, ton USERNAME_FIELD est l'email
        password="pass1234",
        is_active=True,
    )
    return user

@pytest.fixture
def auth_client(db, client, authenticated_user):
    client.force_login(authenticated_user)
    return client

# ---------- client_factory fixture (fixed: ensures owner) -----------------------
@pytest.fixture
def client_factory(db, client_model, user_factory):
    """
    Returns a factory function to create Client instances.

    Behavior:
      - Detects 'owner' field on Client and ensures it is provided.
      - If no owner passed, uses the first existing user or creates a lightweight user.
      - Detects name-like and country-like fields and only passes valid kwargs to create().
    """
    User = get_user_model()

    concrete_fields = [f for f in client_model._meta.get_fields() if getattr(f, "concrete", False) and not f.auto_created]
    allowed_field_names = {f.name for f in concrete_fields}

    COUNTRY_PREFERRED = [
        "country",
        "country_code",
        "country_iso",
        "billing_country",
        "billing_country_code",
        "address_country",
    ]
    detected_country_field = None
    for cand in COUNTRY_PREFERRED:
        if cand in allowed_field_names:
            detected_country_field = cand
            break

    name_field = None
    for candidate in ("name", "company_name", "title"):
        if candidate in allowed_field_names:
            name_field = candidate
            break
    if name_field is None:
        from django.db.models import CharField

        for f in concrete_fields:
            if isinstance(f, CharField):
                name_field = f.name
                break

    owner_field_name = "owner" if "owner" in allowed_field_names else None

    def _create(**kwargs):
        # capture requested country param early
        country = kwargs.pop("country", "FR")

        data = {}

        # Ensure owner: prefer explicit kwarg, else use first User, else create a default user
        owner = kwargs.pop("owner", None)
        if owner is None:
            owner = User.objects.first()
            if owner is None:
                owner = user_factory(email="client_owner@example.test", password="password123")
        if owner_field_name:
            data[owner_field_name] = owner

        if name_field:
            data[name_field] = kwargs.pop(name_field, kwargs.pop("name", "Test Client"))

        # if the model supports a country field, pass it; else we will store in metadata after create
        if detected_country_field:
            data[detected_country_field] = country

        # copy other allowed fields
        for k, v in list(kwargs.items()):
            if k in allowed_field_names:
                data[k] = kwargs.pop(k)

        try:
            instance = client_model.objects.create(**data)
        except Exception:
            # fallback attempt minimal create
            fallback = {}
            if owner_field_name:
                fallback[owner_field_name] = owner
            if name_field:
                fallback[name_field] = data.get(name_field, "Test Client")
            instance = client_model.objects.create(**fallback)

        # ensure metadata['country'] exists if model has no country field
        if detected_country_field is None:
            try:
                # client_model has a metadata JSONField in your schema — fill it
                md = getattr(instance, "metadata", None)
                if md is None:
                    instance.metadata = {}
                if isinstance(instance.metadata, dict):
                    instance.metadata.setdefault("country", country)
                    instance.save(update_fields=["metadata"])
            except Exception:
                # ignore if not present / writable
                pass

        return instance

@pytest.fixture
def quote_factory(db):
    from apps.quote.models import Quote, QuoteLineItem
    from apps.client.models import Client

    def _make(**overrides):
        User = get_user_model()
        owner = overrides.pop("owner", None) or User.objects.create_user(
            email="owner@example.com",
            password="pass1234",
            is_active=True,
        )
        client = overrides.pop("client", None) or Client.objects.create(
            owner=owner,
            name="ACME",
            email="client@example.com",
        )
        quote = Quote.objects.create(
            owner=owner,
            client=client,
            title=overrides.pop("title", "Test Quote"),
            reference=overrides.pop("reference", "REF-TEST"),
            currency=overrides.pop("currency", "EUR"),
            language=overrides.pop("language", "fr"),
            status=overrides.pop("status", Quote.Status.DRAFT),
            issue_date=overrides.pop("issue_date", date.today()),
            valid_until=overrides.pop("valid_until", None),
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            discount_total=Decimal("0.00"),
            total=Decimal("0.00"),
            metadata=overrides.pop("metadata", {}),
        )
        # 1 ligne simple
        QuoteLineItem.objects.create(
            quote=quote,
            description="Ligne",
            qty=Decimal("1.00"),
            unit_price=Decimal("10.00"),
            tax_rate=Decimal("20.00"),
            discount=Decimal("0.00"),
            line_total=Decimal("10.00"),
            order=0,
            metadata={},
        )
        # recalcule les totaux
        quote.recalculate_totals(save=True)
        return quote

    return _make
