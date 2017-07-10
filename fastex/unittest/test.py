import unittest

from decimal import Decimal
from unittest import skip

from booby import errors

from fastex import models
from fastex.base_models import Options
from fastex import fields


class SetupHelper(unittest.TestCase):
    """
    Helper class for tests. It creates Options for multiple using.
    """

    def setUp(self):
        super().setUp()
        self.PRIVATE = "PRIVATE"
        self.PUBLIC = "PUBLIC"
        self.SERVER_PUBLIC = """-----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwT+SN3/aCAwyjsAt+Omu
        9pvLZ9tnMqK0NHq99BgODSR8H+Gt6ZmqiTLCWn4EXyF0Bfjqf0lYTA03D3N1Bs2e
        Pv+OvmNIpP9iF53zweArCgEvwIjotGDbFnrKi6zmeu7jt81D8K6X/g3uEsBhdb8/
        MpulVjUhi0w5JZPUsn4IAI1xLqCVF1EV1Z6bldV4E4LieJrE80+Q0IS5W0YMxQNI
        zZscoVa0jSERXVFQzR+KVVGfw+jD5I+lHmsFgQHS4BVEAFg1rHnFPG8RksYH/y9B
        ENGQFzvl7Gc8posBVI8Y/PP0tM8n+d1HyoKwpx4Ohq0YA7qh5ru7DrjbqgHzoRtJ
        9QIDAQAB
        -----END PUBLIC KEY-----"""
        self.options = Options(
            api_url="https://test.fastcoinexchange.com/api/v1/{method}",
            private=self.PRIVATE,
            public=self.PUBLIC,
            server_public=self.SERVER_PUBLIC,
            unique_id="test_unique",
        )


class TestModels(SetupHelper, unittest.TestCase):
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

    def test_invoice_check_without_parameters(self):
        self.assertFalse(models.InvoiceCheck(self.options).is_valid)

    def test_invoice_check_with_wrong_address(self):
        self.assertEqual(
            models.InvoiceCheck(
                self.options,
                address="OOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"
            ).get(),
            '{"address": "should be a valid Bitcoin Address"}')

    def test_invoice_check_with_right_parameters(self):
        self.assertTrue(
            models.InvoiceCheck(
                self.options,
                address="111111111111111111111111111111"
            ).is_valid
        )

    def test_invoice_rate(self):
        self.assertTrue(models.InvoiceRate(self.options).is_valid)

    def test_invoice_sum_with_all_parameters(self):
        self.assertTrue(models.InvoiceSum(
            self.options,
            amount=Decimal(10.3),
            currency=fields.CURRENCY_BTC
        ).is_valid)

    def test_invoice_sum_without_parameters(self):
        self.assertFalse(models.InvoiceSum(self.options).is_valid)

    def test_invoice_sum_with_required_parameters(self):
        self.assertTrue(models.InvoiceSum(
                self.options,
                amount=Decimal(10.3)
            ).is_valid)

    def test_invoice_sum_with_not_decimal_amount(self):
        self.assertEqual(
            models.InvoiceSum(
                self.options,
                amount=10.3,
                currency=fields.CURRENCY_BTC,
            ).get(),
            '{"amount": "should be a Decimal"}')

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


class TestServer(SetupHelper, unittest.TestCase):
    """
    Tests for checking the server connection.
    """

    def test_connection(self):
        response = models.Rate(self.options).get()
        self.assertIn('code', response.keys())
        self.assertEqual(response.get('code'), 0)


class TestValidators(unittest.TestCase):
    """
    Tests for the fastex validators
    """

    error = errors.ValidationError

    @staticmethod
    def validate(validator, value):
        validator.validate(None, value)

    def test_decimal_validator(self):
        validator = fields.DecimalValidator

        with self.assertRaises(self.error):
            self.validate(validator, 10)

        with self.assertRaises(self.error):
            self.validate(validator, "10")

        with self.assertRaises(self.error):
            self.validate(validator, 10.0)

        raised = False
        try:
            self.validate(validator, Decimal(10.0))
        except self.error:
            raised = True
        self.assertFalse(raised)

    def test_bitcoin_address_validator(self):
        validator = fields.BitcoinAddressValidator

        with self.assertRaises(self.error):
            self.validate(validator, "1111")

        with self.assertRaises(self.error):
            self.validate(validator, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

        with self.assertRaises(self.error):
            self.validate(validator, "aaaaaaaaaaaaaaaaaaaaaaaaOaaaaa")

        raised = False
        try:
            self.validate(validator, "1aaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        except self.error:
            raised = True
        self.assertFalse(raised)


class TestData(SetupHelper, unittest.TestCase):

    def test_rate(self):
        expected_data = {}
        self.assertEqual(models.Rate(self.options).make_data(), expected_data)

    def test_balance(self):
        d = models.Balance(
            self.options,
            currency=fields.CURRENCY_BTC
        ).make_data()
        self.assertTrue(self.options.encryption.verify(d['sign'], d['data']))

    def test_exchange(self):
        expected_data = {'amount': Decimal('10'), 'currency_from': 'btc', 'currency_to': 'usd'}
        self.assertEqual(models.Exchange(
            self.options,
            amount=Decimal(10),
            currency_from=fields.CURRENCY_BTC,
            currency_to=fields.CURRENCY_USD
        ).make_data(), expected_data)

    def test_invoice(self):
        expected_data = {'amount': Decimal('10'), 'currency': 'btc'}
        self.assertEqual(models.Invoice(
            self.options,
            amount=Decimal(10),
            currency=fields.CURRENCY_BTC
        ).make_data(), expected_data)

    def test_invoice_check(self):
        expected_data = {'address': '111111111111111111111111111111'}
        self.assertEqual(models.InvoiceCheck(
            self.options,
            address="111111111111111111111111111111"
        ).make_data(), expected_data)

    def test_invoice_rate(self):
        expected_data = {}
        self.assertEqual(models.InvoiceRate(self.options).make_data(), expected_data)

    def test_invoice_sum(self):
        expected_data = {'amount': Decimal('10'), 'currency': 'btc'}
        self.assertEqual(models.InvoiceSum(
            self.options,
            amount=Decimal(10),
            currency=fields.CURRENCY_BTC
        ).make_data(), expected_data)


if __name__ == '__main__':
    unittest.main()
