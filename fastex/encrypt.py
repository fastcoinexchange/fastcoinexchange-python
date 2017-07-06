import base64
import urllib
import time

import simplejson as json
import zlib
from urllib.parse import quote

from OpenSSL.crypto import verify, sign, load_privatekey, FILETYPE_PEM


class Encryption(object):
    def __init__(self, hash_alg, public, private):
        self.hash_alg = hash_alg
        self.public = public
        self.private = private

    @property
    def nonce(self):
        return int(time.time())

    def encode(self, data):
        if not data or not self.public:
            return False

        json_data = json.dumps(data, use_decimal=True)
        data_combined = self.e(json_data.encode(), self.public).replace('b%27', '').replace('%27-', '-')  # need to change!
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

        if self.data_verify(data_combined, signature, self.public) == 1:  # maybe boolean?
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
            x = (x + box[i] + ord(key[i % len(key)])) % 256
            box[i], box[x] = box[x], box[i]
        x, y = 0, 0
        out = []
        for char in data:
            x = (x + 1) % 256
            y = (y + box[x]) % 256
            box[x], box[y] = box[y], box[x]
            out.append(chr(char ^ box[(box[x] + box[y]) % 256]))

        encrypted = ''.join(out)
        return encrypted, ''.join([str(x) for x in box])

    def e(self, data, key):
        if data:
            data_compressed = zlib.compress(data)
            data_encrypted, encrypted_key = self.rc4crypt(data_compressed, self.public)  # openssl_seal should be here
            # encrypted_key = ""  # should be returned via openssl_seal
            data_encoded = base64.b64encode(data_encrypted.encode())
            encrypted_key = base64.b64encode(encrypted_key.encode())
            data_combined = self.combine_string(data_encoded, encrypted_key)
            data_url_ready = self.data_url_encode(data_combined)
        else:
            data_url_ready = False
        return data_url_ready

    # def d(self, data_url_ready, key):
    #     if data_url_ready:
    #         data_combined = self.data_url_decode(data_url_ready)
    #         complex = self.decombine_string(data_combined)
    #         data_encrypted = base64.b64decode(complex[0])
    #         encrypted_key = base64.b64decode(complex[1])
    #         pkey_id = openssl_get_privatekey(key)
    #         if openssl_open(data_encrypted, data_compressed, encrypted_key, pkey_id):
    #             data = zlib.decompress(data_compressed)
    #         else:
    #             data = False
    #     else:
    #         data = False
    #     return data

    def combine_string(self, s1, s2):
        return f"{s1}-{s2}"

    def decombine_string(self, data_combined):
        return data_combined.split('-')

    def data_url_encode(self, s):
        s = s.replace('/', '_')
        s = quote(s)
        return s

    def data_url_decode(self, s):
        s = urllib.urldecode(s)
        s = s.replace('_', '/')
        return s

    def data_sign(self, data, key):
        return sign(
            load_privatekey(FILETYPE_PEM, key, b""),
            data,
            self.hash_alg
        )

    def data_verify(self, data, signature, key):
        a = self.data_url_decode(signature)
        b = base64.b64decode(a)
        c = verify(data, b, key, int(self.hash_alg))
        return c
