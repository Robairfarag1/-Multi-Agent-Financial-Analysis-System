#!/usr/bin/env python3
import os, pandas as pd

HERE = os.path.dirname(__file__)
MONTHLY = os.path.abspath(os.path.join(HERE, "..", "data_cache", "Monthly"))

TICKERS = ["AAPL","MSFT","GOOGL","NVDA","META","AMZN"]

def read_csv(name):
    p = os.path.join(MONTHLY, name)
    if not os.path.exists(p): return None
    return pd.read_csv(p, index_col=0, parse_dates=True)

def main():
    frames = []

    # benchmarks & macro
    for name in ["ixic_rets.csv", "xlk_rets.csv", "ai_basket_rets.csv", "macro_monthly.csv"]:
        df = read_csv(name)
        if df is not None:
            df.index = pd.to_datetime(df.index, errors="coerce").to_period("M").to_timestamp("M")
            frames.append(df)

    # per-ticker features (we’ll take *_ret if present; otherwise skip)
    for t in TICKERS:
        df = read_csv(f"{t}_features_enriched.csv")
        if df is None: continue
        df.index = pd.to_datetime(df.index, errors="coerce").to_period("M").to_timestamp("M")
        keep = [c for c in df.columns if c.endswith("_ret")]  # e.g. AAPL_ret
        # if no explicit *_ret, try Close -> pct_change
        if not keep:
            # try to infer a price column that looks like the ticker
            price_candidates = [c for c in df.columns if t in c.upper() or c.upper()==t]
            if price_candidates:
                s = pd.to_numeric(df[price_candidates[0]], errors="coerce")
                df[f"{t}_ret"] = s.pct_change()
                keep = [f"{t}_ret"]
        frames.append(df[keep]) if keep else None

    if not frames:
        print("[fatal] Found no usable frames. Aborting.")
        return

    combined = pd.concat(frames, axis=1).sort_index()
    # drop all-empty rows
    combined = combined.dropna(how="all")
    out = os.path.join(MONTHLY, "tech_features_combined.csv")
    combined.to_csv(out)
    print("Saved →", out)
    print("Columns:", list(combined.columns)[:20])

if __name__ == "__main__":
    main()

