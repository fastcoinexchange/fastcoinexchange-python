from decimal import Decimal as DecimalType

from booby import errors
from booby.fields import *
from booby.validators import nullable, Validator

CURRENCY_BTC, CURRENCY_USD = 'btc', 'usd'
CURRENCY_CHOICES = (CURRENCY_BTC, CURRENCY_USD, )


class DecimalValidator(Validator):
    """This validator forces fields values to be an instance of `Decimal`."""

    @nullable
    def validate(self, value):
        if not isinstance(value, DecimalType):
            raise errors.ValidationError('should be a Decimal')


class Decimal(Field):
    """:class:`Field` subclass with builtin `decimal` validation."""

    def __init__(self, *args, **kwargs):
        super(Decimal, self).__init__(DecimalValidator(), *args, **kwargs)


class Currency(String):
    """:class"`String` subclass"""

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = CURRENCY_CHOICES
        super(Currency, self).__init__(*args, **kwargs)
