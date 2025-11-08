# backend/apps/quote/tests/adapters/test_reference_generator.py
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.core.models.mixins import DocumentCounter
from apps.quote.adapters.reference.django_quote_reference_generator import DjangoQuoteReferenceGenerator

User = get_user_model()


@pytest.mark.django_db
def test_reference_generator_sequence_per_owner_and_month():
    user1 = User.objects.create_user(email="user1@example.test", password="x")
    user2 = User.objects.create_user(email="user2@example.test", password="x")

    gen = DjangoQuoteReferenceGenerator()

    date1 = date(2025, 11, 4)
    date2 = date(2025, 12, 1)

    reference1 = gen.next_reference(owner_id=user1.id, when=date1)
    reference2 = gen.next_reference(owner_id=user1.id, when=date1)
    reference3 = gen.next_reference(owner_id=user2.id, when=date1)
    reference4 = gen.next_reference(owner_id=user1.id, when=date2)

    assert reference1.endswith("-0001") and reference1.startswith("Q-2025-11-")
    assert reference2.endswith("-0002") and reference2.startswith("Q-2025-11-")
    assert reference3.endswith("-0001") and reference3.startswith("Q-2025-11-")
    assert reference4.endswith("-0001") and reference4.startswith("Q-2025-12-")

    # Vérifie que les compteurs existent bien
    assert DocumentCounter.objects.filter(owner=user1, doc_type="QUOTE", period="2025-11", last_value=2).exists()
    assert DocumentCounter.objects.filter(owner=user2, doc_type="QUOTE", period="2025-11", last_value=1).exists()
    assert DocumentCounter.objects.filter(owner=user1, doc_type="QUOTE", period="2025-12", last_value=1).exists()


@pytest.mark.django_db
def test_reference_generator_defaults_to_today_when_none_date():
    u = User.objects.create_user(email="u@example.test", password="x")
    gen = DjangoQuoteReferenceGenerator()
    ref = gen.next_reference(owner_id=u.id, when=None)
    # Juste des assertions de forme
    today = timezone.localdate()
    prefix = today.strftime("Q-%Y-%m-")
    assert ref.startswith(prefix)
