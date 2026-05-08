# binance-skill.md
# python-binance Library — Futures Testnet Reference

> Use this file as a cheat sheet when writing any code that touches the Binance Futures Testnet via the `python-binance` library. Read it before writing any client, order, or exception-handling code.

---

## Installation

```bash
pip install python-binance python-dotenv typer
```

---

## Client Initialisation (Futures Testnet)

```python
from binance.client import Client

# CORRECT way to target Futures Testnet
client = Client(
    api_key=API_KEY,
    api_secret=API_SECRET,
    testnet=True  # points to https://testnet.binancefuture.com
)
```

> ⚠️ `testnet=True` is required. Without it, the client hits the live endpoint and your testnet keys will return `APIError(code=-2015): Invalid API-key`.

---

## Placing Orders

### Market Order
```python
order = client.futures_create_order(
    symbol='BTCUSDT',   # string, e.g. 'BTCUSDT', 'ETHUSDT'
    side='BUY',         # 'BUY' or 'SELL'
    type='MARKET',
    quantity=0.01       # float, in base asset units
)
```

### Limit Order
```python
order = client.futures_create_order(
    symbol='BTCUSDT',
    side='SELL',
    type='LIMIT',
    timeInForce='GTC',  # required for LIMIT: 'GTC', 'IOC', 'FOK'
    quantity=0.01,
    price=50000.0       # required for LIMIT orders
)
```

### Stop-Limit Order (Bonus)
```python
order = client.futures_create_order(
    symbol='BTCUSDT',
    side='SELL',
    type='STOP',
    timeInForce='GTC',
    quantity=0.01,
    price=49000.0,      # limit price
    stopPrice=49500.0   # trigger price
)
```

---

## Order Response Fields

```python
{
    "orderId": 123456789,
    "symbol": "BTCUSDT",
    "status": "FILLED",          # NEW, PARTIALLY_FILLED, FILLED, CANCELED, REJECTED
    "side": "BUY",
    "type": "MARKET",
    "origQty": "0.01",
    "executedQty": "0.01",
    "avgPrice": "43210.50",      # available after fill
    "price": "0",                # 0 for market orders
    "timeInForce": "GTC",
    "updateTime": 1713700000000
}
```

---

## Exception Handling

```python
from binance.exceptions import BinanceAPIException, BinanceRequestException

try:
    order = client.futures_create_order(...)
except BinanceAPIException as e:
    # API returned an error code (4xx from Binance)
    # e.code  -> Binance error code, e.g. -2015, -1121, -4131
    # e.message -> human-readable message
    logger.error(f"API error {e.code}: {e.message}")
except BinanceRequestException as e:
    # Network-level failure (timeout, connection refused)
    logger.error(f"Network error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

### Common Binance Error Codes
| Code | Meaning | Fix |
|------|---------|-----|
| `-2015` | Invalid API key | Confirm `testnet=True`, use testnet keys |
| `-1121` | Invalid symbol | Check symbol string e.g. `BTCUSDT` not `BTC-USDT` |
| `-1102` | Missing parameter | `LIMIT` orders need `price` and `timeInForce` |
| `-4131` | PERCENT_PRICE filter | Limit price too far from market price |
| `-1111` | Precision too high | Reduce decimal places on quantity/price |

---

## Useful Utility Methods

```python
# Get current futures account balance
client.futures_account_balance()

# Get symbol price ticker
client.futures_symbol_ticker(symbol='BTCUSDT')

# Get symbol info (filters, precision rules)
client.futures_exchange_info()

# Get open orders
client.futures_get_open_orders(symbol='BTCUSDT')

# Cancel an order
client.futures_cancel_order(symbol='BTCUSDT', orderId=123456789)
```

---

## Known Gotchas

1. **`testnet=True` is mandatory** — testnet API keys do NOT work against the live endpoint.
2. **`timeInForce='GTC'`** is required for all LIMIT and STOP orders or you get a missing-parameter error.
3. **Quantity precision matters** — BTCUSDT allows 3 decimal places max. Use `round(qty, 3)`.
4. **Price precision** — BTCUSDT prices must be in increments of `0.10`. Validate before sending.
5. **Testnet resets periodically** — account balances and orders are wiped. Regenerate API keys if you get auth errors.
6. **`avgPrice` is a string `"0"` on LIMIT orders that haven't filled yet** — handle this in your output formatter.

---

## .env Setup

```
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
```

---

## Logging API Requests (for log file deliverable)

```python
import logging

# Log outgoing order params before placing
logger.info(f"Placing order | symbol={symbol} side={side} type={order_type} qty={quantity} price={price}")

# Log the response
logger.info(f"Order response | id={order['orderId']} status={order['status']} execQty={order['executedQty']} avgPrice={order['avgPrice']}")
```
