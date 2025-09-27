# Convenience imports for data layer
from .yahoo import get_stock_prices, get_multiple_prices
# FRED helpers become available once API key / cache is set:
from .fred import (
    get_fred_series,
    get_fedfunds,
    get_dgs10,
    get_cpi,
    get_unrate,
)

