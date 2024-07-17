# SmsAero async API client

[![PyPI version](https://badge.fury.io/py/smsaero-api-async.svg)](https://badge.fury.io/py/smsaero-api-async)
[![Python Versions](https://img.shields.io/pypi/pyversions/smsaero-api-async.svg)](https://pypi.org/project/smsaero-api-async/)
[![Downloads](https://pepy.tech/badge/smsaero-api-async)](https://pepy.tech/project/smsaero-api-async)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](MIT-LICENSE)

## Installation (from PyPI):

```bash
pip install -U smsaero-api-async
```

## Usage example:

Get credentials from account settings page: https://smsaero.ru/cabinet/settings/apikey/

```python
import pprint
import asyncio
import smsaero


SMSAERO_EMAIL = 'your email'
SMSAERO_API_KEY = 'your api key'


async def send_sms(phone: int, message: str) -> None:
    """
    Sends an SMS message

    Parameters:
    phone (int): The phone number to which the SMS message will be sent.
    message (str): The content of the SMS message to be sent.
    """
    api = smsaero.SmsAero(SMSAERO_EMAIL, SMSAERO_API_KEY)
    try:
        result = await api.send_sms(phone, message)
        pprint.pprint(result)
    finally:
        await api.close_session()


if __name__ == '__main__':
    asyncio.run(send_sms(70000000000, 'Hello, World!'))
```

#### Exceptions:

* `SmsAeroException` - base exception class for all exceptions raised by the library.
* `SmsAeroConnectionException` - exception raised when there is a connection error.
* `SmsAeroNoMoneyException` - exception raised when there is not enough money in the account.


## Command line usage:

```bash
SMSAERO_EMAIL="your email"
SMSAERO_API_KEY="your api key"

smsaero_send --email "$SMSAERO_EMAIL" --api_key "$SMSAERO_API_KEY" --phone 70000000000 --message 'Hello, World!'
```

## Run on Docker:

```bash
docker pull 'smsaero/smsaero_python_async:latest'
docker run -it --rm 'smsaero/smsaero_python_async:latest' smsaero_send --email "your email" --api_key "your api key" --phone 70000000000 --message 'Hello, World!'
```

## Compatibility:

* Currently version of library is compatible with Python 3.6+.


## License:

```
MIT License
```
