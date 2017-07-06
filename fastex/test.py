from decimal import Decimal

from fastex import models
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

# rate = models.Rate(options)
# print(rate.get(keys=['tm']))

# balance = models.Balance(options, **{
#     'currency': CURRENCY_BTC,
# })
# print(balance.get())

exchange = models.Exchange(options, **{
    'amount': Decimal(10),
    'currency_from': CURRENCY_USD,
    'currency_to': CURRENCY_BTC,
})
exchange.get()
