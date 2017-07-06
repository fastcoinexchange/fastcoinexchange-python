import json
import requests
import time

from booby import Model
from fastex import fields
from fastex.encrypt import Encryption

from fastex.exceptions import UnknownRequestMethod, APIError, UnknownResponseKey


GET, POST = range(2)


class Options(object):

    def __init__(self, api_url, private, public, unique_id, **kwargs):
        self.api_url = api_url
        self.private = private
        self.public = public
        self.unique_id = unique_id
        self.encryption = Encryption("sha1", self.public, self.private)
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def __call__(self, *args, **kwargs):
        stop_keys = ("private", "public", "api_url")
        return {k: v for k, v in self.__dict__.items() if k not in stop_keys}


class Base(Model):
    url, method, query_method = None, None, None
    is_private = False

    def __init__(self, options, **kwargs):
        self.options = options
        self.data = kwargs
        super().__init__(**kwargs)
        self.url = self.options.api_url.format(method=self.method) if self.method else ""

    def request(self, data):
        if self.is_valid:
            if self.query_method is GET:
                response = requests.get(self.url, params=data)
            elif self.query_method is POST:
                response = requests.post(self.url, data=data)
            else:
                raise UnknownRequestMethod(self.query_method)

            r = response.json()
            code = r.get('code')
            if code is not 0:
                raise APIError(code, r.get('return', ''))
            return r
        else:
            return json.dumps(dict(self.validation_errors))

    def get(self, keys=None):
        data = self.data
        req = dict()
        req['nonce'] = int(time.time())
        req.update(data)
        if self.is_private:
            encrypted_data = self.options.encryption.encode(req)
            data = {
                'unique_id': self.options.unique_id,
                'sign': encrypted_data.get('sign'),
                'data': encrypted_data.get('data'),
                'nonce': req['nonce'],
            }

        response = self.request(data)
        if keys:
            values = {}
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