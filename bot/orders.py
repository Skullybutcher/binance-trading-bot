from bot.client import BinanceClient


def place_market_order(client: BinanceClient, symbol, side, quantity) -> dict:
	return client.place_order(
		symbol=symbol,
		side=side,
		order_type="MARKET",
		quantity=quantity,
	)


def place_limit_order(client: BinanceClient, symbol, side, quantity, price) -> dict:
	return client.place_order(
		symbol=symbol,
		side=side,
		order_type="LIMIT",
		quantity=quantity,
		price=price,
	)


def place_stop_limit_order(
	client: BinanceClient,
	symbol,
	side,
	quantity,
	price,
	stop_price,
) -> dict:
	return client.place_order(
		symbol=symbol,
		side=side,
		order_type="STOP-LIMIT",
		quantity=quantity,
		price=price,
		stop_price=stop_price,
	)


def format_order_summary(params: dict) -> str:
	symbol = params.get("symbol", "N/A")
	side = params.get("side", "N/A")
	order_type = params.get("type", "N/A")
	quantity = params.get("quantity", "N/A")
	price = params.get("price")
	stop_price = params.get("stop_price")
	price_display = "N/A" if price is None else str(price)
	stop_price_display = "N/A" if stop_price is None else str(stop_price)

	return (
		"-- Order Request ----------------\n"
		f"Symbol   : {symbol}\n"
		f"Side     : {side}\n"
		f"Type     : {order_type}\n"
		f"Quantity : {quantity}\n"
		f"Price    : {price_display}\n"
		f"Stop     : {stop_price_display}\n"
		"-------------------------------"
	)


def format_order_response(response: dict) -> str:
	order_id = response.get("orderId", "N/A")
	status = response.get("status", "N/A")
	executed_qty = response.get("executedQty", "N/A")
	avg_price = response.get("avgPrice")

	if avg_price in (None, "", "0", 0, "0.0"):
		avg_price_display = "Pending"
	else:
		avg_price_display = str(avg_price)

	return (
		"-- Order Response ---------------\n"
		f"Order ID    : {order_id}\n"
		f"Status      : {status}\n"
		f"Executed Qty: {executed_qty}\n"
		f"Avg Price   : {avg_price_display}\n"
		"-------------------------------"
	)
