import os, glob
import pandas as pd

def main():
    os.makedirs("data_cache", exist_ok=True)
    files = glob.glob("data_cache/*_prices.csv")
    if not files:
        print("⚠️ No cached CSVs found in data_cache/. Run download_prices.py first.")
        return

    frames = []
    for f in files:
        ticker = os.path.basename(f).split("_")[0]
        df = pd.read_csv(f)
        df["ticker"] = ticker
        frames.append(df)

    out = pd.concat(frames, ignore_index=True)
    # ensure consistent columns and order
    cols = ["date","ticker","open","high","low","close","volume"]
    out = out[cols]
    out.sort_values(["ticker","date"], inplace=True)

    out_path = "data_cache/tech_prices_merged.csv"
    out.to_csv(out_path, index=False)
    print(f"✅ Merged {len(files)} files -> {out_path}")
    print(out.head())

if __name__ == "__main__":
    main()
