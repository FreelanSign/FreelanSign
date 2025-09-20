# apps/quote/tests/test_serializers.py
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from apps.client.models import Client
from apps.quote.interface.serializers import QuoteCreateUpdateSerializer, QuoteSerializer
from apps.quote.models import Quote, QuoteLineItem

User = get_user_model()


@pytest.fixture
def client_factory(db, request, client_model, user_factory):
    """
    Simple, reliable client factory for tests in this file.

    Usage:
        client = client_factory(country='FR')
        client = client_factory(owner=some_user, country='FR', name='ACME')

    It will:
      - ensure an owner exists (use provided owner, else first user, else create via user_factory)
      - create a Client with minimal required fields (owner + name)
      - store country into metadata['country'] if the Client model does not have an explicit country field
    """

    def _create(**kwargs):
        owner = kwargs.pop("owner", None)
        if owner is None:
            owner = User.objects.first()
            if owner is None:
                owner = user_factory(email="client_owner@example.test")

        # build data to pass to client_model.create()
        data = {}
        # put owner if the model declares an 'owner' field
        try:
            client_model._meta.get_field("owner")
            data["owner"] = owner
        except Exception:
            pass

        # name fallback
        name = kwargs.pop("name", "Test Client")
        # try to find a sensible name field on the model
        name_field = None
        for candidate in ("name", "company_name", "title"):
            try:
                client_model._meta.get_field(candidate)
                name_field = candidate
                break
            except Exception:
                continue
        if name_field:
            data[name_field] = name
        else:
            # fallback: use first charfield
            from django.db.models import CharField

            for f in client_model._meta.get_fields():
                if getattr(f, "concrete", False) and isinstance(f, CharField) and not getattr(f, "auto_created", False):
                    data[f.name] = name
                    break

        # explicitly set metadata if present; else skip
        country = kwargs.pop("country", "FR")
        try:
            meta_field = client_model._meta.get_field("metadata")
            # if metadata field exists, set initial metadata
            data["metadata"] = {"country": country}
        except Exception:
            # no metadata field — we will try to set via attribute after create
            pass

        # include any other allowed fields passed explicitly
        for k, v in list(kwargs.items()):
            try:
                client_model._meta.get_field(k)
                data[k] = v
            except Exception:
                # ignore unknown fields
                continue

        # create instance
        inst = client_model.objects.create(**data)

        # if model has no explicit country field and no metadata already set, try set metadata if possible
        if not hasattr(inst, "country"):
            try:
                md = getattr(inst, "metadata", None)
                if md is None:
                    inst.metadata = {}
                if isinstance(inst.metadata, dict):
                    inst.metadata.setdefault("country", country)
                    inst.save(update_fields=["metadata"])
            except Exception:
                pass

        return inst

    return _create
