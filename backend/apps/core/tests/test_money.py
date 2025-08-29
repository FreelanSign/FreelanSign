from decimal import Decimal
from django.test import SimpleTestCase

from apps.core.utils.money import (
    euros_to_cents,
    cents_to_euros,
    format_euros,
    vat_amount_ht,
    apply_vat,
    extract_vat_from_ttc,
)


class TestMoney(SimpleTestCase):
    def test_cents_rounding(self):
        self.assertEqual(euros_to_cents("12.345"), 1235)
        self.assertEqual(euros_to_cents(12.344), 1234)
        self.assertEqual(cents_to_euros(1234), Decimal("12.34"))

    def test_format_euros(self):
        self.assertEqual(format_euros(1234), "12,34 €")
        self.assertEqual(format_euros(-567), "-5,67 €")

    def test_vat_bps(self):
        ht = 10000  # 100,00 €
        tva_20 = vat_amount_ht(ht, 2000)
        self.assertEqual(tva_20, 2000)  # 20,00 €
        self.assertEqual(apply_vat(ht, 2000), 12000)

        ttc = 12000
        ht2, tva2 = extract_vat_from_ttc(ttc, 2000)
        self.assertEqual(ht2, 10000)
        self.assertEqual(tva2, 2000)

    def test_vat_55(self):
        ht = 10000
        ttc = apply_vat(ht, 550)  # 5,5%
        self.assertEqual(ttc, 10550)
        ht2, tva2 = extract_vat_from_ttc(ttc, 550)
        self.assertEqual(ht2, 10000)
        self.assertEqual(tva2, 550)
