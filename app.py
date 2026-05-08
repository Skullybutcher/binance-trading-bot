from datetime import datetime

import streamlit as st
from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.client import BinanceClient
from bot.orders import place_limit_order, place_market_order
from bot.validators import validate_order_type, validate_price, validate_quantity, validate_side, validate_symbol

st.session_state.setdefault("order_history", [])
st.session_state.setdefault("open_positions", [])
try:
    client = BinanceClient()
except Exception as exc:
    st.error(str(exc))
    st.stop()


@st.cache_data(ttl=5)
def get_ticker_price(symbol):
    return client.futures_symbol_ticker(symbol=symbol)["price"]


def add_history(symbol, side, order_type, response):
    st.session_state["order_history"].append({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "symbol": symbol, "side": side, "type": order_type, "orderId": response.get("orderId"), "status": response.get("status"), "executedQty": response.get("executedQty"), "avgPrice": response.get("avgPrice") or "Pending"})

st.title("Binance Futures Testnet — Order Placer")
side = st.selectbox("Side", ["BUY", "SELL"])
order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])
symbol = st.text_input("Symbol", value="BTCUSDT")
if symbol.strip():
    try:
        cleaned_symbol = validate_symbol(symbol)
        st.caption(f"Current market price: {get_ticker_price(cleaned_symbol)}")
    except Exception as exc:
        st.error(str(exc))
quantity = st.number_input("Quantity", min_value=0.001, step=0.001, value=0.001, format="%.3f")
price = None
if order_type == "LIMIT":
    price = st.number_input("Price", min_value=0.0, step=0.1, value=1000.0, format="%.2f")

if st.button("Place Order"):
    try:
        cleaned_symbol = validate_symbol(symbol)
        cleaned_side = validate_side(side)
        cleaned_order_type = validate_order_type(order_type)
        cleaned_quantity = validate_quantity(quantity)
        cleaned_price = validate_price(price, cleaned_order_type)
    except ValueError as exc:
        st.error(str(exc))
    else:
        try:
            response = place_market_order(client, cleaned_symbol, cleaned_side, cleaned_quantity) if cleaned_order_type == "MARKET" else place_limit_order(client, cleaned_symbol, cleaned_side, cleaned_quantity, cleaned_price)
            add_history(cleaned_symbol, cleaned_side, cleaned_order_type, response)
            avg = response.get("avgPrice")
            st.success(f"Order placed | orderId={response.get('orderId')} status={response.get('status')} executedQty={response.get('executedQty')} avgPrice={'Pending' if avg in (None, '', '0', 0, '0.0') else avg}")
        except (BinanceAPIException, BinanceRequestException) as exc:
            st.error(str(exc))

st.divider()
st.subheader("📊 Open Positions")
if st.button("Refresh Positions"):
    try:
        st.session_state["open_positions"] = [p for p in client.futures_position_information() if float(p["positionAmt"]) != 0]
    except Exception as exc:
        st.error(str(exc))
positions = st.session_state["open_positions"]
if positions:
    for i, pos in enumerate(positions):
        left, right = st.columns([3, 1])
        with left:
            st.write(f"**Symbol:** {pos['symbol']}")
            st.write(f"**Size:** {pos['positionAmt']}")
            st.write(f"**Entry Price:** {pos['entryPrice']}")
            st.write(f"**Unrealized PnL:** {pos['unRealizedProfit']}")
        with right:
            if st.button("Close", key=f"close_{i}_{pos['symbol']}"):
                try:
                    amt = float(pos["positionAmt"])
                    response = place_market_order(client, pos["symbol"], "SELL" if amt > 0 else "BUY", abs(amt))
                    add_history(pos["symbol"], "SELL" if amt > 0 else "BUY", "MARKET", response)
                    st.success(f"Closed {pos['symbol']} | orderId={response.get('orderId')}")
                except (BinanceAPIException, BinanceRequestException, Exception) as exc:
                    st.error(str(exc))
else:
    st.info("No open positions")

st.divider()
st.subheader("🕓 Orders This Session")
history = list(reversed(st.session_state["order_history"]))
if history:
    st.dataframe(history, use_container_width=True)
else:
    st.info("No orders placed yet this session")