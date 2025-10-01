# Multi-Agent Financial Analysis System  
## Task 2: Data Acquisition Report  
**Author:** Robair Farag  
**Course:** AAI 520 – Final Team Project  
**Date:** September–October 2025  

---

### 1. Introduction  
As part of the **Multi-Agent Financial Analysis System** project, my responsibility was **Task 2: Data Acquisition**. This stage serves as the foundation for the project, ensuring that reliable, high-quality data is collected and prepared for subsequent preprocessing, workflow implementation, and agent design. Without accurate data acquisition, the downstream tasks of building agent workflows and autonomous research agents cannot function effectively.  

The focus of this work was to:  
- Set up the project repository and environment.  
- Connect to **Yahoo Finance** for stock price data.  
- Connect to the **FRED API** (Federal Reserve Economic Data) for macroeconomic indicators.  
- Implement caching, schema documentation, and initial visualization.  
- Provide early findings and insights based on the acquired data.  

---

### 2. Repository & Environment Setup  
- Initialized GitHub repository with proper structure:  
  - `src/data/` → Python scripts for data acquisition.  
  - `notebooks/` → Jupyter/analysis scripts.  
  - `data_cache/` → Cached CSV files for reproducibility.  
- Configured `.gitignore` to exclude sensitive files (`.env`, cache files).  
- Added `.env` file to store API keys securely.  
- Created **DATA_SCHEMA.md** to standardize column naming and ensure consistency across datasets.  

---

### 3. Yahoo Finance Integration  
I implemented **`yahoo.py`** to fetch daily OHLCV (Open, High, Low, Close, Volume) stock data.  

**Features:**  
- Single-ticker function (`get_stock_prices`) with customizable period and interval.  
- Multi-ticker support (`get_multiple_prices`) for tech stocks (AAPL, MSFT, NVDA, META).  
- Data cleaning (resetting index, renaming columns to lowercase).  
- Returned tidy DataFrames ready for downstream analysis.  

**Findings:**  
- Retrieved ~250 trading days for each stock (1-year daily).  
- Dataset included consistent columns: `date, open, high, low, close, volume`.  
- Verified correctness with sample plots (AAPL 1-year close price).  

---

### 4. FRED API Integration  
I registered for and integrated a **FRED API Key** to access key macroeconomic indicators.  

**Implemented in `fred.py`:**  
- **FEDFUNDS** → Federal Funds Rate.  
- **DGS10** → 10-Year Treasury Yield.  
- **CPIAUCSL** → Consumer Price Index.  
- **UNRATE** → Unemployment Rate.  

**Enhancements:**  
- Added caching to `data_cache/` to reduce API calls and improve reproducibility.  
- Implemented schema validation when loading cached files.  
- Normalized date handling across Yahoo Finance and FRED datasets.  

**Findings:**  
- ~128 rows retrieved for monthly macroeconomic indicators.  
- Daily Treasury Yield (DGS10) aligned with stock trading dates, enabling comparative analysis.  
- Verified correlation between AAPL price movements and DGS10 fluctuations.  

---

### 5. Visualizations & Early Findings  
I generated initial plots to validate and explore the data.  

**Examples:**  
1. **AAPL 1-Year Closing Price:** Confirmed proper Yahoo Finance integration.  
2. **AAPL vs. DGS10 Overlay:** Showed potential inverse relationship between Apple’s valuation and 10-year Treasury yield.  

**Key Observations:**  
- Growth-oriented tech stocks (like AAPL) show sensitivity to rising yields.  
- Macroeconomic indicators (CPI, UNRATE) can be directly aligned with stock timelines for richer analysis.  
- These early insights validate the relevance of the selected datasets for agent workflows.  

---

### 6. Key Contributions  
As **Data Acquisition Lead**, my completed contributions include:  
- ✅ GitHub repo initialization and environment setup.  
- ✅ Yahoo Finance integration for tech stock data.  
- ✅ FRED API integration for macroeconomic indicators.  
- ✅ Secure API key management (`.env`).  
- ✅ Caching layer for reproducibility.  
- ✅ Data schema documentation.  
- ✅ Sanity plots and comparative visualizations.  
- ✅ Written findings to guide agent and workflow development.  

---

### 7. Conclusion  
My work provided the **data backbone** for the Multi-Agent Financial Analysis System. By integrating financial market data (Yahoo Finance) and macroeconomic indicators (FRED), I ensured that our team has a reliable foundation for implementing agent workflows and autonomous research agents.  

This contribution aligns with the **Code (32.4%) requirement** of the project rubric, ensuring reproducibility, readability, and professional standards.  

---

### Author  
**Robair Farag**  


