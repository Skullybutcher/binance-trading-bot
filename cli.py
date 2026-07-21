from typing import Optional

import typer
from binance.exceptions import BinanceAPIException, BinanceRequestException
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from bot.client import BinanceClient
from bot.logging_config import setup_logging
from bot.orders import (
	place_limit_order,
	place_market_order,
	place_stop_market_order,
	place_stop_limit_order,
)
from bot.validators import (
	validate_order_type,
	validate_price,
	validate_quantity,
	validate_stop_price,
	validate_side,
	validate_symbol,
)

app = typer.Typer()
console = Console()


def _format_money(value: object) -> str:
	if value in (None, "", "N/A"):
		return "N/A"
	try:
		return f"{float(value):,.8f}".rstrip("0").rstrip(".")
	except (TypeError, ValueError):
		return str(value)


def _render_request_panel(params: dict) -> None:
	table = Table.grid(expand=True)
	table.add_column(style="bold cyan", width=14)
	table.add_column(style="white")
	table.add_row("Symbol", params.get("symbol", "N/A"))
	table.add_row("Side", params.get("side", "N/A"))
	table.add_row("Type", params.get("type", "N/A"))
	table.add_row("Quantity", str(params.get("quantity", "N/A")))
	table.add_row("Price", _format_money(params.get("price")))
	table.add_row("Stop Price", _format_money(params.get("stop_price")))
	console.print(Panel(table, title="Order Request", border_style="cyan"))


def _render_response_table(response: dict) -> None:
	table = Table(title="Order Response", show_lines=False)
	table.add_column("Field", style="bold cyan")
	table.add_column("Value", style="white")
	table.add_row("orderId", str(response.get("orderId", "N/A")))
	table.add_row("status", str(response.get("status", "N/A")))
	table.add_row("executedQty", str(response.get("executedQty", "N/A")))
	table.add_row("avgPrice", _format_money(response.get("avgPrice")))
	table.add_row("type", str(response.get("type", "N/A")))
	console.print(table)


def _render_error_panel(title: str, message: str) -> None:
	console.print(Panel(message, title=title, border_style="red"))


def _run_place_order(
	symbol: str,
	side: str,
	order_type: str,
	quantity: float,
	price: Optional[float] = None,
	stop_price: Optional[float] = None,
) -> None:
	logger = setup_logging("trading_bot")

	try:
		cleaned_symbol = validate_symbol(symbol)
		cleaned_side = validate_side(side)
		cleaned_order_type = validate_order_type(order_type)
		cleaned_quantity = validate_quantity(quantity)
		cleaned_price = validate_price(price, cleaned_order_type)
		cleaned_stop_price: Optional[float] = None
		if cleaned_order_type in {"STOP", "STOP-LIMIT", "STOP_MARKET"}:
			if stop_price is None:
				raise ValueError("Stop price is required for stop orders.")
			client = BinanceClient()
			cleaned_stop_price = validate_stop_price(stop_price, cleaned_side, client.get_mark_price(cleaned_symbol))
		else:
			client = BinanceClient()
	except ValueError as exc:
		logger.exception("Validation error")
		_render_error_panel("Validation Error", str(exc))
		raise typer.Exit(1)

	_render_request_panel(
		{
			"symbol": cleaned_symbol,
			"side": cleaned_side,
			"type": cleaned_order_type,
			"quantity": cleaned_quantity,
			"price": cleaned_price,
			"stop_price": cleaned_stop_price,
		}
	)

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
		elif cleaned_order_type == "STOP_MARKET":
			response = place_stop_market_order(
				client=client,
				symbol=cleaned_symbol,
				side=cleaned_side,
				quantity=cleaned_quantity,
				stop_price=cleaned_stop_price,
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
		logger.exception("Order placement failed")
		_render_error_panel("API Failure", str(exc))
		raise typer.Exit(1)

	_render_response_table(response)
	console.print(Panel("Order placed successfully", border_style="green"))


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
