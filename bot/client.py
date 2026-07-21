import os

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv

from bot.logging_config import setup_logging


class BinanceClient:
	def __init__(self) -> None:
		load_dotenv()

		api_key = os.getenv("BINANCE_API_KEY")
		api_secret = os.getenv("BINANCE_API_SECRET")
		if not api_key or not api_secret:
			raise ValueError(
				"Missing Binance API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET."
			)

		self._logger = setup_logging("trading_bot")
		self._client = Client(api_key=api_key, api_secret=api_secret, testnet=True)

	def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None) -> dict:
		cleaned_order_type = str(order_type).upper()
		params = {
			"symbol": symbol,
			"side": side,
			"quantity": quantity,
		}

		if cleaned_order_type == "MARKET":
			params["type"] = "MARKET"
		elif cleaned_order_type == "LIMIT":
			params["type"] = "LIMIT"
			params["timeInForce"] = "GTC"
			params["price"] = price
		elif cleaned_order_type in {"STOP", "STOP-LIMIT"}:
			params["type"] = "STOP"
			params["timeInForce"] = "GTC"
			params["price"] = price
			params["stopPrice"] = stop_price
		elif cleaned_order_type == "STOP_MARKET":
			params["type"] = "STOP_MARKET"
			params["stopPrice"] = stop_price
		else:
			params["type"] = cleaned_order_type

		self._logger.info(
			"Order request initiated | Symbol=%s Side=%s Type=%s Qty=%s Price=%s StopPrice=%s",
			symbol,
			side,
			cleaned_order_type,
			quantity,
			price,
			stop_price,
		)

		try:
			response = self._client.futures_create_order(**params)
			self._logger.debug("Raw order response payload: %s", response)
			return response
		except BinanceAPIException as exc:
			self._logger.exception("Binance API error %s: %s", exc.code, exc.message)
			raise
		except BinanceRequestException as exc:
			self._logger.exception("Binance network error: %s", exc)
			raise

	def futures_mark_price(self, symbol: str) -> dict:
		"""Returns the current futures mark price for a symbol."""
		return self._client.futures_mark_price(symbol=symbol)

	def get_mark_price(self, symbol: str) -> float:
		mark_price = self.futures_mark_price(symbol=symbol).get("markPrice")
		return float(mark_price)

	def futures_symbol_ticker(self, symbol: str) -> dict:
		"""Returns current price ticker for a futures symbol."""
		return self._client.futures_symbol_ticker(symbol=symbol)

	def futures_position_information(self, symbol: str = None) -> list:
		"""Returns all futures positions. Pass symbol to filter, or omit for all."""
		if symbol:
			return self._client.futures_position_information(symbol=symbol)
		return self._client.futures_position_information()
