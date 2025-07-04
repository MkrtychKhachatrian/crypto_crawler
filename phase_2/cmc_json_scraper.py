"""
Phase 2.2: CoinGecko JSON API Scraper (Fallback for CoinMarketCap block)

Fetches the top 100 cryptocurrencies from CoinGecko's public API,
extracting Rank, Name, Symbol, Price (USD), 24h % Change, and Market Cap (USD),
and writes the results to a CSV file.

Usage:
    python cmc_json_scraper.py
"""

import requests
import csv
import logging
import os
import time
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

JSON_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
OUTPUT_CSV = "data/cmc_top100_json.csv"


def fetch_top_100_coingecko() -> List[Dict[str, str]]:
    """
    Fetches the top 100 coins using CoinGecko's public API.

    Returns:
        List[Dict[str, str]]: List of coin data dictionaries.
    """
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": "false"
    }
    start_time = time.time()
    resp = requests.get(JSON_API_URL, params=params, timeout=10)
    duration = time.time() - start_time
    resp.raise_for_status()
    data = resp.json()
    logging.info(f"Fetched {len(data)} coins from CoinGecko API in {duration:.3f} seconds")
    coins = []
    for idx, coin in enumerate(data, start=1):
        try:
            price = coin["current_price"]
            percent_change_24h = coin["price_change_percentage_24h"]
            market_cap = coin["market_cap"]
            coins.append({
                "Rank": idx,
                "Name": coin["name"],
                "Symbol": coin["symbol"].upper(),
                "Price (USD)": f"{price:.8f}".rstrip('0').rstrip('.'),
                "24h % Change": f"{percent_change_24h:.2f}",
                "Market Cap (USD)": f"{market_cap:.2f}".rstrip('0').rstrip('.'),
            })
        except Exception as e:
            logging.warning(f"Failed to parse coin data: {e}")
    return coins


def write_to_csv(coins: List[Dict[str, str]], filename: str) -> None:
    """
    Writes coin data to CSV.

    Args:
        coins: List of coin data dictionaries.
        filename: Output CSV filename.
    """
    if not coins:
        logging.error("No data to write.")
        return
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    fieldnames = ["Rank", "Name", "Symbol", "Price (USD)", "24h % Change", "Market Cap (USD)"]
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(coins)
    logging.info(f"Wrote {len(coins)} records to {filename}")


def main() -> None:
    """
    Main entry point for JSON scraping and saving.
    """
    coins = fetch_top_100_coingecko()
    write_to_csv(coins, OUTPUT_CSV)


if __name__ == "__main__":
    main()
