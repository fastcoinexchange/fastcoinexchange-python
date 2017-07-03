import json
import requests

from booby import Model

from fastex import fields
from fastex.exceptions import UnknownRequestMethod, APIError, UnknownResponseKey

GET, POST = range(2)

# === BASE MODELS ===========


class Options(object):

    def __init__(self, api_url, private, public, unique_id, **kwargs):
        self.api_url = api_url
        self.private = private
        self.public = public
        self.unique_id = unique_id
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def __call__(self, *args, **kwargs):
        stop_keys = ("private", "public", "api_url")
        return {k: v for k, v in self.__dict__.items() if k not in stop_keys}


class Base(Model):
    url, method, query_method = None, None, None

    def __init__(self, options,  *args, **kwargs):
        opt_values = options()
        opt_values.update(kwargs)
        super().__init__(**opt_values)
        self.url = options.api_url.format(method=self.method) if self.method else ""

    def request(self, is_json=True, **kwargs):
        if self.is_valid:
            if self.query_method is GET:
                response = requests.get(self.url, params=kwargs)
            elif self.query_method is POST:
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

    def get(self, is_json=True, keys=None):
        response = self.request(is_json=is_json)
        if keys:
            values = {}
            if not is_json:
                response = response.json()
            for key in keys:
                try:
                    values[key] = response['data'][key]
                except KeyError:
                    raise UnknownResponseKey(key)
            return values
        return response


class PublicRequest(Base):
    unique_id = fields.String()
    sign = fields.String()
    data = fields.String()
    nonce = fields.Integer()


class PrivateRequest(Base):
    unique_id = fields.String(required=True)
    sign = fields.String(required=True)
    data = fields.String(required=True)
    nonce = fields.Integer(required=True)

# === METHOD MODELS ===========


class Rate(PublicRequest):
    method = "rate"
    query_method = GET


class Balance(PrivateRequest):
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
