import base64
import urllib
import time

import simplejson as json
import zlib
from urllib.parse import quote, unquote

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from OpenSSL.crypto import verify, sign, load_privatekey, FILETYPE_PEM, load_publickey, X509, Error


class Encryption(object):
    def __init__(self, hash_alg, public, private, server_public):
        self.hash_alg = hash_alg
        self.public = public
        self.private = private
        self.server_public = server_public

    @property
    def nonce(self):
        return int(time.time())

    def encode(self, data):
        if not data or not self.server_public:
            return False

        json_data = json.dumps(data, use_decimal=True)
        data_combined = self.e(json_data.encode(), self.server_public)
        signature = self.data_sign(data_combined, self.private)
        if signature:
            return {
                'sign': signature,
                'data': data_combined,
            }

        return False

    def decode(self, signature, data_combined):
        if not signature or not data_combined or not self.public:
            return False

        if self.data_verify(data_combined, signature, self.server_public):
            data = self.d(data_combined, self.private)
            if not data:
                print("Bad data")
                return False

            return json.loads(data)

        return False

    def verify(self, signature, data_combined):
        return self.data_verify(data_combined, signature, self.public)

    def rc4crypt(self, data, key):
        x = 0
        box = [x for x in range(256)]
        for i in range(256):
            if isinstance(key, bytes):
                x = (x + box[i] + key[i % len(key)]) % 256
            else:
                x = (x + box[i] + ord(key[i % len(key)])) % 256
            box[i], box[x] = box[x], box[i]
        x, y = 0, 0
        out = []
        key_box = box
        for char in data:
            x = (x + 1) % 256
            y = (y + box[x]) % 256
            box[x], box[y] = box[y], box[x]
            out.append(chr(char ^ box[(box[x] + box[y]) % 256]))

        encrypted = ''.join(out)
        return encrypted.encode(), ''.join([str(x) for x in key_box]).encode()

    def e(self, data, key):
        if data:
            data_compressed = zlib.compress(data)
            data_encrypted, encrypted_key = self.rc4crypt(data_compressed, key)
            data_encrypted = base64.b64encode(data_encrypted)
            encrypted_key = base64.b64encode(encrypted_key)
            data_combined = self.combine_string(data_encrypted, encrypted_key)
            return self.data_url_encode(data_combined)
        return False

    def d(self, data_url_ready, key):
        data = False
        if data_url_ready:
            data_combined = self.data_url_decode(data_url_ready)
            data_encrypted, encrypted_key = self.decombine_string(data_combined)
            data_encrypted = base64.b64decode(data_encrypted)
            encrypted_key = base64.b64decode(encrypted_key)

            data_compressed = openssl_open(data_encrypted, encrypted_key, key)
            data = zlib.decompress(data_compressed)
        return data

    def combine_string(self, s1, s2):
        return f"{s1.decode()}-{s2.decode()}"

    def decombine_string(self, data_combined):
        s1, s2 = data_combined.split('-')
        return s1.encode(), s2.encode()

    def data_url_encode(self, s):
        s = s.replace('/', '_')
        s = quote(s)
        return s

    def data_url_decode(self, s):
        s = unquote(s)
        s = s.replace('_', '/')
        return s

    def data_sign(self, data, key):
        # return base64.b64encode(self.openssl_sign(data, key))
        signed = base64.b64encode(sign(
            load_privatekey(FILETYPE_PEM, key),
            data,
            self.hash_alg
        ))
        return self.data_url_encode(signed.decode())

    def openssl_sign(self, data, key):
        rsa_key = RSA.importKey(key, "")
        h = SHA.new(data.encode('utf-8'))
        signer = PKCS1_v1_5.new(rsa_key)
        signature = signer.sign(h)
        return signature

    def data_verify(self, data, signature, key):
        pkey = load_publickey(FILETYPE_PEM, key)
        x509 = X509()
        x509.set_pubkey(pkey)
        sign = base64.b64decode(self.data_url_decode(signature))
        try:
            verify(x509, sign, data, self.hash_alg)
        except Error:
            return False
        else:
            return True
