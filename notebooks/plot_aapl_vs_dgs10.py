import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
from src.data.yahoo import get_stock_prices
from src.data.fred import get_dgs10, MissingApiKey

# fetch AAPL
aapl = get_stock_prices("AAPL", period="1y", interval="1d")

# fetch DGS10 (10Y Treasury) — needs key or existing cache
try:
    dgs10 = get_dgs10(start="2015-01-01", use_cache=True)
except MissingApiKey as e:
    print("⚠️ DGS10 requires FRED_API_KEY or cached CSV. Skipping overlay.")
    dgs10 = None

plt.figure(figsize=(10,6))
ax1 = plt.gca()
ax1.plot(aapl["date"], aapl["close"], label="AAPL Close (USD)")
ax1.set_xlabel("Date")
ax1.set_ylabel("AAPL Price (USD)")

if dgs10 is not None:
    # align to last 1y for visual clarity
    dgs10_1y = dgs10[dgs10["date"] >= aapl["date"].min()]
    ax2 = ax1.twinx()
    ax2.plot(dgs10_1y["date"], dgs10_1y["value"], label="US 10Y Yield (DGS10)", linestyle="--")
    ax2.set_ylabel("Yield (%)")
    ax2.legend(loc="upper left")

ax1.legend(loc="upper right")
plt.title("AAPL vs US 10Y Treasury Yield (overlay)")
plt.grid(True)
plt.tight_layout()
out = "notebooks/aapl_vs_dgs10.png"
plt.savefig(out)
print(f"✅ Plot saved to {out}")
