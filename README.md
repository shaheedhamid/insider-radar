# Insider Radar 📡

A free, self-hosted GitHub Pages dashboard that tracks **insider buying activity** from [OpenInsider](http://openinsider.com). Data is automatically scraped every 2 hours via GitHub Actions and displayed in a clean, filterable dashboard.

## Features

- **Automatic scraping** every 2 hours — open market purchases only, minimum $100K trade value
- **Cluster buy detection** — flags tickers where 2+ insiders buy within 14 days
- **Interactive filters** — search by ticker/company, filter by title (CEO/Director/VP), minimum value slider
- **Sortable columns** — click any column header to sort
- **Role-based highlighting** — CEOs and Directors in green, VPs in yellow
- **Auto-refresh** — dashboard silently re-fetches data every 30 minutes
- **Mobile responsive** — works on all screen sizes

## Project Structure

```
insider-radar/
├── index.html              # Dashboard (served by GitHub Pages)
├── scraper/
│   ├── scrape.py           # Python scraper
│   └── requirements.txt    # Python dependencies
├── data/
│   ├── latest.json         # Last 1000 days of trades (overwritten each run)
│   └── history.csv         # Full trade history (append-only)
└── .github/
    └── workflows/
        └── scrape.yml      # GitHub Actions workflow
```

## Setup

### 1. Fork / Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/insider-radar.git
cd insider-radar
```

### 2. Enable GitHub Pages

1. Go to your repository on GitHub.
2. Click **Settings** → **Pages** (left sidebar).
3. Under **Source**, select **Deploy from a branch**.
4. Set the **Branch** to `main` (or `master`) and the folder to `/ (root)`.
5. Click **Save**.

Your dashboard will be live at:
```
https://shaheedhamid.github.io/insider-radar/
```

> It may take 1–2 minutes after the first push for GitHub Pages to activate.

### 3. Allow Actions to write to the repository

1. Go to **Settings** → **Actions** → **General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Click **Save**.

This allows the GitHub Actions bot to commit the updated data files automatically.

### 4. Run the scraper manually (optional first-time setup)

After setting up the repo you can trigger the scraper immediately instead of waiting up to 2 hours:

1. Go to the **Actions** tab in your repository.
2. Select **Scrape Insider Trades** from the left panel.
3. Click **Run workflow** → **Run workflow**.

This will populate `data/latest.json` and `data/history.csv` right away.

### 5. Local development

```bash
pip install -r scraper/requirements.txt
python scraper/scrape.py
# Then open index.html in a browser (serve via a local HTTP server for fetch() to work):
python -m http.server 8000
# Open http://localhost:8000
```

## Data Files

| File | Description |
|------|-------------|
| `data/latest.json` | Trades from the last 1000 days. Overwritten on every run. Served directly to the dashboard. |
| `data/history.csv` | Append-only CSV log of all trades ever seen. Never overwritten. |

### `data/latest.json` schema

```json
{
  "last_updated": "2024-01-15T08:00:00Z",
  "trade_count": 142,
  "trades": [
    {
      "filing_date": "2024-01-14",
      "trade_date":  "2024-01-12",
      "ticker":      "AAPL",
      "company":     "Apple Inc.",
      "insider_name":"John Doe",
      "title":       "Director",
      "trade_type":  "P - Purchase",
      "price":       "185.50",
      "qty":         "5000",
      "owned":       "50000",
      "delta_own":   "+11%",
      "value":       "927500",
      "cluster_buy": true
    }
  ]
}
```

## Cluster Buy Detection

A **cluster buy** is flagged when **2 or more different insiders** purchase shares of the **same ticker within a 14-day window**. Research suggests cluster buys have stronger predictive value than single insider purchases.

Cluster trades are displayed with a 🔥 **Cluster** badge in the dashboard.

## Scraper Configuration

Edit constants at the top of `scraper/scrape.py` to adjust behaviour:

| Constant | Default | Description |
|----------|---------|-------------|
| `CLUSTER_WINDOW_DAYS` | 14 | Days to look back for cluster detection |
| `CLUSTER_MIN_INSIDERS` | 2 | Insiders required to flag a cluster buy |
| `HISTORY_DAYS` | 1000 | Days of data kept in `latest.json` |

## Schedule

The scraper runs on a `cron: "0 */2 * * *"` schedule (every 2 hours). You can also trigger it manually from the **Actions** tab.

> **Note:** GitHub Actions scheduled workflows may be delayed by up to 15–30 minutes during high-load periods. Free-tier repositories with no recent activity may have scheduled workflows paused — simply push a commit to re-enable them.

## Disclaimer

This dashboard is for **informational and educational purposes only**. Insider trading data is publicly disclosed and sourced from SEC Form 4 filings via OpenInsider. Nothing here constitutes financial advice.

## License

MIT
