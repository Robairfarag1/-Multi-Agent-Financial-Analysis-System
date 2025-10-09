#!/usr/bin/env python3
"""
Tech Monthly — STABLE
- Macro from FRED (needs FRED_API_KEY)
- Prices from Polygon aggregates (preferred) with local caching; fallback to yfinance if no POLYGON_API_KEY
- Uses QQQ (ETF) as NASDAQ-100 proxy to avoid Yahoo '^' ticker issues
- News & earnings DISABLED by default; enable via .env flags:
    ENABLE_NEWS=1
    ENABLE_EARNINGS=1
- Outputs to ../data_cache/Monthly
- Raw price cache to ../data_cache/raw (Parquet)
"""

import os, time, datetime as dt
from typing import Tuple, List, Dict, Any
import pandas as pd, numpy as np, requests

# ---------- optional deps ----------
try:
    import yfinance as yf
except Exception as e:
    raise SystemExit("Install deps:\n  python3 -m pip install --user yfinance pandas numpy requests python-dotenv pyarrow statsmodels") from e

try:
    import statsmodels.api as sm
    _SM_OK = True
except Exception:
    _SM_OK = False

# ---------- env loading ----------
def load_env():
    loaded = []
    try:
        from dotenv import load_dotenv, find_dotenv
        here = os.path.dirname(__file__)
        for p in [os.path.join(here, ".env"),
                  os.path.abspath(os.path.join(here, "..", ".env")),
                  find_dotenv(usecwd=True)]:
            if p and os.path.isfile(p) and load_dotenv(p, override=True):
                loaded.append(p)
    except Exception:
        pass
    if loaded: print("[info] Loaded .env from:", " | ".join(dict.fromkeys(loaded)))

load_env()

FRED_KEY    = os.getenv("FRED_API_KEY", "")
POLY_KEY    = os.getenv("POLYGON_API_KEY", "")
FINN_KEY    = os.getenv("FINNHUB_API_KEY", "")
ENABLE_NEWS = os.getenv("ENABLE_NEWS", "0") == "1"
ENABLE_EARN = os.getenv("ENABLE_EARNINGS", "0") == "1"
FORCE_REF   = os.getenv("FORCE_REFRESH", "0") == "1"
def _mask(s): return "<missing>" if not s else s[:4]+"..."+s[-4:]
print("Keys:", {"FRED": bool(FRED_KEY), "POLYGON": bool(POLY_KEY), "FINNHUB": bool(FINN_KEY)})

# ---------- paths ----------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR   = os.path.join(REPO_ROOT, "data_cache", "Monthly")
RAW_DIR   = os.path.join(REPO_ROOT, "data_cache", "raw")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

# ---------- config ----------
TECH = ["AAPL","MSFT","GOOGL","NVDA","META","AMZN"]
AI_BASKET = ["NVDA","META","MSFT","GOOGL","AMD","AVGO"]
# Use ETF proxies for stability (Polygon + Yahoo-safe):
IXIC_PROXY = "QQQ"   # NASDAQ-100 proxy instead of "^IXIC"
XLK_PROXY  = "XLK"

START = "2018-01-01"
END   = dt.date.today().isoformat()
LAGS  = [1,3,6]

# ---------- helpers ----------
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
POLY_BASE = "https://api.polygon.io"

def _get_json(url, params=None, tries=3, backoff=1.0):
    last=None
    for i in range(tries):
        try:
            r = requests.get(url, params=params, timeout=30)
            if r.status_code==429:
                time.sleep(backoff*(i+1))
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last=e; time.sleep(backoff*(i+1))
    print(f"[warn] GET fail {url} | {type(last).__name__}: {last}")
    return None

def _to_csv(df, path):
    df.to_csv(path); print("Saved →", path)

def make_lags(df, cols, lags=(1,3,6)):
    out=df.copy()
    for c in cols:
        if c in out:
            for L in lags: out[f"{c}_lag{L}"]=out[c].shift(L)
    return out

def diag(df, name):
    print(f"\n[Diag] {name}: shape={df.shape}, index=({df.index.min()}, {df.index.max()})")
    print("[Diag] Top NaN%:\n", df.isna().mean().sort_values(ascending=False).head(8).to_string())

# ---------- macro (FRED) ----------
def fred_series_monthly(series_id, start, end, how="mean") -> pd.Series:
    if not FRED_KEY: raise SystemExit("FRED_API_KEY missing.")
    params=dict(series_id=series_id, api_key=FRED_KEY, file_type="json",
                observation_start=start, observation_end=end)
    js=_get_json(FRED_BASE, params)
    obs=(js or {}).get("observations", [])
    if not obs: return pd.Series(dtype=float)
    df=pd.DataFrame(obs)
    df["date"]=pd.to_datetime(df["date"])
    df["value"]=pd.to_numeric(df["value"], errors="coerce")
    s=df.set_index("date")["value"].astype(float)
    return s.resample("ME").last() if how=="last" else s.resample("ME").mean()

def macro_block(start, end):
    m=pd.DataFrame({
        "fed_funds_rate":    fred_series_monthly("FEDFUNDS", start, end),
        "cpi_index":         fred_series_monthly("CPIAUCSL", start, end),
        "us10y":             fred_series_monthly("DGS10", start, end),
        "unemployment_rate": fred_series_monthly("UNRATE", start, end),
    }).sort_index()
    m["inflation_yoy"]=m["cpi_index"].pct_change(12, fill_method=None)*100
    m["us10y_chg"]=m["us10y"].diff(1)
    m["fedfunds_chg"]=m["fed_funds_rate"].diff(1)
    m["unrate_chg"]=m["unemployment_rate"].diff(1)
    diag(m, "macro monthly")
    _to_csv(m, os.path.join(OUT_DIR,"macro_monthly.csv"))
    return m

# ---------- prices (Polygon preferred) ----------
def polygon_agg_daily(ticker, start, end) -> pd.DataFrame:
    """Fetch daily aggregates via Polygon; return DataFrame with 'close' col named ticker."""
    if not POLY_KEY:
        return pd.DataFrame()
    url = f"{POLY_BASE}/v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}"
    params = {"adjusted":"true", "sort":"asc", "limit":50000, "apiKey": POLY_KEY}
    js=_get_json(url, params)
    results=(js or {}).get("results", [])
    if not results: return pd.DataFrame()
    df=pd.DataFrame(results)
    if "t" not in df or "c" not in df: return pd.DataFrame()
    df["date"]=pd.to_datetime(df["t"], unit="ms")
    df=df.set_index("date").sort_index()
    return df[["c"]].rename(columns={"c":ticker})

def load_price_cached(ticker, start, end) -> pd.Series:
    """Return monthly close Series for ticker (Polygon→cache→yfinance)."""
    cache_path=os.path.join(RAW_DIR, f"{ticker}_daily.parquet")
    df=None

    # Try Polygon + write cache
    if POLY_KEY:
        if not os.path.exists(cache_path) or FORCE_REF:
            df=polygon_agg_daily(ticker, start, end)
            if not df.empty:
                try: df.to_parquet(cache_path)
                except Exception: pass
        if df is None and os.path.exists(cache_path):
            try: df=pd.read_parquet(cache_path)
            except Exception: df=None
    # Fallback: yfinance (single ticker to be gentle)
    if df is None or df.empty:
        data=yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
        if data is not None and "Close" in data and not data.empty:
            df=data["Close"].to_frame(name=ticker)
            try: df.to_parquet(cache_path)
            except Exception: pass

    if df is None or df.empty: return pd.Series(dtype=float)
    m=df.resample("ME").last()[ticker]
    return m

def monthly_returns_for(targets, start, end) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if isinstance(targets, (list, tuple, set)):
        cols=[]
        for t in targets:
            s=load_price_cached(t, start, end)
            if not s.empty: cols.append(s.to_frame(name=t))
            time.sleep(0.15)  # gentle
        if not cols: return pd.DataFrame(), pd.DataFrame()
        close=pd.concat(cols, axis=1).sort_index()
    else:
        s=load_price_cached(targets, start, end)
        if s.empty: return pd.DataFrame(), pd.DataFrame()
        close=s.to_frame(name=targets)
    rets=close.pct_change(fill_method=None)
    return close, rets

# ---------- features ----------
def build_features(ticker, macro, ixic_rets, xlk_rets, ai_ret_eqw) -> pd.DataFrame:
    _, rets = monthly_returns_for(ticker, START, END)
    if rets.empty:
        frame=pd.DataFrame(index=macro.index, data={f"{ticker}_ret": np.nan})
    else:
        frame=rets.rename(columns={rets.columns[0]: f"{ticker}_ret"})
    frame=frame.join(ixic_rets, how="left").join(xlk_rets, how="left").join(ai_ret_eqw, how="left")

    base=["inflation_yoy","us10y","us10y_chg","fed_funds_rate","fedfunds_chg","unemployment_rate","unrate_chg"]
    frame=frame.join(make_lags(macro, base, lags=LAGS), how="left")
    if len(frame)>max(LAGS): frame=frame.iloc[max(LAGS):]
    return frame

def fit_ols_safe(df: pd.DataFrame, target_col: str, min_rows=12):
    if not _SM_OK:
        print("[info] statsmodels not installed – skipping OLS.")
        return
    aligned=df.dropna()
    if len(aligned)<min_rows:
        print(f"[info] Not enough rows after dropna for {target_col}: {len(aligned)} (need >= {min_rows}).")
        return
    y=aligned[target_col]; X=sm.add_constant(aligned.drop(columns=[target_col]), has_constant="add")
    m=sm.OLS(y,X).fit()
    print(m.summary())

# ---------- main ----------
def main():
    macro=macro_block(START, END)

    # Benchmarks using stable tickers
    _, qqq = monthly_returns_for(IXIC_PROXY, START, END); qqq = qqq.rename(columns={qqq.columns[0]:"ixic_ret"}) if not qqq.empty else pd.DataFrame(index=macro.index, data={"ixic_ret":np.nan})
    _, xlk = monthly_returns_for(XLK_PROXY,  START, END); xlk = xlk.rename(columns={xlk.columns[0]:"xlk_ret"})   if not xlk.empty else pd.DataFrame(index=macro.index, data={"xlk_ret":np.nan})
    _, ai  = monthly_returns_for(AI_BASKET,  START, END)
    ai_eqw = ai.mean(axis=1).to_frame(name="ai_basket_ret") if not ai.empty else pd.DataFrame(index=macro.index, data={"ai_basket_ret":np.nan})

    _to_csv(qqq, os.path.join(OUT_DIR,"ixic_rets.csv"))
    _to_csv(xlk, os.path.join(OUT_DIR,"xlk_rets.csv"))
    _to_csv(ai_eqw, os.path.join(OUT_DIR,"ai_basket_rets.csv"))

    # Per-ticker features
    all_feat={}
    for t in TECH:
        print(f"Features for {t} ...")
        ft=build_features(t, macro, qqq, xlk, ai_eqw)
        diag(ft, f"{t} features")
        all_feat[t]=ft
        _to_csv(ft, os.path.join(OUT_DIR, f"{t}_features_enriched.csv"))

    combined=pd.concat(all_feat, axis=1)
    _to_csv(combined, os.path.join(OUT_DIR,"tech_features_combined.csv"))

    # Optional OLS
    for t in TECH:
        print(f"\n=== {t} OLS (enriched) ===")
        target=f"{t}_ret"
        if target in all_feat[t]:
            na=all_feat[t].drop(columns=[target]).isna().mean()
            keep = na.sort_values().index[:20].tolist()
            fit_ols_safe(all_feat[t][[target]+keep], target)

    print("\nDone. CSVs in:", OUT_DIR)
    print("Raw price cache in:", RAW_DIR)

if __name__=="__main__":
    main()
