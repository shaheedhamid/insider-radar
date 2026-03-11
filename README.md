# InsiderEdgePro — SEC Insider Trading Tracker | Congressional Trades & Insider Buying Alerts

**Live dashboard:** https://insideredgepro.github.io

Real-time tracker for SEC Form 4 insider purchases, **congressional stock trades**, and Canadian SEDI filings. Get Discord alerts for US insider buys, Canada insider buys, and politician stock trades — before the market reacts.

---

## What Is InsiderEdge?

InsiderEdgePro is a **free insider trading tracker** that monitors SEC Form 4 open-market purchases, **congressional stock trades (STOCK Act disclosures)**, and Canadian SEDI filings in real time. It detects **cluster buys** — when multiple insiders at the same company buy simultaneously — one of the strongest bullish signals in quantitative finance. Discord alerts cover US insider buys, Canadian insider buys, and politician trades.

---

## Features

- **Real-time SEC Form 4 data** — auto-refreshes every 30 minutes
- **Congressional trade alerts** — Discord notifications for politician stock buys (STOCK Act)
- **Cluster buy detection** — flags stocks where 2+ insiders buy at once
- **Role filters** — filter by CEO, CFO, Director, Chairman, VP, SVP, EVP
- **Value filters** — $100K+, $500K+, $1M+, $5M+, $10M+ trade thresholds
- **Period filters** — 1D, 7D, 30D, 90D, 1Y, All-time views
- **Performance tracker** — measures stock returns since each insider filing date
- **Canadian market** — tracks TSX & TSX-V insider purchases via SEDI
- **Discord alerts** — real-time notifications for US insiders, Canada insiders & congressional trades

---

## Frequently Asked Questions

**What are insiders buying right now?**
InsiderEdgePro tracks every SEC Form 4 open-market purchase filed today, showing exactly which stocks CEOs, CFOs, Directors, and other corporate insiders are buying with their own money. The dashboard refreshes every 30 minutes and highlights unusual insider buying activity with our cluster buy signal — when two or more insiders at the same company purchase simultaneously.

**Is insider buying a bullish signal?**
Academic research consistently shows that open-market insider purchases are among the most reliable leading indicators of stock outperformance. When an executive buys shares with personal capital rather than receiving options or RSUs, it reflects genuine conviction. Cluster buys — where a CEO, CFO, and Director all purchase in the same week — amplify this smart money signal significantly, more so than any single insider purchase alone.

**What is a cluster buy signal?**
A cluster buy occurs when two or more corporate insiders at the same company file SEC Form 4 purchases within a short window. This is one of the highest-conviction signals in quantitative finance. InsiderEdgePro automatically detects and flags cluster buy signals in real time, so you can spot unusual insider buying activity the moment it happens — before it shows up in 13F filings months later.

**How do I track congressional stock trades?**
Under the STOCK Act (Stop Trading on Congressional Knowledge Act), US Senators and Representatives must disclose personal stock trades within 45 days. InsiderEdgePro monitors these STOCK Act filings and sends real-time Discord alerts for every congressional trade. Our Congress stock market tracker surfaces Nancy Pelosi stock trades, Senate trades, and House of Representatives disclosures — a free politician portfolio tracker for every investor.

**Do politician trades beat the market?**
Studies have found that congressional stock trades have historically outperformed broad market indexes, particularly trades made near major legislation or regulatory announcements. Whether you want to follow Warren Buffett trades via 13F filings or track Nancy Pelosi and congressional stock picks via STOCK Act disclosures, InsiderEdgePro surfaces smart money moves the moment they are disclosed publicly — no subscription required.

**How do I read SEC Form 4 filings?**
A Form 4 is filed with the SEC whenever a corporate insider — director, officer, or 10%+ shareholder — buys or sells company shares. The most important field is Transaction Type: "P" means an open-market purchase (the most bullish signal), while "S" means a sale. InsiderEdgePro parses every Form 4 on SEC EDGAR and presents the data in a clean, filterable dashboard, saving you from manually reading raw filings. We surface the trade date, price paid, total value, and insider title so you can immediately assess signal quality.

---

## Pages

| Page | URL | Description |
|---|---|---|
| US Dashboard | `/` | Real-time SEC Form 4 insider purchases — NYSE, NASDAQ, OTC |
| Canada Dashboard | `/canada.html` | Real-time SEDI insider purchases — TSX & TSX-V |
| Performance | `/performance.html` | Stock price returns since each insider filing date |

---

## Data Sources

- **US Insiders:** [SEC EDGAR Form 4](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=4) — publicly available, updated multiple times daily
- **Canada:** [SEDI (System for Electronic Disclosure by Insiders)](https://www.sedi.ca) — Canadian equivalent of SEC Form 4
- **Congressional trades:** STOCK Act (Stop Trading on Congressional Knowledge Act) — mandatory disclosure of trades by US Senators and Representatives

---

## Why Insider Buying Matters

Academic research consistently shows that **open-market insider purchases** — where executives buy shares with their own money — are among the most reliable leading indicators of stock outperformance. Unlike options grants or RSUs, open-market purchases represent true conviction.

**Cluster buys amplify the signal.** When a CEO, CFO, and two Directors all purchase in the same week, the probability of a meaningful move increases significantly.

InsiderEdgePro makes this data accessible to every investor — not just hedge funds.

---

## Discord Alerts Community

Join **[discord.gg/k6Q5rtEPe](https://discord.gg/k6Q5rtEPe)** for real-time alerts across three channels:

- 🇺🇸 **US Insider Alerts** — SEC Form 4 open-market purchases as they are filed
- 🇨🇦 **Canada Insider Alerts** — SEDI filings for TSX & TSX-V insiders
- 🏛️ **Congressional Trade Alerts** — STOCK Act disclosures when politicians buy or sell stocks

Free to join. No subscription required.

---

*Data sourced from public SEC EDGAR and SEDI filings. For informational purposes only. Not financial advice.*
