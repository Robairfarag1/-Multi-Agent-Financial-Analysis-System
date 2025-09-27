import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.yahoo import get_multiple_prices

os.makedirs("data_cache", exist_ok=True)

tickers = ["AAPL", "MSFT", "NVDA", "META"]
data = get_multiple_prices(tickers, period="1y", interval="1d")

for t, df in data.items():
    path = f"data_cache/{t}_prices.csv"
    df.to_csv(path, index=False)
    print(f"✅ saved {t} -> {path}")
