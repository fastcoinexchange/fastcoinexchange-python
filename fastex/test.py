import time

from fastex import models
from fastex.encrypt import Encryption
from fastex.fields import CURRENCY_BTC, CURRENCY_USD
from fastex.base_models import Options

PRIVATE = """-----BEGIN PRIVATE KEY-----
-----END PRIVATE KEY-----"""

PUBLIC = """-----BEGIN PUBLIC KEY-----
-----END PUBLIC KEY-----"""

options = Options(
    api_url="https://fastcoinexchange.com/api/v1/{method}",
    private=PRIVATE,
    public=PUBLIC,
    unique_id="LlaQSA",
)

rate = models.Rate(options)
print(rate.get({}, keys=['tm']))

# encryption = Encryption("sha512", PUBLIC, PRIVATE)
#
# data = {
#     'currency': CURRENCY_BTC,
#     'unique_id': "LlaQSA",
# }
#
# balance = models.Balance(options, currency=CURRENCY_BTC)
# response = balance.get(data)
#
# print(response)
