# fastcoinexchange-python
Python library for the fastcoinexchange API

This is a simple wrapper for the FastCoinExchange API, which makes you able to use API with your Python code.

## Installation
`pip install fastcoinexchange` - in your environment.

## How to use?

### Options

If you want to have an access to the private methods, then tou have to save your private and public keys into pem files. 
You can get its in the FastCoinExchange administrative interface. Be careful, you can get them once only. 
Also you need to save the server's public key.

```python
from fastex import Api

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

* FastexAPIError - it raised if API server returned an error message
* FastexInvalidDataReceived - it raised if was got an invalid data from the API server
* FastexBadDataDecoded - it raised if error occurred while response decoding

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

## Methods
* Rate
* Balance
* Exchange
* Invoice
* InvoiceCheck
* InvoiceRate
* InvoiceSum

this list might be extended

The detail specialization you can find [here](https://test.fastcoinexchange.com/#api).
