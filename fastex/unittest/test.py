import unittest

from decimal import Decimal
from unittest import skip

from fastex import models
from fastex.base_models import Options
from fastex import fields


class Helper(unittest.TestCase):
    """
    Helper class for tests. It creates Options for multiple using.
    """

    def setUp(self):
        super().setUp()
        self.PRIVATE = "PRIVATE"
        self.PUBLIC = "PUBLIC"
        self.options = Options(
            api_url="https://fastcoinexchange.com/api/v1/{method}",
            private=self.PRIVATE,
            public=self.PUBLIC,
            unique_id="test_unique",
        )


class TestModels(Helper, unittest.TestCase):
    """
    Tests for checking models behavior.
    """

    def test_rate(self):
        self.assertTrue(
            models.Rate(self.options).is_valid)

    def test_balance_without_parameters(self):
        self.assertFalse(
            models.Balance(self.options).is_valid)

    def test_balance_with_wrong_parameters(self):
        self.assertFalse(
            models.Balance(self.options, currency='bitcoin').is_valid)

    def test_balance_with_right_parameters(self):
        self.assertTrue(
            models.Balance(self.options, currency=fields.CURRENCY_BTC).is_valid)

    def test_exchange_without_parameters(self):
        self.assertFalse(
            models.Exchange(self.options).is_valid)

    def test_exchange_with_required_parameters(self):
        self.assertTrue(
            models.Exchange(
                self.options,
                amount=Decimal(10.3),
                currency_from=fields.CURRENCY_BTC,
                currency_to=fields.CURRENCY_USD
            ).is_valid)

    def test_exchange_with_not_decimal_amount(self):
        self.assertEqual(
            models.Exchange(
                self.options,
                amount=10,
                currency_from=fields.CURRENCY_BTC,
                currency_to=fields.CURRENCY_USD
            ).get(),
            '{"amount": "should be a Decimal"}')

    def test_exchange_with_all_parameters(self):
        self.assertTrue(models.Exchange(
                self.options,
                amount=Decimal(10.3),
                currency_from=fields.CURRENCY_BTC,
                currency_to=fields.CURRENCY_USD,
                rate_ask=Decimal(252656799000),
                rate_bid=Decimal(249463614000)
            ).is_valid)

    def test_invoice_with_all_parameters(self):
        self.assertTrue(models.Invoice(
            self.options,
            amount=Decimal(10.3),
            currency=fields.CURRENCY_BTC
        ).is_valid)

    def test_invoice_without_parameters(self):
        self.assertFalse(models.Invoice(self.options).is_valid)

    def test_invoice_with_required_parameters(self):
        self.assertTrue(models.Invoice(
                self.options,
                amount=Decimal(10.3)
            ).is_valid)

    def test_invoice_with_not_decimal_amount(self):
        self.assertEqual(
            models.Invoice(
                self.options,
                amount=10.3,
                currency=fields.CURRENCY_BTC,
            ).get(),
            '{"amount": "should be a Decimal"}')

    def test_invoicecheck_without_parameters(self):
        self.assertFalse(models.InvoiceCheck(self.options).is_valid)

    def test_invoicecheck_with_wrong_address(self):
        self.assertEqual(
            models.InvoiceCheck(
                self.options,
                address="OOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"
            ).get(),
            '{"address": "should be a valid Bitcoin Address"}')

    def test_invoicecheck_with_right_parameters(self):
        self.assertTrue(
            models.InvoiceCheck(
                self.options,
                address="111111111111111111111111111111"
            ).is_valid
        )

    @skip
    def test_key_filtering(self):
        rate = models.Rate(self.options)
        response = rate.get()
        self.assertIn('code', response.keys())
        self.assertIn('tm', response.get('data').keys())
        self.assertIn('ask', response.get('data').keys())
        self.assertIn('bid', response.get('data').keys())
        response = rate.get(keys=['tm'])
        self.assertNotIn('code', response.keys())
        self.assertIn('tm', response.keys())
        self.assertEqual(1, len(response))


class TestServer(Helper, unittest.TestCase):
    """
    Tests for checking the server connection.
    """

    @skip
    def test_connection(self):
        response = models.Rate(self.options).get()
        self.assertIn('code', response.keys())
        self.assertEqual(response.get('code'), 0)


if __name__ == '__main__':
    unittest.main()
