from fastex import fields
from fastex.base_models import PublicRequest, PrivateRequest, GET, POST, Base


class Rate(Base):
    method = "rate"
    query_method = GET


class Balance(Base):
    method = "balance"
    query_method = POST
    is_private = False

    currency = fields.Currency()


class Exchange(Base):
    method = "exchange"
    query_method = POST
    is_private = False

    amount = fields.Decimal(required=True)
    currency_from = fields.Currency(required=True)
    currency_to = fields.Currency(required=True)
    rate_ask = fields.Decimal(required=False)
    rate_bid = fields.Decimal(required=False)


class Invoice(Base):
    method = "invoice"
    query_method = POST
    is_private = False

    amount = fields.Decimal(required=True)
    currency = fields.Currency(default=fields.CURRENCY_USD)
