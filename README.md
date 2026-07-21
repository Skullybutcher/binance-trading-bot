# Binance Futures Testnet Trading Bot

## Overview
This is a Python project for placing Binance USDT-M Futures orders on the Binance Futures Testnet. It includes both a CLI and a Streamlit UI, and supports MARKET, LIMIT, and STOP-LIMIT style order placement.

## Project Structure
```text
binance-trading-bot/
├─ app.py
├─ cli.py
├─ README.md
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ binance-skill.md
├─ bot/
│  ├─ __init__.py
│  ├─ client.py
│  ├─ logging_config.py
│  ├─ orders.py
│  └─ validators.py
└─ logs/
```

## Setup
- Clone the repo.
- Install dependencies:

```bash
pip install -r requirements.txt
```

- Copy the environment template and fill in your testnet API keys from https://testnet.binancefuture.com:

```bash
cp .env.example .env
```

- How to get testnet keys: create a Futures Testnet account, then generate API keys from the account's API Management page.

## CLI Usage
MARKET buy order:

```bash
python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.01
```

LIMIT sell order:

```bash
python cli.py --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.01 --price 50000
```

MARKET sell order:

```bash
python cli.py --symbol BTCUSDT --side SELL --order-type MARKET --quantity 0.001
```

Validation failure example (missing required LIMIT price):

```bash
python cli.py --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.01
```

STOP-LIMIT sell order:

```bash
python cli.py --symbol BTCUSDT --side SELL --order-type STOP-LIMIT --quantity 0.01 --price 50000 --stop-price 49500
```

## Streamlit UI
Start the UI:

```bash
streamlit run app.py
```

Features:
- Order form for MARKET, LIMIT, STOP-LIMIT, and STOP_MARKET orders
- Live mark price metric for the selected symbol
- Open positions panel
- Close position action (market close in opposite direction)
- Session order history (in-memory per browser session)
- Live execution log viewer backed by `logs/trading.log`

Use the log tab to inspect the latest execution trail after placing an order, or after a validation/API failure during a testnet run.

The Streamlit UI is included for interactive order entry, live mark price context, positions, and log inspection.

## Design Decisions
- Why python-binance over raw requests? It provides a higher-level abstraction, handles request signing/authentication, and supports a `testnet=True` switch for the Futures Testnet endpoint.
- How is input validated? A dedicated `validators.py` layer validates and normalizes inputs before any API call, used in both the CLI and Streamlit UI.
- How are errors handled? `BinanceAPIException` (API errors) and `BinanceRequestException` (network errors) are handled explicitly, logged, and surfaced with clean user-facing messages.
- Why Typer for CLI? It provides typed options, generates `--help` automatically, and supports clean exit behavior for validation/API failures.
- Why is the client a wrapper class? It centralizes testnet configuration, environment loading, and logging in one place, and makes it straightforward to swap to mainnet later.
- How does logging work? A dual-handler logger writes DEBUG-level events to `logs/trading.log`, INFO-level events to the console, logs outgoing request parameters at INFO, raw API responses at DEBUG, and full tracebacks for failures.

## Assumptions
- USDT-M Futures testnet only.
- Quantity is in base asset units (for example, BTC for `BTCUSDT`).
- Limit price must be within the exchange PERCENT_PRICE filter range.
- Testnet accounts reset periodically; regenerate keys if you see authentication errors.

## Sample Log Output
```text
2026-07-21 20:39:17,189 | INFO | trading_bot | Order request initiated | Symbol=BTCUSDT Side=BUY Type=MARKET Qty=0.001 Price=None StopPrice=None
2026-07-21 20:39:17,839 | DEBUG | trading_bot | Raw order response payload: {'orderId': 23173416653, 'symbol': 'BTCUSDT', 'status': 'NEW', 'clientOrderId': 'x-Cb7ytekJeb55b06311609b488b073f', 'price': '0.00', 'origQty': '0.0010', 'executedQty': '0.0000', 'cumQty': '0.0000', 'timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False, 'side': 'BUY', 'positionSide': 'BOTH', 'stopPrice': '0.00', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False, 'origType': 'MARKET', 'priceMatch': 'NONE', 'selfTradePreventionMode': 'EXPIRE_MAKER', 'goodTillDate': 0, 'updateTime': 1784646557804}
2026-07-21 20:42:55,814 | INFO | trading_bot | Order request initiated | Symbol=BTCUSDT Side=SELL Type=MARKET Qty=0.001 Price=None StopPrice=None
2026-07-21 20:42:56,452 | DEBUG | trading_bot | Raw order response payload: {'orderId': 23173856375, 'symbol': 'BTCUSDT', 'status': 'NEW', 'clientOrderId': 'x-Cb7ytekJ73dc9931587127aff92cc0', 'price': '0.00', 'origQty': '0.0010', 'executedQty': '0.0000', 'cumQty': '0.0000', 'timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False, 'side': 'SELL', 'positionSide': 'BOTH', 'stopPrice': '0.00', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False, 'origType': 'MARKET', 'priceMatch': 'NONE', 'selfTradePreventionMode': 'EXPIRE_MAKER', 'goodTillDate': 0, 'updateTime': 1784646776454}
```

The full traceback is written to `logs/trading.log` and shown in the Streamlit "Live Execution Logs" tab for recent runs.
