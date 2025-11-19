from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.db import connection

from apps.quote.adapters.reference.django_quote_reference_generator import DjangoQuoteReferenceGenerator

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_reference_generator_concurrency_unique_and_gapless():
    # SQLite ne supporte pas select_for_update -> on skip pour éviter un faux négatif
    if connection.vendor == "sqlite":
        pytest.skip("Concurrency test skipped on SQLite (no SELECT ... FOR UPDATE support).")

    u = User.objects.create_user(email="concur@example.test", password="x")
    gen = DjangoQuoteReferenceGenerator()

    day = date(2025, 11, 4)
    N = 8

    def task():
        return gen.next_reference(owner_id=u.id, when=day)

    with ThreadPoolExecutor(max_workers=N) as ex:
        refs = list(ex.map(lambda _: task(), range(N)))

    # Unicité
    assert len(set(refs)) == N, f"Duplicate refs: {refs}"

    # Vérifie qu'on a bien les suffixes 0001..0008 (ordre non garanti entre threads)
    suffixes = sorted(int(r.split("-")[-1]) for r in refs)
    assert suffixes == list(range(1, N + 1))
