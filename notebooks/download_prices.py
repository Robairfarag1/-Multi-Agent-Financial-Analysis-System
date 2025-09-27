import sys, os, argparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data.yahoo import get_multiple_prices

def main():
    p = argparse.ArgumentParser(description="Download OHLCV CSVs to data_cache/")
    p.add_argument("--tickers", type=str, default="AAPL,MSFT,NVDA,META",
                   help="Comma-separated tickers, e.g. AAPL,MSFT")
    p.add_argument("--period", type=str, default="1y",
                   help="e.g. 6mo, 1y, 5y, max")
    p.add_argument("--interval", type=str, default="1d",
                   help="e.g. 1d, 1wk, 1mo")
    args = p.parse_args()

    os.makedirs("data_cache", exist_ok=True)
    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    data = get_multiple_prices(tickers=tickers, period=args.period, interval=args.interval)

    for t, df in data.items():
        path = f"data_cache/{t}_prices.csv"
        df.to_csv(path, index=False)
        print(f"✅ saved {t} -> {path}")

if __name__ == "__main__":
    main()
