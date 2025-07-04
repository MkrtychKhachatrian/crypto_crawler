"""
Crypto Crawler Challenge - Phase 1: Price Pulse

Polls CoinGecko's API for the live Bitcoin price every second,
prints the price and a simple moving average (SMA) of the last 10 prices,
handles network errors robustly with exponential backoff,
and exits gracefully on SIGINT (Ctrl-C).

Usage:
    python price_pulse.py
"""

import requests
import time
import signal
import sys
import logging
from collections import deque
from datetime import datetime
from typing import Tuple, Deque

should_shutdown: bool = False


def signal_handler(sig: int, frame) -> None:
    """
    Handles SIGINT (Ctrl-C) signal for graceful shutdown.

    Args:
        sig (int): Signal number.
        frame: Current stack frame.
    """
    global should_shutdown
    print("\nShutting down...")
    should_shutdown = True


# Register the signal handler for SIGINT (Ctrl-C)
signal.signal(signal.SIGINT, signal_handler)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

API_URL: str = "https://api.coingecko.com/api/v3/simple/price"
PARAMS: dict = {
    "ids": "bitcoin",
    "vs_currencies": "usd",
    "include_last_updated_at": "true"
}


def fetch_price() -> Tuple[float, str]:
    """
    Fetches the current Bitcoin price in USD and its last updated timestamp.

    Returns:
        Tuple[float, str]: A tuple containing the price and the formatted UTC timestamp.

    Raises:
        requests.RequestException: If the HTTP request fails.
        ValueError: If the expected data is missing from the response.
    """
    resp = requests.get(API_URL, params=PARAMS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    price = data["bitcoin"]["usd"]
    ts_unix = data["bitcoin"]["last_updated_at"]
    dt = datetime.utcfromtimestamp(ts_unix).strftime("%Y-%m-%dT%H:%M:%S")
    return price, dt


def main() -> None:
    """
    Runs the main polling loop.

    - Fetches and prints BTC price and SMA(10) every second.
    - Handles exponential backoff on API errors.
    - Logs warnings and errors.
    - Exits gracefully on SIGINT.
    """
    price_window: Deque[float] = deque(maxlen=10)
    consecutive_failures: int = 0
    backoff: int = 1

    while not should_shutdown:
        try:
            price, timestamp = fetch_price()
            price_window.append(price)
            sma = sum(price_window) / len(price_window) if price_window else price
            print(f"[{timestamp}] BTC → USD: ${price:,.2f} | SMA(10): ${sma:,.2f}")

            consecutive_failures = 0
            backoff = 1
            for _ in range(10):
                if should_shutdown:
                    break
                time.sleep(0.1)
        except (requests.RequestException, ValueError) as e:
            logging.warning("%s", e)
            consecutive_failures += 1
            logging.info("Retrying in %d seconds...", backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)

            if consecutive_failures >= 5:
                logging.error("5 consecutive failures. Continuing to poll...")

    sys.exit(0)


if __name__ == "__main__":
    main()
