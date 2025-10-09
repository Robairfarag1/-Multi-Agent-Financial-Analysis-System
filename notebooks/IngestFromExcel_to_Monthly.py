#!/usr/bin/env python3
import os, sys
import pandas as pd
import numpy as np

THIS_DIR = os.path.dirname(__file__)
XLSX_PATH = os.path.join(THIS_DIR, "Monthly_combined_analysis.xlsx")
OUT_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "data_cache", "Monthly"))
os.makedirs(OUT_DIR, exist_ok=True)
OUT_COMBINED = os.path.join(OUT_DIR, "tech_features_combined.csv")

DATE_CANDIDATES = [
    "date",
    "datetime",
    "internal (index)",
    "month-end timestamp; time index for monthly aggregation.",
]

def read_workbook(path: str):
    if not os.path.exists(path):
        print(f"[fatal] Excel not found at: {path}")
        sys.exit(1)
    return pd.ExcelFile(path)

def guess_header_row(raw: pd.DataFrame, max_scan: int = 12) -> int:
    raw = raw.copy()
    raw = raw.dropna(how="all").dropna(axis=1, how="all")
    nrows = min(len(raw), max_scan)
    for r in range(nrows):
        row_vals = raw.iloc[r].astype(str).str.strip().str.lower().fillna("")
        if any(v in ("date", "month", "datetime", "internal (index)") for v in row_vals):
            return r
    for r in range(nrows - 1):
        row = raw.iloc[r]
        nxt = raw.iloc[r + 1]
        str_frac = (row.astype(str) == row).mean()
        num_like = pd.to_numeric(nxt, errors="coerce")
        date_like = pd.to_datetime(nxt, errors="coerce")
        score = (num_like.notna().mean() + date_like.notna().mean()) / 2.0
        if str_frac > 0.6 and score > 0.3:
            return r
    return 0

def build_df_from_raw(raw: pd.DataFrame) -> pd.DataFrame:
    raw = raw.dropna(how="all").dropna(axis=1, how="all")
    hdr = guess_header_row(raw)
    headers = raw.iloc[hdr].astype(str).tolist()
    df = raw.iloc[hdr + 1 :].copy()
    df.columns = [h.strip() for h in headers]
    # drop empty/Unnamed
    keep = [c for c in df.columns if c and not str(c).startswith("Unnamed")]
    return df.loc[:, keep]

def _parse_maybe_epoch(s: pd.Series) -> pd.Series:
    # try text/ISO parse
    dt = pd.to_datetime(s, errors="coerce")
    if dt.notna().sum() >= max(5, int(0.25 * len(s))):
        return dt
    # try unix seconds
    dt = pd.to_datetime(pd.to_numeric(s, errors="coerce"), unit="s", errors="coerce")
    if dt.notna().sum() >= max(5, int(0.25 * len(s))):
        return dt
    # try unix ms
    dt = pd.to_datetime(pd.to_numeric(s, errors="coerce"), unit="ms", errors="coerce")
    if dt.notna().sum() >= max(5, int(0.25 * len(s))):
        return dt
    # try unix ns
    dt = pd.to_datetime(pd.to_numeric(s, errors="coerce"), unit="ns", errors="coerce")
    if dt.notna().sum() >= max(5, int(0.25 * len(s))):
        return dt
    # try Excel serial date
    num = pd.to_numeric(s, errors="coerce")
    # Excel serials are usually between ~20000 and ~60000 for modern dates
    if num.notna().any():
        dt = pd.to_datetime(num, unit="D", origin="1899-12-30", errors="coerce")
        if dt.notna().sum() >= max(5, int(0.25 * len(s))):
            return dt
    return pd.to_datetime(pd.Series([], dtype=object), errors="coerce")

def to_month_end_index(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    # find a date column
    cols_lc = {c.lower(): c for c in df.columns}
    cand = next((cols_lc[c] for c in DATE_CANDIDATES if c in cols_lc), None)

    if cand is None:
        # if first column looks date-like, use it
        for c in df.columns:
            dt = _parse_maybe_epoch(df[c])
            if dt.notna().mean() > 0.5:
                cand = c
                break

    if cand is None:
        print("[warn] No date-like column found. Writing CSV as-is.")
        return df

    dt = _parse_maybe_epoch(df[cand])
    keep = dt.notna()
    if keep.sum() == 0:
        print(f"[warn] Could not parse any dates in column: {cand}")
        return df

    df = df.loc[keep].copy()
    df.index = dt.loc[keep].dt.to_period("M").dt.to_timestamp("M")
    df.drop(columns=[cand], inplace=True, errors="ignore")
    df.sort_index(inplace=True)
    df = df[~df.index.duplicated(keep="last")]
    return df

def main():
    x = read_workbook(XLSX_PATH)
    sheets = x.sheet_names
    print("Workbook sheets found:", sheets)
    sheet = sheets[0] if len(sheets) == 1 else ( "tech_features_combined" if "tech_features_combined" in sheets else sheets[0] )
    if len(sheets) == 1:
        print(f"[auto] Single sheet detected ({sheet}). Treating as tech_features_combined.csv")
    else:
        print(f"[auto] Using sheet: {sheet}")

    raw = pd.read_excel(XLSX_PATH, sheet_name=sheet, header=None, dtype=object)
    df = build_df_from_raw(raw)
    # numeric-cast obvious numeric columns
    for c in df.columns:
        if df[c].dtype == object:
            n = pd.to_numeric(df[c], errors="coerce")
            if n.notna().sum() >= max(5, int(0.5 * len(df))):
                df[c] = n

    df = to_month_end_index(df)
    df.to_csv(OUT_COMBINED)
    print("Saved →", OUT_COMBINED)
    print("\n✅ Done. CSV exported to:", OUT_COMBINED)

if __name__ == "__main__":
    main()

