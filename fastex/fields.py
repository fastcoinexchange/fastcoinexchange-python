from booby import errors
from booby.fields import *
from booby.validators import nullable


class DecimalValidator(object):
    """This validator forces fields values to be an instance of `Decimal`."""

    @nullable
    def validate(self, value):
        if not isinstance(value, Decimal):
            raise errors.ValidationError('should be a Decimal')


class Decimal(Field):
    """:class:`Field` subclass with builtin `decimal` validation."""

    def __init__(self, *args, **kwargs):
        super(Decimal, self).__init__(DecimalValidator(), *args, **kwargs)
