# Crypto Crawler 

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MkrtychKhachatrian/crypto_crawler.git
   cd crypto_crawler
2. **(Optional) Create and activate a virtual environment:**

   **For Unix/macOS:**
   ```bash
   python -m venv venv
   source venv/bin/activate

  **For Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

## Performance Observations

**Code length:**

phase1/price_pulse.py: ~116 lines

phase2/cmc_html_scraper.py: ~146 lines

phase2/cmc_json_scraper.py: ~96 lines

**Throughput:**

Phase 1: 1 request per second 

Phase 2.1 (HTML): ~5 requests (5 pages, some parsing delay), ~7–10 seconds for 100 coins

Phase 2.2 (JSON): 1 request for all 100 coins, ~0.5 seconds total
