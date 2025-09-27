import pandas as pd

df = pd.read_csv("data_cache/tech_prices_merged.csv")
df["date"] = pd.to_datetime(df["date"])

# pivot close prices to wide, compute daily pct change, then correlation
wide = df.pivot(index="date", columns="ticker", values="close").sort_index()
rets = wide.pct_change().dropna()
corr = rets.corr()

corr_path = "data_cache/tech_close_daily_corr.csv"
corr.to_csv(corr_path)
print(f"✅ Correlation matrix saved to {corr_path}")
print(corr)
