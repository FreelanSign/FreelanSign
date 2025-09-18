from django.test import SimpleTestCase

from apps.core.enums import AddressType, PrestationStatus, QuoteStatus


class TestEnums(SimpleTestCase):
    def test_quote_status_values(self):
        self.assertEqual(
            {s.value for s in QuoteStatus},
            {"draft", "sent", "validated", "canceled", "refused", "deleted"},
        )

    def test_address_type_values(self):
        self.assertEqual(
            {s.value for s in AddressType},
            {"billing", "shipping", "pro"},
        )

    def test_prestation_status_values(self):
        self.assertEqual(
            {s.value for s in PrestationStatus},
            {"active", "canceled", "deleted"},
        )
