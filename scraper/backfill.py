#!/usr/bin/env python3
"""
One-time historical backfill for Insider Radar.

Uses the correct OpenInsider screener URL (provided by user):
  fd=730    → last 730 days (~2 years)
  vl=50     → minimum value $50K  (OpenInsider uses $K units)
  page=N    → page-based pagination (1 … MAX_PAGES)
  cnt=1000  → 1000 rows per page

Merges all rows into data/history.csv and rebuilds data/latest.json.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from bs4 import BeautifulSoup

from scrape import (
    HEADERS,
    MIN_TRADE_VALUE,
    DATA_DIR,
    clean_number,
    parse_date,
    parse_time,
    parse_value,
    detect_clusters,
    save_history_csv,
    load_history_as_list,
    save_latest_json,
)

BASE_URL  = "http://openinsider.com/screener"
MAX_PAGES = 5

BACKFILL_PARAMS = {
    "s": "", "o": "", "pl": "", "ph": "", "ll": "", "lh": "",
    "fd": 730,          # last 730 days
    "fdr": "",
    "td": 0, "tdr": "",
    "fdlyl": "", "fdlyh": "", "daysago": "",
    "xp": 1,            # required by this endpoint
    "vl": 50,           # minimum value in $K  (= $50,000)
    "vh": "",
    "ocl": "", "och": "",
    "sic1": -1, "sicl": 100, "sich": 9999,
    "isofficer": 1, "iscob": 1, "isceo": 1, "ispres": 1,
    "iscoo": 1, "iscfo": 1, "isgc": 1, "isvp": 1,
    "isdirector": 1, "istenpercent": 1, "isother": 1,
    "grp": 0,
    "nfl": "", "nfh": "", "nil": "", "nih": "",
    "nol": "", "noh": "", "v2l": "", "v2h": "",
    "oc2l": "", "oc2h": "",
    "sortcol": 0,       # sort by filing date
    "cnt": 1000,
    # 'page' is set per request
}


def fetch_page(page: int) -> list[dict]:
    params = {**BACKFILL_PARAMS, "page": page}
    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  ERROR on page {page}: {exc}", file=sys.stderr)
        return []

    soup  = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", {"class": "tinytable"})
    if not table:
        return []

    tbody = table.find("tbody")
    if not tbody:
        return []

    trades = []
    for row in tbody.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 16:
            continue

        filing_raw  = cells[1].get_text(strip=True)
        filing_date = parse_date(filing_raw)
        filing_time = parse_time(filing_raw)
        trade_date  = parse_date(cells[2].get_text(strip=True))
        ticker      = cells[3].get_text(strip=True)
        company     = cells[4].get_text(strip=True)
        insider     = cells[5].get_text(strip=True)
        title       = cells[6].get_text(strip=True)
        trade_type  = cells[7].get_text(strip=True)
        price       = clean_number(cells[8].get_text(strip=True))
        qty         = clean_number(cells[9].get_text(strip=True))
        owned       = clean_number(cells[10].get_text(strip=True))
        delta_own   = cells[11].get_text(strip=True)
        value       = clean_number(cells[12].get_text(strip=True))

        trades.append({
            "filing_date":  filing_date,
            "filing_time":  filing_time,
            "trade_date":   trade_date,
            "ticker":       ticker,
            "company":      company,
            "insider_name": insider,
            "title":        title,
            "trade_type":   trade_type,
            "price":        price,
            "qty":          qty,
            "owned":        owned,
            "delta_own":    delta_own,
            "value":        value,
            "cluster_buy":  False,
        })

    # In-code safety filter (server params may not be 100% reliable)
    trades = [t for t in trades if t["trade_type"].startswith("P")]
    INT32_MAX = 2_147_483_647  # OpenInsider overflow sentinel — exclude
    trades = [t for t in trades if MIN_TRADE_VALUE <= parse_value(t["value"]) < INT32_MAX]
    return trades


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    all_fetched: list[dict] = []

    for page in range(1, MAX_PAGES + 1):
        print(f"  Fetching page {page}/{MAX_PAGES} …", end=" ", flush=True)
        rows = fetch_page(page)
        print(f"{len(rows)} qualifying trades")

        if not rows:
            print("  No more results — stopping early.")
            break

        all_fetched.extend(rows)
        time.sleep(1)   # be polite to OpenInsider

    if not all_fetched:
        print("Nothing fetched.")
        sys.exit(0)

    print(f"\nTotal fetched: {len(all_fetched)} trades")

    # Show date range covered
    dates = [t["filing_date"] for t in all_fetched if t["filing_date"]]
    if dates:
        print(f"Date range:    {min(dates)}  →  {max(dates)}")

    all_fetched = detect_clusters(all_fetched)

    added = save_history_csv(all_fetched)
    print(f"New rows added to history.csv: {added}")

    # Rebuild latest.json from the complete CSV history
    all_trades = load_history_as_list()
    all_trades = detect_clusters(all_trades)
    save_latest_json(all_trades)
    print("Done.")


if __name__ == "__main__":
    main()
