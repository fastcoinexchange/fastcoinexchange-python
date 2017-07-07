import re
from decimal import Decimal as DecimalType

from booby import errors
from booby.fields import *
from booby.validators import nullable, Validator

CURRENCY_BTC, CURRENCY_USD = 'btc', 'usd'
CURRENCY_CHOICES = (CURRENCY_BTC, CURRENCY_USD, )


# Validators

class DecimalValidator(Validator):
    """This validator forces fields values to be an instance of `Decimal`."""

    @nullable
    def validate(self, value):
        if not isinstance(value, DecimalType):
            raise errors.ValidationError('should be a Decimal')


class BitcoinAddressValidator(Validator):
    """This validator forces fields values to be an valid Bitcoin Address."""

    @nullable
    def validate(self, value):
        if not bool(re.match("^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", value)):
            raise errors.ValidationError('should be a valid Bitcoin Address')


# Fields

class Decimal(Field):
    """:class:`Field` subclass with builtin `decimal` validation."""

    def __init__(self, *args, **kwargs):
        super(Decimal, self).__init__(DecimalValidator(), *args, **kwargs)


class Currency(String):
    """:class"`String` subclass"""

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = CURRENCY_CHOICES
        super(Currency, self).__init__(*args, **kwargs)


class BitcoinAddress(String):
    """:class"`String` subclass"""

    def __init__(self, *args, **kwargs):
        super(BitcoinAddress, self).__init__(BitcoinAddressValidator(), *args, **kwargs)
