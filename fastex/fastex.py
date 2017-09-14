import time
import requests
import base64
import json
import zlib

import OpenSSL.crypto as ct

from urllib.parse import quote, unquote
from Crypto import Random
from Crypto.Cipher import ARC4, PKCS1_v1_5
from Crypto.PublicKey import RSA

from exceptions import FastexAPIError, FastexInvalidDataReceived, FastexBadDataDecoded


OPENSSL_ALGO_SHA512 = 'sha512'
OPENSSL_ALGO_SHA1 = 'sha1'

SERVER_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwT+SN3/aCAwyjsAt+Omu
9pvLZ9tnMqK0NHq99BgODSR8H+Gt6ZmqiTLCWn4EXyF0Bfjqf0lYTA03D3N1Bs2e
Pv+OvmNIpP9iF53zweArCgEvwIjotGDbFnrKi6zmeu7jt81D8K6X/g3uEsBhdb8/
MpulVjUhi0w5JZPUsn4IAI1xLqCVF1EV1Z6bldV4E4LieJrE80+Q0IS5W0YMxQNI
zZscoVa0jSERXVFQzR+KVVGfw+jD5I+lHmsFgQHS4BVEAFg1rHnFPG8RksYH/y9B
ENGQFzvl7Gc8posBVI8Y/PP0tM8n+d1HyoKwpx4Ohq0YA7qh5ru7DrjbqgHzoRtJ
9QIDAQAB
-----END PUBLIC KEY-----"""


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
        return f"{str1.decode()}-{str2.decode()}"

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


class FastexApi(object):
    hash_type = OPENSSL_ALGO_SHA512
    nonce = None
    is_test = True

    def __init__(self, fastex_id, public, private, server_key, is_test=True):
        s = open(public, "r").read()
        self.public = s  # RSA.importKey(s)
        s = open(private).read()
        self.private = s  # RSA.importKey(s)
        self.server_key = server_key
        self.is_test = is_test
        self.unique_id = fastex_id

    @property
    def url(self):
        if self.is_test:
            return "https://test.fastcoinexchange.com/api/v1/{}"
        return "https://fastcoinexchange.com/api/v1/{}"

    def __query_private(self, method, params=None, detail=False):
        if self.nonce:
            self.nonce += 1
        else:
            self.nonce = int(time.time())

        req = {}
        req.update({'nonce': self.nonce, 'currency': ''})
        req.update(params or {})

        encryption = Encryption(self.server_key, self.private, self.hash_type)
        sign, data = encryption.encode(req)

        response = requests.post(
            self.url.format(method),
            data={
                'unique_id': self.unique_id,
                'sign': sign,
                'data': data,
                'nonce': self.nonce
            }
        )
        r = json.loads(response.text)

        if not all(['return' in r, 'sign' in r, 'code'in r]):
            raise FastexInvalidDataReceived

        decrypted_data = encryption.decode(r['sign'], r['return'])

        if r['code'] != 0:
            raise FastexAPIError(r['code'], decrypted_data.get('message') or decrypted_data['return']['message'])

        if detail:
            r['data'] = decrypted_data
            return r
        return decrypted_data['data']

    def __query_public(self, method, params=None, detail=False):
        response = requests.get(self.url.format(method), params=params)
        r = json.loads(response.text)
        if not r.get('code'):
            raise FastexInvalidDataReceived

        if r['code'] != 0:
            raise FastexAPIError(r['code'], r.get('message'))

        if detail:
            return r
        return r['data']

    # ## METHODS ###

    def rate(self, *args, **kwargs):
        return self.__query_public('rate', *args, **kwargs)

    def balance(self, currency=None, *args, **kwargs):
        params = {}
        if currency:
            params = {'currency': currency}
        return self.__query_private('balance', params=params, *args, **kwargs)

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

    def invoice(self, amount, currency=None, *args, **kwargs):
        params = {
            'amount': amount,
        }
        if currency:
            params = {'currency': currency}
        return self.__query_private('invoice', params=params, *args, **kwargs)

    def invoicecheck(self, address, *args, **kwargs):
        params = {
            'address': address,
        }
        return self.__query_private('invoicecheck', params=params, *args, **kwargs)

    def invoicerate(self, *args, **kwargs):
        params = {}
        return self.__query_private('invoicerate', params=params, *args, **kwargs)

    def invoicesum(self, *args, **kwargs):
        params = {}
        return self.__query_private('invoicesum', params=params, *args, **kwargs)


# USAGE

api = FastexApi("xddlcQ", "../publickey.pem", "../privatekey.pem", SERVER_KEY)

try:
    rate = api.rate()
except FastexAPIError as e:
    print(e)
else:
    print("Rate", rate)

print("Balance: ", api.balance(currency='USD'))
