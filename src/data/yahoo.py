import yfinance as yf
import pandas as pd

def get_stock_prices(ticker="AAPL", period="1y", interval="1d") -> pd.DataFrame:
    """
    Fetch daily OHLCV history for a given ticker.
    Columns: date, open, high, low, close, volume
    """
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    df = df.reset_index().rename(columns=str.lower)
    return df[["date", "open", "high", "low", "close", "volume"]]


def get_multiple_prices(tickers=None, period="1y", interval="1d"):
    """
    Fetch OHLCV history for multiple tickers.
    Returns a dict {ticker: DataFrame}.
    """
    tickers = tickers or ["AAPL", "MSFT", "NVDA", "META"]
    out = {}
    for t in tickers:
        try:
            out[t] = get_stock_prices(t, period=period, interval=interval)
        except Exception as e:
            print(f"⚠️ Failed to fetch {t}: {e}")
    return out

