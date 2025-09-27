import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()  # optional: read FRED_API_KEY from .env if present

from src.data.fred import (
    get_fedfunds, get_dgs10, get_cpi, get_unrate, MissingApiKey
)

SERIES = {
    "FEDFUNDS": get_fedfunds,
    "DGS10":    get_dgs10,
    "CPIAUCSL": get_cpi,
    "UNRATE":   get_unrate,
}

def main():
    print("Starting FRED download (cache-first)...")
    for name, fn in SERIES.items():
        try:
            df = fn(use_cache=True)   # loads cache if exists; else calls API & caches
            print(f"✅ {name}: {len(df)} rows (cached or fetched)")
        except MissingApiKey as e:
            print(f"⚠️ {name}: {e}")
            print("   Set a key via:  export FRED_API_KEY=YOUR_KEY  (or add to .env)")
            return

if __name__ == "__main__":
    main()
