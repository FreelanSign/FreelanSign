# backend/apps/email/tests/bdd/steps/email_steps.py
from datetime import datetime

import pytest
from django.urls import reverse
from pytest_bdd import given, parsers, then, when
from rest_framework.test import APIClient

from apps.client.models import Client
from apps.quote.models import Quote
from apps.user.models import User

FAKE_UUID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def context():
    return {}  # dict partagé entre les steps


@given(parsers.parse('un utilisateur connecté "{email}"'))
def user_authenticated(api_client, django_user_model, email, context):
    user = django_user_model.objects.create_user(email=email, password="test1234")
    api_client.force_authenticate(user)
    context["user"] = user


@given(parsers.parse('un devis "{ref}" appartenant à "{email}"'))
def create_quote(django_user_model, ref, email, context):
    owner, _ = django_user_model.objects.get_or_create(email=email)
    client = Client.objects.create(owner=owner, name="Client Inc", email="client@example.com")
    quote = Quote.objects.create(
        owner=owner,
        client=client,
        issue_date=datetime.now(),
        reference=ref,
        title="Site web",
    )
    context["quote"] = quote


@when(parsers.parse("elle appelle GET /api/quote/{ref}/prepared-email"))
@when(parsers.parse("il appelle GET /api/quote/{ref}/prepared-email"))
def call_api(api_client, ref, context):
    try:
        quote = Quote.objects.get(reference=ref)
        url = reverse("email:prepared-email", kwargs={"quote_id": str(quote.id)})
    except Quote.DoesNotExist:
        url = f"/api/quote/{ref}/prepared-email"  # simulate not found
    context["response"] = api_client.get(url)


@when(parsers.parse("elle appelle GET /api/quote/{ref}/prepared-email sans être connectée"))
def call_api_unauthenticated(ref, context):
    quote = Quote.objects.get(reference=ref)
    quote_id = str(quote.id)

    client = APIClient()
    url = f"/api/quote/{quote_id}/prepared-email"
    context["response"] = client.get(url)


@then(parsers.parse("la réponse est {code:d}"))
def assert_status(context, code):
    assert context["response"].status_code == code


@then('le JSON contient "to", "subject", "body", "template_version"')
def assert_keys_present(context):
    data = context["response"].json()
    for key in ["to", "subject", "body", "template_version"]:
        assert key in data
