# Multi-Agent Financial Analysis System

Group project for building a multi-agent financial analysis system.

## Structure
- `src/data/` → data acquisition and preprocessing
- `notebooks/` → Jupyter notebooks + sanity plots
- `data_cache/` → local cache (ignored in git)

## Setup
```bash
pip install -r requirements.txt
## Usage

### Download Tech Stock Prices
```bash
python3 notebooks/sanity_plot.py
python3 notebooks/plot_ticker.py --ticker NVDA --period 1y --interval 1d

