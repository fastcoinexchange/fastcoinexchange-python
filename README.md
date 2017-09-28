# fastcoinexchange-python
Python library for the fastcoinexchange API

This is a simple wrapper for the FastCoinExchange API, which makes you able to use API with your Python code.

## Installation
`pip install fastcoinexchange` - in your environment.

## How to use?

### Options

If you need public requests only, it's not necessarily to have any keys and fastex unique_id. 
Just make an `Api` objects.

```python
from fastex.api import Api

api = Api()
```

Notice: you will get a warning message `Fastex: Public requests only`.
If you'll try to call any private method, you'll get the following exception:

```
FastexPrivateRequestsDisabled: It`s impossible to make a private request without a fastex id, a public key, a private key or a server key definition.
```

If you want to have an access to the private methods, then you have to save your private and public keys into pem files. 
You can get its in the FastCoinExchange administrative interface. Be careful, you can get them once only. 
Also you need to save the server's public key.

```python
from fastex.api import Api

SERVER_KEY = """-----BEGIN PUBLIC KEY-----
...
-----END PUBLIC KEY-----"""

api = Api("<unique_id>", "<path_to_your_public_key.pem>", "<path_to_your_private_key.pem>", SERVER_KEY)
```

### Request API

Let's assume that we want to get the current rate of the Bitcoin.
Following code does that:

```python
api.rate()

# {'tm': '1499418523', 'ask': 252656799000, 'bid': 249463614000}
```
This is a `dict` object, so you don't have to worry about the serialization.

### Exceptions

* FastexAPIError - it raises if API server returned an error message
* FastexInvalidDataReceived - it raises if was got an invalid data from the API server
* FastexBadDataDecoded - it raises if error occurred while response decoding
* FastexPrivateRequestsDisabled - it raises if you have no defined private and public keys, server public key or your uniqu_id

For example:

```python
try:
    rate = api.balance(currency='LTC')
except FastexAPIError as e:
    print(e)
else:
    print("Rate", rate)
    
# FastCoinExchange APIError "Incorrect currency" (code: -55)
```

### Constants

You can use the following constants to avoid confusion, e.g. in currency names.

```python
from fastex.api import USD, BTC

api.exchange(amount=0.0001, currency_from=BTC, currency_to=USD)
```

## Methods
* Rate
* Balance
* Exchange
* Invoice
* InvoiceCheck
* InvoiceRate
* InvoiceSum

this list might be extended

The detail specification you can find [here](https://test.fastcoinexchange.com/#api).
