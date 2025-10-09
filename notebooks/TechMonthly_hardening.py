#!/usr/bin/env python3
"""
Tech Monthly — Polygon-Only, Rock-Stable

- Macro from FRED (requires FRED_API_KEY)
- Prices ONLY from Polygon v2 aggregates (requires POLYGON_API_KEY with aggregates access)
- No yfinance, no news, no earnings → minimal moving parts
- Month-end alignment for joins with FRED
- Caches monthly closes per ticker to ../data_cache/raw/*_poly_monthly.parquet
"""

import os, time, datetime as dt
from typing import Dict, Tuple, List
import pandas as pd, numpy as np, requests

# -------- env loading --------
def load_env():
    loaded=[]
    try:
        from dotenv import load_dotenv, find_dotenv
        here = os.path.dirname(__file__)
        for p in [os.path.join(here,".env"),
                  os.path.abspath(os.path.join(here,"..",".env")),
                  find_dotenv(usecwd=True)]:
            if p and os.path.isfile(p) and load_dotenv(p, override=True):
                loaded.append(p)
    except Exception:
        pass
    if loaded:
        print("[info] Loaded .env from:", " | ".join(dict.fromkeys(loaded)))

load_env()

FRED_KEY  = os.getenv("FRED_API_KEY","")
POLY_KEY  = os.getenv("POLYGON_API_KEY","")

print("Keys:", {"FRED": bool(FRED_KEY), "POLYGON": bool(POLY_KEY)})

# -------- paths & config --------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR = os.path.join(REPO_ROOT, "data_cache", "Monthly")
RAW_DIR = os.path.join(REPO_ROOT, "data_cache", "raw")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

TECH = ["AAPL","MSFT","GOOGL","NVDA","META","AMZN"]
AI_BASKET = ["NVDA","META","MSFT","GOOGL","AMD","AVGO"]
IXIC_PROXY = "QQQ"  # NASDAQ-100 proxy
XLK_PROXY  = "XLK"

START = "2018-01-01"
END   = dt.date.today().isoformat()
LAGS  = [1,3,6]

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
POLY_BASE = "https://api.polygon.io"

# -------- utils --------
def _get_json(url, params=None, tries=3, backoff=1.5):
    last=None
    for i in range(tries):
        try:
            r=requests.get(url, params=params, timeout=30)
            if r.status_code==429:
                time.sleep(backoff*(i+1))
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last=e; time.sleep(backoff*(i+1))
    print(f"[warn] GET fail {url} | {type(last).__name__}: {last}")
    try: print("  ↳ response:", r.text[:300])
    except Exception: pass
    return None

def _to_csv(df: pd.DataFrame, path: str):
    df.to_csv(path); print("Saved →", path)

def make_lags(df: pd.DataFrame, cols: List[str], lags=(1,3,6)) -> pd.DataFrame:
    out=df.copy()
    for c in cols:
        if c in out:
            for L in lags:
                out[f"{c}_lag{L}"]=out[c].shift(L)
    return out

def diag(df: pd.DataFrame, name: str):
    print(f"\n[Diag] {name}: shape={df.shape}, index=({df.index.min()}, {df.index.max()})")
    print("[Diag] Top NaN%:\n", df.isna().mean().sort_values(ascending=False).head(8).to_string())

# -------- FRED macro --------
def fred_series_monthly(series_id: str, start: str, end: str, how="mean") -> pd.Series:
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

def macro_block(start, end) -> pd.DataFrame:
    m=pd.DataFrame({
        "fed_funds_rate":    fred_series_monthly("FEDFUNDS", start, end),
        "cpi_index":         fred_series_monthly("CPIAUCSL", start, end),
        "us10y":             fred_series_monthly("DGS10", start, end),
        "unemployment_rate": fred_series_monthly("UNRATE", start, end),
    }).sort_index()
    # month-end alignment; avoid future warning with fill_method=None
    m["inflation_yoy"]=m["cpi_index"].pct_change(12, fill_method=None)*100
    m["us10y_chg"]=m["us10y"].diff(1)
    m["fedfunds_chg"]=m["fed_funds_rate"].diff(1)
    m["unrate_chg"]=m["unemployment_rate"].diff(1)
    diag(m, "macro monthly")
    _to_csv(m, os.path.join(OUT_DIR,"macro_monthly.csv"))
    return m

# -------- Polygon validation --------
def polygon_validate() -> Tuple[bool,str]:
    if not POLY_KEY:
        return False, "No POLYGON_API_KEY set."
    url=f"{POLY_BASE}/v3/reference/tickers"
    params={"active":"true","limit":1,"apiKey":POLY_KEY}
    js=_get_json(url, params, tries=2, backoff=1.0)
    if not js:
        return False, "No response (network or service)."
    if str(js.get("status","")).upper()=="OK":
        return True, "OK"
    return False, js.get("error") or js.get("message") or "Unknown error/plan"

# -------- Polygon prices (daily → month-end) with caching --------
def polygon_agg_daily_to_monthly(ticker: str, start: str, end: str) -> pd.Series:
    cache = os.path.join(RAW_DIR, f"{ticker}_poly_monthly.parquet")
    if os.path.exists(cache):
        try:
            s = pd.read_parquet(cache)
            if isinstance(s, pd.DataFrame) and ticker in s.columns:
                s = s[ticker]
            s.index = pd.to_datetime(s.index)
            # ensure month-end index (already saved as month-end)
            return pd.Series(s, name=ticker).sort_index()
        except Exception:
            pass

    url = f"{POLY_BASE}/v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}"
    params = {"adjusted":"true", "sort":"asc", "limit":50000, "apiKey": POLY_KEY}
    js=_get_json(url, params, tries=4, backoff=2.0)
    results=(js or {}).get("results", [])
    if not results:
        return pd.Series(dtype=float, name=ticker)
    df=pd.DataFrame(results)
    if "t" not in df or "c" not in df:
        return pd.Series(dtype=float, name=ticker)
    df["date"]=pd.to_datetime(df["t"], unit="ms")
    df=df.set_index("date").sort_index()
    s = df["c"].rename(ticker)
    # convert to month-end
    s.index = s.index.to_period("M").to_timestamp("M")
    s = s.groupby(level=0).last()
    # cache
    try: s.to_frame(name=ticker).to_parquet(cache)
    except Exception: pass
    return s

def monthly_close_frame_polygon(targets: List[str]) -> pd.DataFrame:
    cols=[]
    for i, t in enumerate(targets):
        s = polygon_agg_daily_to_monthly(t, START, END)
        if not s.empty:
            cols.append(s.to_frame(name=t))
        time.sleep(0.15)  # gentle pacing
    if not cols:
        return pd.DataFrame()
    return pd.concat(cols, axis=1).sort_index()

# -------- Features --------
def build_features(ticker: str, macro: pd.DataFrame,
                   ixic_rets: pd.DataFrame, xlk_rets: pd.DataFrame, ai_ret_eqw: pd.DataFrame) -> pd.DataFrame:
    # per-ticker returns (from polygon, already month-end)
    s = polygon_agg_daily_to_monthly(ticker, START, END)
    if s.empty:
        frame=pd.DataFrame(index=macro.index, data={f"{ticker}_ret": np.nan})
    else:
        rets = s.pct_change(fill_method=None).to_frame(name=f"{ticker}_ret")
        frame=rets
    # join benchmarks (already month-end & saved)
    frame=frame.join(ixic_rets, how="left").join(xlk_rets, how="left").join(ai_ret_eqw, how="left")
    # macro & lags
    base=["inflation_yoy","us10y","us10y_chg","fed_funds_rate","fedfunds_chg","unemployment_rate","unrate_chg"]
    frame=frame.join(make_lags(macro, base, lags=LAGS), how="left")
    if len(frame)>max(LAGS): frame=frame.iloc[max(LAGS):]
    return frame

# -------- OLS (optional) --------
try:
    import statsmodels.api as sm
    _SM_OK = True
except Exception:
    _SM_OK = False

def fit_ols_safe(df: pd.DataFrame, target_col: str, min_rows=24):
    if not _SM_OK:
        print("[info] statsmodels not installed – skipping OLS.")
        return
    aligned=df.dropna()
    k = aligned.shape[1]  # includes target
    resid_df = aligned.shape[0] - k  # lower bound; const adds +1 later
    if len(aligned) < min_rows or resid_df <= 1:
        print(f"[info] Not enough rows/df for {target_col}: n={len(aligned)}, resid_df≈{resid_df}. Skipping.")
        return
    y=aligned[target_col]; X=sm.add_constant(aligned.drop(columns=[target_col]), has_constant="add")
    m=sm.OLS(y,X).fit()
    print(m.summary())

# -------- main --------
def main():
    ok,msg = polygon_validate()
    if not ok:
        print(f"[fatal] Polygon aggregates unavailable → {msg}")
        print("Check your POLYGON_API_KEY and plan. Prices require aggregate access.")
        return

    macro = macro_block(START, END)

    # Benchmarks via Polygon
    bench = monthly_close_frame_polygon([IXIC_PROXY, XLK_PROXY])
    if bench.empty:
        print("[fatal] Could not fetch benchmark prices (Polygon).")
        return
    qqq = bench[[IXIC_PROXY]].pct_change(fill_method=None).rename(columns={IXIC_PROXY: "ixic_ret"})
    xlk = bench[[XLK_PROXY]].pct_change(fill_method=None).rename(columns={XLK_PROXY: "xlk_ret"})

    # AI basket (Polygon)
    ai_close = monthly_close_frame_polygon(AI_BASKET)
    if ai_close.empty:
        ai_eqw = pd.DataFrame(index=macro.index, data={"ai_basket_ret": np.nan})
    else:
        ai_eqw = ai_close.pct_change(fill_method=None).mean(axis=1).to_frame(name="ai_basket_ret")

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

    # Optional OLS with safety checks
    for t in TECH:
        print(f"\n=== {t} OLS (enriched) ===")
        target=f"{t}_ret"
        if target in all_feat[t]:
            na=all_feat[t].drop(columns=[target]).isna().mean()
            keep = na.sort_values().index[:min(20, len(na))].tolist()
            fit_ols_safe(all_feat[t][[target]+keep], target)

    print("\nDone. CSVs in:", OUT_DIR)
    print("Raw price cache in:", RAW_DIR)
    print("Provider: polygon (only)")

if __name__=="__main__":
    main()

