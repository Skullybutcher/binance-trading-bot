def validate_symbol(symbol: str) -> str:
	if not isinstance(symbol, str):
		raise ValueError("Symbol must be a string.")

	cleaned_symbol = symbol.strip().upper()
	if not cleaned_symbol:
		raise ValueError("Symbol cannot be empty.")

	valid_suffixes = ("USDT", "BUSD", "BTC")
	if not cleaned_symbol.endswith(valid_suffixes):
		raise ValueError("Symbol must end with USDT, BUSD, or BTC.")

	return cleaned_symbol


def validate_side(side: str) -> str:
	if not isinstance(side, str):
		raise ValueError("Side must be a string.")

	cleaned_side = side.strip().upper()
	if cleaned_side not in {"BUY", "SELL"}:
		raise ValueError("Side must be BUY or SELL.")

	return cleaned_side


def validate_order_type(order_type: str) -> str:
	if not isinstance(order_type, str):
		raise ValueError("Order type must be a string.")

	cleaned_order_type = order_type.strip().upper()
	if cleaned_order_type not in {"MARKET", "LIMIT", "STOP-LIMIT"}:
		raise ValueError("Order type must be MARKET, LIMIT, or STOP-LIMIT.")

	return cleaned_order_type


def validate_quantity(quantity: float) -> float:
	try:
		cleaned_quantity = float(quantity)
	except (TypeError, ValueError) as exc:
		raise ValueError("Quantity must be a number.") from exc

	if cleaned_quantity <= 0:
		raise ValueError("Quantity must be greater than 0.")

	return cleaned_quantity


def validate_price(price: float | None, order_type: str) -> float | None:
	cleaned_order_type = validate_order_type(order_type)

	if cleaned_order_type == "MARKET":
		return None

	if price is None:
		raise ValueError(f"Price is required for {cleaned_order_type} orders.")

	try:
		cleaned_price = float(price)
	except (TypeError, ValueError) as exc:
		raise ValueError("Price must be a number.") from exc

	if cleaned_price <= 0:
		raise ValueError(f"Price must be greater than 0 for {cleaned_order_type} orders.")

	return cleaned_price
