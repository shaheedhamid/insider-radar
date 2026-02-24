#!/usr/bin/env python3
"""
Insider Radar - OpenInsider Scraper
Scrapes open market purchases from openinsider.com and saves to data files.
"""

import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = "http://openinsider.com/screener"
PARAMS = {
    "s": "", "o": "", "pl": "", "ph": "", "ll": "", "lh": "",
    "fd": 730,          # last 730 days (~2 years)
    "fdr": "",
    "td": 0, "tdr": "",
    "fdlyl": "", "fdlyh": "", "daysago": "",
    "xp": 1,
    "vl": 50,           # minimum value $50K (server-side filter, $K units)
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
    "sortcol": 0,
    "cnt": 1000,
    "page": 1,
}

MIN_TRADE_VALUE = 50_000  # minimum trade value in dollars (enforced in-code)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LATEST_JSON = os.path.join(DATA_DIR, "latest.json")
HISTORY_CSV = os.path.join(DATA_DIR, "history.csv")

CSV_FIELDNAMES = [
    "filing_date",
    "trade_date",
    "ticker",
    "company",
    "insider_name",
    "title",
    "trade_type",
    "price",
    "qty",
    "owned",
    "delta_own",
    "value",
    "cluster_buy",
]

CLUSTER_WINDOW_DAYS = 14  # days to look for cluster buys
CLUSTER_MIN_INSIDERS = 2   # insiders required to flag cluster buy
HISTORY_DAYS = 1000        # how many days of data to keep in latest.json


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_number(text: str) -> str:
    """Strip currency symbols, commas, and whitespace."""
    return re.sub(r"[$,\s%+]", "", text).strip()


def parse_value(text: str) -> float:
    """Convert a formatted number string to float, return 0 on failure."""
    try:
        return float(clean_number(text))
    except (ValueError, TypeError):
        return 0.0


def parse_date(text: str) -> str:
    """Return ISO date string from various formats, or empty string."""
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # Try to grab just the date portion if a time is appended
    match = re.match(r"(\d{4}-\d{2}-\d{2})", text)
    if match:
        return match.group(1)
    return text


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

def fetch_trades() -> list[dict]:
    """Fetch and parse insider trades from openinsider.com."""
    print(f"Fetching data from {BASE_URL} ...")
    try:
        resp = requests.get(BASE_URL, params=PARAMS, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"ERROR fetching data: {exc}", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(resp.text, "html.parser")

    # The main results table has class "tinytable"
    table = soup.find("table", {"class": "tinytable"})
    if table is None:
        print("ERROR: Could not find results table in page.", file=sys.stderr)
        # Dump first 2000 chars for debugging
        print(resp.text[:2000], file=sys.stderr)
        sys.exit(1)

    rows = table.find("tbody").find_all("tr")
    trades = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 16:
            continue

        # Column indices (0-based) from openinsider screener table:
        # 0: X (checkbox), 1: Filing Date, 2: Trade Date, 3: Ticker, 4: Company Name
        # 5: Insider Name, 6: Title, 7: Trade Type, 8: Price, 9: Qty, 10: Owned
        # 11: ΔOwn, 12: Value, 13: 1d, 14: 1w, 15: 1m, 16: 6m
        filing_date = parse_date(cells[1].get_text(strip=True))
        trade_date  = parse_date(cells[2].get_text(strip=True))
        ticker      = cells[3].get_text(strip=True)
        company     = cells[4].get_text(strip=True)
        insider     = cells[5].get_text(strip=True)
        title       = cells[6].get_text(strip=True)
        trade_type  = cells[7].get_text(strip=True)
        price       = clean_number(cells[8].get_text(strip=True))
        qty         = clean_number(cells[9].get_text(strip=True))
        owned       = clean_number(cells[10].get_text(strip=True))
        delta_own   = cells[11].get_text(strip=True).strip()
        value       = clean_number(cells[12].get_text(strip=True))

        trades.append({
            "filing_date":  filing_date,
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

    # Defensive filters (API params are not reliably honoured server-side)
    trades = [t for t in trades if t["trade_type"].startswith("P")]
    trades = [t for t in trades if parse_value(t["value"]) >= MIN_TRADE_VALUE]
    print(f"Parsed {len(trades)} purchase trades >= ${MIN_TRADE_VALUE:,} from the page.")
    return trades


# ---------------------------------------------------------------------------
# Cluster buy detection
# ---------------------------------------------------------------------------

def detect_clusters(trades: list[dict]) -> list[dict]:
    """Flag trades that are part of a cluster buy (2+ insiders, same ticker, 14-day window)."""
    # Group trades by ticker
    by_ticker: dict[str, list[dict]] = defaultdict(list)
    for t in trades:
        by_ticker[t["ticker"]].append(t)

    for ticker, ticker_trades in by_ticker.items():
        # Sort by trade date
        sorted_trades = sorted(
            ticker_trades,
            key=lambda x: x["trade_date"] if x["trade_date"] else "0000-00-00",
        )

        # Sliding-window cluster detection
        for i, anchor in enumerate(sorted_trades):
            if not anchor["trade_date"]:
                continue
            try:
                anchor_date = datetime.strptime(anchor["trade_date"], "%Y-%m-%d")
            except ValueError:
                continue

            window_end = anchor_date + timedelta(days=CLUSTER_WINDOW_DAYS)
            cluster_insiders = {anchor["insider_name"]}

            for j in range(i + 1, len(sorted_trades)):
                other = sorted_trades[j]
                if not other["trade_date"]:
                    continue
                try:
                    other_date = datetime.strptime(other["trade_date"], "%Y-%m-%d")
                except ValueError:
                    continue
                if other_date > window_end:
                    break
                cluster_insiders.add(other["insider_name"])

            if len(cluster_insiders) >= CLUSTER_MIN_INSIDERS:
                # Mark all trades in this window for this ticker
                for t in sorted_trades:
                    if not t["trade_date"]:
                        continue
                    try:
                        td = datetime.strptime(t["trade_date"], "%Y-%m-%d")
                    except ValueError:
                        continue
                    if anchor_date <= td <= window_end:
                        t["cluster_buy"] = True

    return trades


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def load_existing_csv() -> dict[str, dict]:
    """Load existing history.csv rows into a dict keyed by unique row ID."""
    existing = {}
    if not os.path.exists(HISTORY_CSV):
        return existing
    with open(HISTORY_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['filing_date']}|{row['ticker']}|{row['insider_name']}|{row['value']}"
            existing[key] = row
    return existing


def load_history_as_list() -> list[dict]:
    """Load all rows from history.csv as a list of trade dicts."""
    if not os.path.exists(HISTORY_CSV):
        return []
    trades = []
    with open(HISTORY_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["cluster_buy"] = row.get("cluster_buy", "").strip().lower() == "true"
            trades.append(dict(row))
    return trades


def save_history_csv(new_trades: list[dict]) -> int:
    """Append new trades to history.csv, skipping duplicates. Returns number added."""
    existing = load_existing_csv()
    added = 0
    file_exists = os.path.exists(HISTORY_CSV)

    with open(HISTORY_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        if not file_exists or os.path.getsize(HISTORY_CSV) == 0:
            writer.writeheader()
        for trade in new_trades:
            key = f"{trade['filing_date']}|{trade['ticker']}|{trade['insider_name']}|{trade['value']}"
            if key not in existing:
                writer.writerow({k: trade.get(k, "") for k in CSV_FIELDNAMES})
                existing[key] = trade
                added += 1

    return added


def save_latest_json(trades: list[dict]) -> None:
    """Save the most recent HISTORY_DAYS of trades to latest.json (overwrite)."""
    INT32_MAX = 2_147_483_647  # OpenInsider overflow sentinel — exclude
    cutoff = (datetime.utcnow() - timedelta(days=HISTORY_DAYS)).strftime("%Y-%m-%d")
    filtered = [
        t for t in trades
        if t.get("filing_date", "") >= cutoff
        and MIN_TRADE_VALUE <= parse_value(t.get("value", "0")) < INT32_MAX
    ]

    payload = {
        "last_updated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "trade_count": len(filtered),
        "trades": filtered,
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LATEST_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved {len(filtered)} trades to {LATEST_JSON}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    trades = fetch_trades()
    if not trades:
        print("No trades found. Exiting without writing files.")
        sys.exit(0)

    trades = detect_clusters(trades)

    # Persist new trades to CSV
    added = save_history_csv(trades)
    print(f"Added {added} new rows to {HISTORY_CSV}")

    # Build latest.json from the full CSV history (up to HISTORY_DAYS days),
    # re-running cluster detection so cross-run clusters are caught correctly.
    all_trades = load_history_as_list()
    all_trades = detect_clusters(all_trades)
    save_latest_json(all_trades)

    print("Done.")


if __name__ == "__main__":
    main()
