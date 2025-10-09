#!/usr/bin/env python3
import os, sys
import pandas as pd
import numpy as np

THIS_DIR = os.path.dirname(__file__)
MONTHLY_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "data_cache", "Monthly"))
COMBINED_CSV = os.path.join(MONTHLY_DIR, "tech_features_combined.csv")

TICKERS = ["AAPL","MSFT","GOOGL","NVDA","META","AMZN"]

def read_csv_maybe_index(p: str) -> pd.DataFrame:
    if not os.path.exists(p):
        print(f"[fatal] Missing file: {p}")
        sys.exit(1)
    df = pd.read_csv(p, index_col=0, parse_dates=True)
    # ensure monthly index if parse succeeded; otherwise leave as is
    if df.index.dtype.kind in ("M", "m") or np.issubdtype(df.index.dtype, np.datetime64):
        # force month-end
        df.index = pd.to_datetime(df.index, errors="coerce").to_period("M").to_timestamp("M")
        df = df[~df.index.duplicated(keep="last")].sort_index()
    return df

def ensure_returns(df: pd.DataFrame) -> pd.DataFrame:
    have = [c for c in df.columns if c.endswith("_ret")]
    if have:
        return df

    # try to find price columns that look like tickers
    price_cols = []
    for t in TICKERS:
        # exact match or case-insensitive contains
        hits = [c for c in df.columns if (c.upper()==t) or (t in c.upper())]
        # pick the "cleanest" one if multiple
        if hits:
            # prefer exact match, else shortest name
            best = sorted(hits, key=lambda x: (x.upper()!=t, len(x)))[0]
            price_cols.append((t, best))

    if not price_cols:
        print("[fatal] No *_ret columns and no obvious price columns found.")
        print("Available columns:", list(df.columns)[:10], "...")
        sys.exit(2)

    out = df.copy()
    for t, col in price_cols:
        s = pd.to_numeric(out[col], errors="coerce")
        if s.notna().sum() < 3:
            continue
        ret = s.pct_change(fill_method=None)
        out[f"{t}_ret"] = ret

    made = [c for c in out.columns if c.endswith("_ret")]
    if not made:
        print("[fatal] Could not construct returns from candidate price columns.")
        print("Candidates tried:", price_cols)
        sys.exit(3)

    return out

def main():
    df = read_csv_maybe_index(COMBINED_CSV)
    df = ensure_returns(df)

    # quick sanity print
    ret_cols = [c for c in df.columns if c.endswith("_ret")]
    print("Return columns detected:", ret_cols)

    # minimal demo: compute correlation matrix of returns and save
    corr = df[ret_cols].corr(min_periods=6)
    out_corr = os.path.join(MONTHLY_DIR, "ret_corr.csv")
    corr.to_csv(out_corr)
    print("Saved →", out_corr)

    # tiny “model”: average of all returns as a factor, show last row
    df["avg_ret"] = df[ret_cols].mean(axis=1, skipna=True)
    print("\nLast few rows of avg_ret:")
    print(df["avg_ret"].tail(5).to_string())

if __name__ == "__main__":
    main()

