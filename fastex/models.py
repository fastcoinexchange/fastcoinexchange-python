from fastex import fields
from fastex.base_models import PublicRequest, PrivateRequest, GET, POST, Base


class Rate(PublicRequest):
    method = "rate"
    query_method = GET


class Balance(Base):
    method = "balance"
    query_method = POST

    currency = fields.Currency()


class Exchange(PrivateRequest):
    method = "exchange"
    query_method = POST

    amount = fields.Decimal(required=True)
    currency_from = fields.Currency(required=True)
    currency_to = fields.Currency(required=True)
    rate_ask = fields.Decimal(required=False)
    rate_bid = fields.Decimal(required=False)


class Invoice(PrivateRequest):
    method = "invoice"
    query_method = POST

    amount = fields.Decimal(required=True)
    currency = fields.Currency()
