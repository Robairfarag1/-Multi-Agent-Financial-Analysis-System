import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.yahoo import get_stock_prices
import matplotlib.pyplot as plt

# Fetch 1 year of Apple stock data
aapl = get_stock_prices("AAPL", period="1y")

# Plot closing price
plt.figure(figsize=(10,5))
plt.plot(aapl["date"], aapl["close"], label="AAPL Close")
plt.title("AAPL Closing Price (1 Year)")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save figure
plt.savefig("notebooks/aapl_plot.png")
print("✅ Plot saved to notebooks/aapl_plot.png")
