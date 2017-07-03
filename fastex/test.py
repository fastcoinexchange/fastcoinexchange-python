from fastex import models
from fastex.models import CURRENCY_BTC

options = {
    "unique_id": 100,
    "sign": "sign",
    "data": "data",
    "nonce": 10,
}
print(CURRENCY_BTC)

rate = models.Rate()
print(rate.get())

balance = models.Balance(currency=CURRENCY_BTC, **options)
print(balance.get())
