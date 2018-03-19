import time
import warnings

import requests
import base64
import json
import zlib

import OpenSSL.crypto as ct

from Crypto import Random
from Crypto.Cipher import ARC4, PKCS1_v1_5
from Crypto.PublicKey import RSA
from decimal import Decimal

try:
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote, unquote

from .exceptions import FastexAPIError, FastexInvalidDataReceived, FastexBadDataDecoded, AccountDisabled, \
    FastexPrivateRequestsDisabled

OPENSSL_ALGO_SHA512 = 'sha512'
OPENSSL_ALGO_SHA1 = 'sha1'

USD, BTC = "USD", "BTC"


def normalize(request_keys=None, response_keys=None):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            kwargs = Api.dict_to_normalized(self, kwargs, Api.NTO, keys=request_keys)
            return Api.dict_to_normalized(self, func(self, *args, **kwargs), Api.TON, keys=response_keys)
        return wrapper
    return decorator


class Encryption(object):
    def __init__(self, remote_public_key, own_private_key, hash_alg=OPENSSL_ALGO_SHA1):
        self.hash_alg = hash_alg
        if remote_public_key and own_private_key:
            self.remote_public_key = remote_public_key
            self.own_private_key = own_private_key

    @staticmethod
    def __openssl_seal(data, key, encode_alg=None):
        public_key = RSA.importKey(key)
        random_key = Random.new().read(16)
        cipher = PKCS1_v1_5.new(public_key)
        encrypted_key = cipher.encrypt(random_key)
        cipher = ARC4.new(random_key)
        encrypted_data = cipher.encrypt(data)
        if encode_alg:
            return encode_alg(encrypted_data), encode_alg(encrypted_key)
        return encrypted_data, encrypted_key

    @staticmethod
    def __openssl_open(data, key, pkey_id):
        cipher = PKCS1_v1_5.new(RSA.importKey(pkey_id))
        key = cipher.decrypt(key, False)
        return ARC4.new(key=key).decrypt(data)

    @staticmethod
    def __combine_strings(str1, str2):
        return "{}-{}".format(str1.decode(), str2.decode())

    @staticmethod
    def __decombine_strings(data_combined):
        return data_combined.split('-')

    @staticmethod
    def __data_url_encode(s):
        return quote(s.replace('/', '_'))

    @staticmethod
    def __data_url_decode(s):
        return unquote(s).replace('_', '/')

    def __data_sign(self, data, key):
        pkey = ct.load_privatekey(ct.FILETYPE_PEM, key)
        signature = ct.sign(pkey, data, self.hash_alg)
        return self.__data_url_encode(base64.b64encode(signature).decode())

    # ## PUBLIC METHODS

    def encode(self, data):
        if not data or not self.remote_public_key:
            return False

        encrypted_data, encrypted_key = self.__openssl_seal(
            zlib.compress(json.dumps(data, separators=(',', ':')).encode()),
            self.remote_public_key, encode_alg=base64.b64encode
        )
        data_combined = self.__combine_strings(encrypted_data, encrypted_key)
        data_url_ready = self.__data_url_encode(data_combined)
        signature = self.__data_sign(
            data_url_ready,
            self.own_private_key
        )
        return signature, data_url_ready

    def decode(self, signature, data_combined):
        if not signature or not data_combined or not self.remote_public_key:
            return False

        data_combined = self.__data_url_decode(data_combined)
        data_encrypted, encrypted_key = self.__decombine_strings(data_combined)
        data_encrypted = base64.b64decode(data_encrypted)
        encrypted_key = base64.b64decode(encrypted_key)
        data_compressed = self.__openssl_open(data_encrypted, encrypted_key, self.own_private_key)
        data = zlib.decompress(data_compressed).decode()

        if not data:
            raise FastexBadDataDecoded
        return json.loads(data)


class Api(object):
    hash_type = OPENSSL_ALGO_SHA512
    is_test = True
    multiplier = Decimal(10 ** 8)
    divider = Decimal(10 ** -8)
    public = None
    private = None

    TON, NTO = 0, 1

    def __init__(self, fastex_id=None, public=None, public_file=None, private=None, private_file=None, server_key=None,
                 is_test=True, money_type=Decimal, precision=8):
        if public:
            self.public = public
        if private:
            self.private = private
        if not public and public_file:
            s = open(public_file, "r").read()
            self.public = s  # RSA.importKey(s)
        if not private and private_file:
            s = open(private_file).read()
            self.private = s  # RSA.importKey(s)

        self.server_key = server_key
        self.is_test = is_test
        self.unique_id = fastex_id
        self.money_type = money_type
        self.precision = f".{''.join(['0' for x in range(precision-1)])}1"

        if not self.private or not self.public or not self.server_key:
            warnings.warn("Fastex: Public requests only", Warning)

    @property
    def url(self):
        if self.is_test:
            return "https://test.fastcoinexchange.com/api/v1/{}"
        return "https://fastcoinexchange.com/api/v1/{}"

    def __query_private(self, method, params=None, detail=False):
        if not all([self.public, self.private, self.server_key, self.unique_id]):
            raise FastexPrivateRequestsDisabled()

        nonce = int(time.time())

        req = {}
        req.update({'nonce': nonce, 'currency': ''})
        req.update(params or {})

        encryption = Encryption(self.server_key, self.private, self.hash_type)
        sign, data = encryption.encode(req)

        response = requests.post(
            self.url.format(method),
            data={
                'unique_id': self.unique_id,
                'sign': sign,
                'data': data,
                'nonce': nonce
            }
        )
        r = json.loads(response.text)

        if 'code' in r and r['code'] == -2:
            raise AccountDisabled

        if not all(['return' in r, 'sign' in r, 'code' in r]):
            raise FastexInvalidDataReceived(r)

        decrypted_data = encryption.decode(r['sign'], r['return'])

        if r['code'] != 0:
            raise FastexAPIError(r['code'],
                                 decrypted_data.get('message')
                                 or decrypted_data.get('errors')
                                 or decrypted_data['return']['message'])

        if detail:
            r['data'] = decrypted_data
            return r
        return decrypted_data['data'] if 'data' in decrypted_data else decrypted_data

    def __query_public(self, method, params=None, detail=False):
        response = requests.get(self.url.format(method), params=params)
        r = json.loads(response.text)
        if not 'code' in r:
            raise FastexInvalidDataReceived

        if r['code'] != 0:
            raise FastexAPIError(r['code'], r.get('message'))

        if detail:
            return r
        return r['data']

    def __to_normalized(self, value):
        return self.money_type(
            (Decimal(value) * self.divider).quantize(Decimal(self.precision)) or 0)

    def __normalized_to(self, value):
        return self.money_type(
            (Decimal(value) * self.multiplier).quantize(Decimal(self.precision)) or 0)

    def dict_to_normalized(self, d, normalizer, keys=None):
        if not keys:
            keys = []
        if normalizer == self.TON:
            nf = self.__to_normalized
        elif normalizer == self.NTO:
            nf = self.__normalized_to
        return dict(map(lambda x: (x[0], nf(x[1]) if x[0] in keys else x[1]), d.items()))

    # ## METHODS ###

    @normalize(response_keys=['bid', 'ask'])
    def rate(self, *args, **kwargs):
        return self.__query_public('rate', *args, **kwargs)

    @normalize(response_keys=['usd', 'btc'])
    def balance(self, currency=None, *args, **kwargs):
        params = {}
        if currency:
            params = {'currency': currency}
        return self.__query_private('balance', params=params, *args, **kwargs)

    @normalize(request_keys=['amount'], response_keys=['rate', 'from_amount', 'to_amount'])
    def exchange(self, amount, currency_from, currency_to, rate_ask=None, rate_bid=None, *args, **kwargs):
        params = {
            'amount': amount,
            'currency_from': currency_from,
            'currency_to': currency_to,
        }
        if rate_ask:
            params.update({'rate_ask': rate_ask})
        if rate_bid:
            params.update({'rate_bid': rate_bid})
        return self.__query_private('exchange', params=params, *args, **kwargs)

    @normalize(request_keys=['amount'], response_keys=['btc_due'])
    def invoice(self, amount, currency=None, *args, **kwargs):
        params = {
            'amount': amount,
        }
        if currency:
            params = {'currency': currency}
        return self.__query_private('invoice', params=params, *args, **kwargs)

    @normalize(response_keys=['btc_due', 'amount_due', 'btc_paid', 'amount_paid'])
    def invoicecheck(self, address, *args, **kwargs):
        params = {
            'address': address,
        }
        return self.__query_private('invoicecheck', params=params, *args, **kwargs)

    @normalize(response_keys=['bid'])
    def invoicerate(self, *args, **kwargs):
        params = {}
        return self.__query_private('invoicerate', params=params, *args, **kwargs)

    @normalize(request_keys=['amount'], response_keys=['btc_due'])
    def invoicesum(self, *args, **kwargs):
        params = {}
        return self.__query_private('invoicesum', params=params, *args, **kwargs)

    @normalize(request_keys=['amount'])
    def send_btc(self, address, amount, *args, **kwargs):
        params = {
            'output_data': [
                {
                    'address': address,
                    'amount': amount,
                }
            ]
        }
        return self.__query_private('send/btc/simple', params=params, *args, **kwargs)

    def get_new_address(self, is_autoexchange=0, *args, **kwargs):
        params = {
            'is_autoexchange': is_autoexchange,
        }
        return self.__query_private('address/get/new', params=params, *args, **kwargs)

    @normalize(request_keys=['amount'], response_keys=['amount', 'cost'])
    def create_wex_coupon(self, amount, *args, **kwargs):
        params = {
            'amount': amount,
        }
        return self.__query_private('withdraw/wexcoupon/usd', params=params, *args, **kwargs)

    @normalize(request_keys=['amount'], response_keys=['amount', 'cost'])
    def wex_coupon_cost(self, amount, *args, **kwargs):
        params = {
            'amount': amount,
        }
        return self.__query_private('wex/usd/cost', params=params, *args, **kwargs)
