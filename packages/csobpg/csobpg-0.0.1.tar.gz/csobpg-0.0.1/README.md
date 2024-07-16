# CSOB client
Python library for communicating with ČSOB (<https://platbakartou.csob.cz/>) payment gateway API. The API is described here: <https://github.com/csob/paymentgateway>.

The library currently implements API v.1.9 only.


## Installation
```bash
pip install csobpg
```

## Basic usage
### API client initialization
```python
from csobpg.v19 import APIClient

client = APIClient("merchantId", "merch_private.key", "csob.pub", base_url=..., http_client=...)
```

### HTTP client
The library uses the `HTTPClient` interface for making HTTP requests.

It provides the following HTTP clients:
  * `csobpg.http.urllib_client.UrllibHTTPClient` - the default one using the `urllib` under the hood
  * `csobpg.http.requests_client.RequestsHTTPClient` - an extra HTTP client using the `requests` under the hood. The library must be installed with the `requests-client` extra to be able to use this client

It is also possible to implement the `HTTPClient` interface to use your custom HTTP client.

The HTTP client is set as the following:

```python
from csobpg.v19 import APIClient
from csobpg.http import HTTPClient

class CustomHTTPClient(HTTPClient):
    ...

client = APIClient(..., http_client=CustomHTTPClient(...))
```

### Payment initialization
```python
from csobpg.v19 import Cart, CartItem

response = client.init_payment(
    order_no="2233823251",
    total_amount=100,
    return_url="http://127.0.0.1:5000/",
    cart=Cart([CartItem("Apples", 1, 100)]),
    merchant_data=b"Hello, World!",
)
```

### Get payment URL
```python
url = client.get_payment_process_url(pay_id)
```

### Process the gateway redirect
```python
response = client.process_gateway_return(data_dict)
```

### Get payment status
```python
response = client.get_payment_status(pay_id)
```

### Reverse payment
```python
response = client.reverse_payment(pay_id)
```

### Refund payment
```python
response = client.refund_payment(pay_id, amount=100)
```

### Exceptions handling
```python
from csobpg.v19.errors import APIError, APIClientError
from csobpg.http import HTTPRequestError

try:
    response = client.<operation>(...)
except APIError as exc:
    # handle API error
    # it is raised on any API error. You may also catch the specific API error
except APIClientError as exc:
    # handle API client error
    # it is raised when API returns unexpected response (e.g. invalid JSON, invalid signature)
except HTTPRequestError as exc:
    # handle HTTP error
    # it is raised on any HTTP error
except ValueError as exc:
    # handle value error
    # it is raised on any library's misuse (e.g. passing invalid parameters)
    # it always means developer's mistake
```

### RSA keys management
The simples way to pass RSA keys is to pass their file paths:

```python
from csobpg.v19 import APIClient

client = APIClient(..., "merch_private.key", "csob.pub")
```

The library will read the private key from the file when needed. The public key will be cached into the RAM.

If you want to change it, use special classes:

```python
from csobpg.v19 import APIClient, FileRSAKey, CachedRSAKey

client = APIClient(..., FileRSAKey("merch_private.key"), FileRSAKey("csob.pub"))
```

You may also override the base RSAKey class to define your own key access strategy:

```python
from csobpg.v19 import RSAKey

class MyRSAKey(RSAKey):

    def __str__(self) -> str:
        return "my key"
```
