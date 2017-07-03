import json
import requests

from booby import Model

from fastex import fields
from fastex.exceptions import UnknownRequestMethod, APIError


CURRENCY_BTC, CURRENCY_USD = 'btc', 'usd'
CURRENCY_CHOICES = (CURRENCY_BTC, CURRENCY_USD, )


class Base(Model):
    GET, POST = "get", "post"
    url, method, query_method = None, None, None
    url_pattern = "https://fastcoinexchange.com/api/v1/{method}"

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.url = self.url_pattern.format(method=self.method) if self.method else ""

    def request(self, is_json=True, **kwargs):
        if self.is_valid:
            if self.query_method is self.GET:
                response = requests.get(self.url, params=kwargs)
            elif self.query_method is self.POST:
                response = requests.post(self.url, data=kwargs)
            else:
                raise UnknownRequestMethod(self.query_method)
            if is_json:
                r = response.json()
                code = r.get('code')
                msg = r.get('message', '')
                if code is not 0:
                    raise APIError(code, msg)
                return r
            return response
        else:
            return json.dumps(dict(self.validation_errors))

    def get(self, is_json=True, **kwargs):
        return self.request(is_json=is_json, **kwargs)


class PublicRequest(Base):
    unique_id = fields.Integer()
    sign = fields.String()
    data = fields.String()
    nonce = fields.Integer()


class PrivateRequest(Base):
    unique_id = fields.Integer(required=True)
    sign = fields.String(required=True)
    data = fields.String(required=True)
    nonce = fields.Integer(required=True)


class Rate(PublicRequest):
    method = "rate"
    query_method = "get"


class Balance(PrivateRequest):
    method = "balance"
    query_method = "post"

    currency = fields.String(choices=CURRENCY_CHOICES, required=False)


class Exchange(PrivateRequest):
    method = "exchange"
    query_method = "post"

    amount = fields.Decimal(required=True)
    currency_from = fields.String(choices=CURRENCY_CHOICES, required=True)
    currency_to = fields.String(choices=CURRENCY_CHOICES, required=True)
    rate_ask = fields.Decimal(required=False)
    rate_bid = fields.Decimal(required=False)
