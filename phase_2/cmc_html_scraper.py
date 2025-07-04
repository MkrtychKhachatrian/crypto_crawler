"""
Phase 2.1: CoinMarketCap HTML Scraper

Scrapes the top 100 cryptocurrencies from https://coinmarketcap.com/ (pages 1–5),
extracting Rank, Name, Symbol, Price (USD), 24h % Change, and Market Cap (USD),
and writes the results to a CSV file.

Usage:
    python cmc_html_scraper.py
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
import os
from typing import List, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

BASE_URL = "https://coinmarketcap.com/"
OUTPUT_CSV = "data/cmc_top100_html.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def parse_coin_row(tr) -> Dict[str, str]:
    """
    Parses a single row of the CoinMarketCap table.

    Args:
        tr: BeautifulSoup Tag object for the row.

    Returns:
        Dict[str, str]: Parsed coin data, or empty dict if not a coin row.
    """
    tds = tr.find_all('td')
    if len(tds) < 8:
        return {}
    try:
        rank = tds[1].get_text(strip=True)
        name = ""
        symbol = ""
        p_tags = tds[2].find_all('p')
        if len(p_tags) >= 2:
            name = p_tags[0].get_text(strip=True)
            symbol = p_tags[1].get_text(strip=True)
        else:
            cell_text = tds[2].get_text(strip=True)
            if cell_text:
                parts = cell_text.split()
                name = parts[0] if parts else ""
                symbol = parts[1] if len(parts) > 1 else ""

        price = tds[3].get_text(strip=True).replace('$', '').replace(',', '')
        change_24h = tds[4].get_text(strip=True).replace('%', '')
        market_cap = tds[7].get_text(strip=True).replace('$', '').replace(',', '')

        if not name or not symbol or not price.replace('.', '', 1).isdigit():
            return {}

        return {
            "Rank": rank,
            "Name": name,
            "Symbol": symbol,
            "Price (USD)": price,
            "24h % Change": change_24h,
            "Market Cap (USD)": market_cap
        }
    except Exception as e:
        logging.warning(f"Failed to parse row: {e}")
        return {}


def scrape_cmc_top_100() -> List[Dict[str, str]]:
    """
    Scrapes the top 100 cryptocurrencies from CoinMarketCap (pages 1–5).

    Returns:
        List[Dict[str, str]]: List of coin data dictionaries.
    """
    all_coins = []
    for page in range(1, 6):
        url = BASE_URL + (f"?page={page}" if page > 1 else "")
        logging.info(f"Fetching {url}")
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find('tbody')
        if not table:
            logging.error("Failed to find coin table.")
            continue
        rows = table.find_all('tr')
        logging.info(f"Page {page} rows: {len(rows)}")
        parsed_this_page = 0
        for tr in rows:
            data = parse_coin_row(tr)
            if data:
                all_coins.append(data)
                parsed_this_page += 1
        logging.info(f"Parsed {parsed_this_page} coins from page {page}")
        time.sleep(1)
    logging.info(f"Total real coins scraped: {len(all_coins)}")
    return all_coins


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
    Main entry point for scraping and saving data.
    """
    coins = scrape_cmc_top_100()
    top_100 = coins[:100]
    write_to_csv(top_100, OUTPUT_CSV)


if __name__ == "__main__":
    main()
