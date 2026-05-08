import logging
import os
import sys


def setup_logging(name: str = "trading_bot") -> logging.Logger:
	"""Configure and return a logger for the trading bot."""
	logger = logging.getLogger(name)
	logger.setLevel(logging.INFO)

	if logger.handlers:
		return logger

	os.makedirs("logs", exist_ok=True)

	log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
	formatter = logging.Formatter(log_format)

	file_handler = logging.FileHandler("logs/trading_bot.log", mode="a", encoding="utf-8")
	file_handler.setLevel(logging.INFO)
	file_handler.setFormatter(formatter)

	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setLevel(logging.WARNING)
	console_handler.setFormatter(formatter)

	logger.addHandler(file_handler)
	logger.addHandler(console_handler)
	logger.propagate = False

	return logger
