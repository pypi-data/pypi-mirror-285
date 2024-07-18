# HsTrader SDK for Python

![PyPI - Version](https://img.shields.io/pypi/v/hstrader)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hstrader)
[![Documentation](https://img.shields.io/badge/docs-latest-blue)](https://staging.hstrader.com/trader/docs/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


hstrader-sdk-py is the [HsTrader](https://hstrader.com) SDK for Python.

The HsTrader SDK requires a minimum version of Python 3.7.

## Installation

```bash
pip install hstrader
```

## Documentation

[https://hstrader.com/trader/docs](https://staging.hstrader.com/trader/docs/)

## Getting Started

### Http Example

```python
from hstrader import HsTrader


# Its recommended to use environment variables to store your credentials
CLIENT_ID = "<YOUR_CLIENT_ID>"
SECRET = "<YOUR_SECRET>"


# Create a new instance of HSTrader
client = HsTrader(CLIENT_ID, SECRET)

try:

    # Get the EURUSD symbol
    eurusd = client.get_symbol("EURUSD")
    print(
        f"Symbol ID: {eurusd.id}, Name: {eurusd.symbol}, Last Bid: {eurusd.last_bid}, Last Ask: {eurusd.last_ask}"
    )

except Exception as e:
    print(e)


```

### Websocket Example

```python
from hstrader import HsTrader
from hstrader.models import Event, Tick


# Its recommended to use environment variables to store your credentials
CLIENT_ID = "<YOUR_CLIENT_ID>"
SECRET = "<YOUR_SECRET>"


# Create a new instance of HSTrader
client = HsTrader(CLIENT_ID, SECRET)


# Create a callback function to handle connection events
@client.subscribe(Event.CONNECT)
def on_connect(): # this function will be called when the client is connected to the server
    print("Connected")
    # Subscribe to market feed updates
    client.start_market_feed()
    


# Create a callback function to handle market updates
@client.subscribe(Event.MARKET)
def on_market(tick: Tick):  # this function will be called whenever a new market update is received
    print(
        f"Received tick for symbol {tick.symbol_id}: bid = {tick.bid} ask = {tick.ask}"
    )


# Start listening to real-time data
client.start()


```

For more examples, please refer to the [examples](/examples/) directory.
## Contributing

Contributions are welcome.<br/>
If you've found a bug within this project, please open an issue to discuss what you would like to change.<br/>
If it's an issue with the API, please open a topic at [Contact Us]().
