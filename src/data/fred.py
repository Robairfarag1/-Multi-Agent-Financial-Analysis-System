import os
import pandas as pd
import requests

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

class MissingApiKey(RuntimeError):
    pass

def _cache_path(series_id: str) -> str:
    os.makedirs("data_cache", exist_ok=True)
    return f"data_cache/fred_{series_id}.csv"

def _load_cache(series_id: str) -> pd.DataFrame | None:
    path = _cache_path(series_id)
    if os.path.exists(path):
        df = pd.read_csv(path)
        # basic schema check
        if set(df.columns) >= {"date", "value"}:
            df["date"] = pd.to_datetime(df["date"])
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            return df
    return None

def _save_cache(series_id: str, df: pd.DataFrame) -> None:
    df.to_csv(_cache_path(series_id), index=False)

def _get_key() -> str:
    key = os.getenv("FRED_API_KEY")
    if not key:
        # defer failure until after we try to use cache
        raise MissingApiKey(
            "FRED_API_KEY not set. Add it later in your shell or a .env file.\n"
            "Example:\n  export FRED_API_KEY=YOUR_KEY_HERE"
        )
    return key

def get_fred_series(series_id: str, start: str = "2015-01-01", use_cache: bool = True) -> pd.DataFrame:
    """
    Return a tidy DataFrame with columns: date (datetime64[ns]), value (float).
    Priority: load from cache -> else fetch from API (requires FRED_API_KEY).
    """
    if use_cache:
        cached = _load_cache(series_id)
        if cached is not None:
            return cached

    # No usable cache; try API
    api_key = _get_key()  # raises clear error if not set
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start,
        "sort_order": "asc",
    }
    r = requests.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    obs = r.json().get("observations", [])
    df = pd.DataFrame(obs, columns=["date", "value"])
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    if use_cache:
        _save_cache(series_id, df)

    return df

# Convenience wrappers for your chosen indicators
def get_fedfunds(start="2015-01-01", use_cache: bool = True) -> pd.DataFrame:
    return get_fred_series("FEDFUNDS", start=start, use_cache=use_cache)

def get_dgs10(start="2015-01-01", use_cache: bool = True) -> pd.DataFrame:
    return get_fred_series("DGS10", start=start, use_cache=use_cache)

def get_cpi(start="2015-01-01", use_cache: bool = True) -> pd.DataFrame:
    # CPIAUCSL (index level). YoY % is units=pc1; we keep level for now (simpler).
    return get_fred_series("CPIAUCSL", start=start, use_cache=use_cache)

def get_unrate(start="2015-01-01", use_cache: bool = True) -> pd.DataFrame:
    return get_fred_series("UNRATE", start=start, use_cache=use_cache)

