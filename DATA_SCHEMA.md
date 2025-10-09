# Data Schema

This document describes the structure and location of datasets used in the **Multi-Agent Financial Analysis System**.

---

## 📊 Stock Prices

**File:** `data_cache/tech_prices_merged.csv`  
**Description:** Daily OHLCV history for selected technology tickers (AAPL, MSFT, NVDA, META).  
**Columns:**
- `date` — trading date (timezone-aware, daily frequency)
- `ticker` — stock symbol
- `open` — opening price
- `high` — daily high price
- `low` — daily low price
- `close` — adjusted closing price
- `volume` — trading volume

---

## 🏦 FRED Indicators

Downloaded from [FRED API](https://fred.stlouisfed.org/) and cached locally.

Files saved under `data_cache/`:

- **`fred_FEDFUNDS.csv`**  
  *Federal Funds Rate (FEDFUNDS)* — Effective overnight rate, monthly.

- **`fred_DGS10.csv`**  
  *10-Year Treasury Constant Maturity Yield (DGS10)* — Benchmark yield, daily.

- **`fred_CPIAUCSL.csv`**  
  *Consumer Price Index for All Urban Consumers (CPIAUCSL)* — Inflation index, monthly.

- **`fred_UNRATE.csv`**  
  *Civilian Unemployment Rate (UNRATE)* — Unemployment percentage, monthly.

**Columns (for all FRED series):**
- `date` — observation date
- `value` — numeric value of the series

---

## 📁 Location

All datasets are cached under `data_cache/` and tracked by `.gitkeep`.  
`.env` is used to provide the `FRED_API_KEY` but is ignored in version control.

