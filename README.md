# fastcoinexchange-python
Python library for the fastcoinexchange API

This is a simple wrapper for the FastCoinExchange API, which makes you able to use API with your Python code.

## Installation
`pip install fastcoinexchange_python` - in your environment.

Then you should import some gears to make this mechanism works.

```python
from fastex import models
from fastex import fields
from fastex.base_models import Options
```

## How to use?

### Options

If you want to have an access to the private methods, then tou have to save your parameters into `Options` instance:

```python
options = Options(
    api_url="https://fastcoinexchange.com/api/v1/{method}",
    private=PRIVATE,  # your private key
    public=PUBLIC,  # server's public key
    unique_id="your_unique",  # your unique id
)
```

### Request API

Let's assume that we want to get the current rate of the bitcoin.
Following code does that:

```python
rate = models.Rate(options)
rate.get()

# {'code': 0, 'data': {'tm': '1499418523', 'ask': 252656799000, 'bid': 249463614000}}
```
This is a `dict` object, so you don't have to worry about the conversion.

### Response filtering

If you need one field only, e.g. `bid`, you could use the `keys` argument like following:
```python
rate.get(keys=['bid'])

# {'tm': '1499422855'}
```

## Models
* Rate
* Balance
* Exchange
* Invoice
* InvoiceCheck
* InvoiceRate
* InvoiceSum

this list might be extended
