from typing import Optional

import typer
from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.client import BinanceClient
from bot.logging_config import setup_logging
from bot.orders import (
	format_order_response,
	format_order_summary,
	place_limit_order,
	place_market_order,
	place_stop_limit_order,
)
from bot.validators import (
	validate_order_type,
	validate_price,
	validate_quantity,
	validate_side,
	validate_symbol,
)

app = typer.Typer()


def _run_place_order(
	symbol: str,
	side: str,
	order_type: str,
	quantity: float,
	price: Optional[float] = None,
	stop_price: Optional[float] = None,
) -> None:
	setup_logging()

	try:
		cleaned_symbol = validate_symbol(symbol)
		cleaned_side = validate_side(side)
		cleaned_order_type = validate_order_type(order_type)
		cleaned_quantity = validate_quantity(quantity)
		cleaned_price = validate_price(price, cleaned_order_type)
		cleaned_stop_price: Optional[float] = None
		if cleaned_order_type == "STOP-LIMIT":
			if stop_price is None:
				raise ValueError("Stop price is required for STOP-LIMIT orders.")
			cleaned_stop_price = float(stop_price)
			if cleaned_stop_price <= 0:
				raise ValueError("Stop price must be greater than 0 for STOP-LIMIT orders.")
	except ValueError as exc:
		typer.echo(str(exc))
		raise typer.Exit(1)

	summary = format_order_summary(
		{
			"symbol": cleaned_symbol,
			"side": cleaned_side,
			"type": cleaned_order_type,
			"quantity": cleaned_quantity,
			"price": cleaned_price,
			"stop_price": cleaned_stop_price,
		}
	)
	typer.echo(summary)

	client = BinanceClient()

	try:
		if cleaned_order_type == "MARKET":
			response = place_market_order(
				client=client,
				symbol=cleaned_symbol,
				side=cleaned_side,
				quantity=cleaned_quantity,
			)
		elif cleaned_order_type == "LIMIT":
			response = place_limit_order(
				client=client,
				symbol=cleaned_symbol,
				side=cleaned_side,
				quantity=cleaned_quantity,
				price=cleaned_price,
			)
		else:
			response = place_stop_limit_order(
				client=client,
				symbol=cleaned_symbol,
				side=cleaned_side,
				quantity=cleaned_quantity,
				price=cleaned_price,
				stop_price=cleaned_stop_price,
			)
	except (BinanceAPIException, BinanceRequestException) as exc:
		typer.echo(f"❌ Order failed: {exc}")
		raise typer.Exit(1)

	typer.echo(format_order_response(response))
	typer.echo("✅ Order placed successfully")


@app.callback(invoke_without_command=True)
def place_order(
	ctx: typer.Context,
	symbol: str = typer.Option(..., "--symbol"),
	side: str = typer.Option(..., "--side"),
	order_type: str = typer.Option(..., "--order-type"),
	quantity: float = typer.Option(..., "--quantity"),
	price: Optional[float] = typer.Option(None, "--price"),
	stop_price: Optional[float] = typer.Option(None, "--stop-price"),
) -> None:
	if ctx.invoked_subcommand is None:
		_run_place_order(symbol, side, order_type, quantity, price, stop_price)


if __name__ == "__main__":
	app()
