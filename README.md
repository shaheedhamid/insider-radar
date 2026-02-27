# Insider Radar 📡

A free GitHub Pages dashboard that tracks **insider buying activity** from SEC Form 4 filings. Data is automatically scraped every 2 hours and pushed here by a separate private backend repo.

## Live Site

```
https://shaheedhamid.github.io/insider-radar/
```

## Features

- **Automatic updates** every 2 hours — open market purchases only, minimum $100K trade value
- **Cluster buy detection** — flags tickers where 2+ insiders buy within 14 days
- **Interactive filters** — search by ticker/company, filter by title (CEO/Director/VP), minimum value slider
- **Sortable columns** — click any column header to sort
- **Role-based highlighting** — CEOs and Directors in green, VPs in yellow
- **Auto-refresh** — dashboard silently re-fetches data every 30 minutes
- **Mobile responsive** — works on all screen sizes

## Architecture

This project is split across two repos:

| Repo | Visibility | Contents |
|------|-----------|----------|
| [`insider-radar`](https://github.com/shaheedhamid/insider-radar) (this repo) | Public | `index.html` dashboard + `data/` JSON files served by GitHub Pages |
| `insider-radar-backend` | Private | Python scraper + GitHub Actions workflow |

The backend workflow runs every 2 hours, executes the scraper, and pushes updated JSON files to `data/` in this repo using a scoped `PUBLIC_REPO_TOKEN` secret.

## Project Structure

```
insider-radar/          ← this repo (public)
├── index.html          # Dashboard served by GitHub Pages
└── data/
    ├── latest.json     # Last 1000 days of trades (updated every 2 hours)
    └── history.csv     # Full trade history (append-only)

insider-radar-backend/  ← separate private repo
├── scraper/
│   ├── scrape.py       # Python scraper (SEC Form 4)
│   └── requirements.txt
└── .github/
    └── workflows/
        └── scrape.yml  # Runs scraper and pushes data/ here
```

## Setup

### 1. Enable GitHub Pages on this repo

1. Go to **Settings → Pages**.
2. Under **Source**, select **Deploy from a branch**.
3. Set the branch to `main` and folder to `/ (root)`.
4. Click **Save**.

Your dashboard will be live at `https://<your-username>.github.io/insider-radar/` within 1–2 minutes.

### 2. Set up the private backend repo

See the `insider-radar-backend` repo for full instructions. The short version:

1. Create a private GitHub repo named `insider-radar-backend`.
2. Add `scraper/` and `.github/workflows/scrape.yml`.
3. Create a fine-grained Personal Access Token with **Contents: Read and write** scoped to *this* repo only.
4. Add it as a secret named `PUBLIC_REPO_TOKEN` in the backend repo.
5. Trigger the workflow manually once to confirm the first push works.

### 3. Local preview

Serve the frontend locally with any static file server:

```bash
python -m http.server 8000
# Open http://localhost:8000
```

`data/latest.json` is already committed, so the dashboard loads with real data immediately.

## Data Files

| File | Description |
|------|-------------|
| `data/latest.json` | Trades from the last 1000 days. Overwritten on every scraper run. |
| `data/history.csv` | Append-only CSV log of all trades ever seen. |

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

A **cluster buy** is flagged when **2 or more different insiders** purchase shares of the **same ticker within a 14-day window**. Cluster trades are displayed with a 🔥 **Cluster** badge in the dashboard.

## Disclaimer

This dashboard is for **informational and educational purposes only**. Data is sourced from publicly disclosed SEC Form 4 filings. Nothing here constitutes financial advice.

## License

MIT
