import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data_cache/tech_prices_merged.csv")
df["date"] = pd.to_datetime(df["date"])

# pivot to wide for close prices
wide = df.pivot(index="date", columns="ticker", values="close").sort_index()

# rebase each series to 100 at the first available value
rebased = wide.apply(lambda s: (s / s.dropna().iloc[0]) * 100, axis=0)

plt.figure(figsize=(10,6))
for col in rebased.columns:
    plt.plot(rebased.index, rebased[col], label=col)

plt.title("Tech Stocks — Rebased to 100 (Last ~1Y)")
plt.xlabel("Date")
plt.ylabel("Index (100 = first day)")
plt.legend()
plt.grid(True)
plt.tight_layout()
out = "notebooks/tech_rebased_100.png"
plt.savefig(out)
print(f"✅ Plot saved to {out}")
