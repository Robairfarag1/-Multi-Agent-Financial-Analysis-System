import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.yahoo import get_multiple_prices
import matplotlib.pyplot as plt

# fetch
data = get_multiple_prices(["AAPL", "MSFT"], period="1y", interval="1d")
aapl, msft = data["AAPL"], data["MSFT"]

# plot
plt.figure(figsize=(10,5))
plt.plot(aapl["date"], aapl["close"], label="AAPL Close")
plt.plot(msft["date"], msft["close"], label="MSFT Close")
plt.title("AAPL vs MSFT — Closing Price (1 Year)")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(True)
plt.tight_layout()

# save
out = "notebooks/aapl_vs_msft.png"
plt.savefig(out)
print(f"✅ Plot saved to {out}")
