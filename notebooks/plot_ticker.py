import sys, os, argparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.yahoo import get_stock_prices
import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser(description="Plot a ticker's closing price and save PNG")
    p.add_argument("--ticker", type=str, required=True, help="e.g. AAPL")
    p.add_argument("--period", type=str, default="1y", help="e.g. 6mo, 1y, 5y, max")
    p.add_argument("--interval", type=str, default="1d", help="e.g. 1d, 1wk, 1mo")
    args = p.parse_args()

    df = get_stock_prices(args.ticker.upper(), period=args.period, interval=args.interval)

    plt.figure(figsize=(10,5))
    plt.plot(df["date"], df["close"], label=f"{args.ticker.upper()} Close")
    plt.title(f"{args.ticker.upper()} Closing Price ({args.period})")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    os.makedirs("notebooks", exist_ok=True)
    out = f"notebooks/{args.ticker.upper()}_{args.period}_close.png"
    plt.savefig(out)
    print(f"✅ Plot saved to {out}")

if __name__ == "__main__":
    main()
