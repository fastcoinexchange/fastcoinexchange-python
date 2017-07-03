from fastex import models
from fastex.fields import CURRENCY_BTC
from fastex.models import Options



options = Options(
    api_url="https://fastcoinexchange.com/api/v1/{method}",
    private=PRIVATE,
    public=PUBLIC,
    unique_id="LlaQSA",
    **{
        "sign": "sign",
        "data": "data",
        "nonce": 10,
    })

# rate = models.Rate(options)
# print(rate.get(keys=['tm']))

balance = models.Balance(options, currency=CURRENCY_BTC)
print(balance.get())
