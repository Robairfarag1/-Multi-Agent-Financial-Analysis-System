# 🧠 Multi-Agent Financial Analysis System

## 📘 Project Summary
This project is a **multi-agent financial analysis system** that combines **macroeconomic, sector, and company-level data** to generate actionable insights.  
It automates financial data ingestion from multiple APIs and offline sources, builds monthly analytical features, and performs regression and correlation modeling.  
The system is designed for **reproducibility, scalability, and automation**, supporting both cloud and Jetson-based deployments.

---

## 🚀 Key Features

✅ Multi-source data integration (FRED, Polygon, Yahoo Finance, or Excel)  
✅ Automated monthly feature generation with caching  
✅ Macro indicators, market correlation, and AI-basket analysis  
✅ Offline Excel ingestion workflow for teammate datasets  
✅ Clean modular code with reproducible notebooks  
✅ Ready for Linux/Jetson or cloud deployment  

---

## 📁 Project Structure

```
Multi-Agent-Financial-Analysis-System/
│
├── src/                               # Core data and model utilities
│   ├── data/
│   │   ├── fred.py                    # FRED downloader (CPI, rates, inflation)
│   │   ├── yahoo.py                   # Yahoo Finance helper
│   │   └── __init__.py
│   └── __init__.py
│
├── notebooks/                         # Notebooks and scripts
│   ├── TechMonthly_hardening.py       # Full online pipeline (FRED + Polygon)
│   ├── TechMonthly_stable.py          # Stable variant of monthly aggregator
│   ├── IngestFromExcel_to_Monthly.py  # Offline Excel → CSV ingestion
│   ├── Rebuild_combined_from_features.py  # Reconstructs combined dataset
│   ├── Monthly_offline_model.py       # Offline regression/correlation model
│   ├── sanity_plot.py                 # Quick sanity visualizations
│   ├── plot_ticker.py                 # Plot a specific stock ticker
│   ├── TechStockData_monthly.ipynb    # Core analysis notebook
│   └── final_integrated_agent.ipynb   # Multi-agent AI integration demo
│
├── data_cache/                        # Auto-generated local data
│   ├── Monthly/
│   │   ├── tech_features_combined.csv
│   │   └── ret_corr.csv
│   └── raw/                           # Ignored raw caches
│
├── data_sources/                      # Offline Excel input (ignored)
│   └── Monthly_combined_analysis.xlsx
│
├── tests/                             # Sanity tests for CI
│   └── test_sanity.py
│
├── .github/workflows/python-app.yml   # GitHub Actions for testing
├── DATA_SCHEMA.md                     # Dataset schema and description
├── PROJECT_PLAN.pdf                   # Original project plan
├── Aiagent.md                         # Multi-agent AI design doc
├── Iman_Ai_Agent_Report.md            # Partner's analytical report
├── ROBAIR_TASK2_REPORT.md             # Technical and presentation report
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Ignore rules
└── README.md                          # You are here 🎯
```

---

## ⚙️ Setup

### 1️⃣ Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### 🧩 Option 1 — Offline Workflow (no API keys needed)
Use when teammate provides Excel data.
```bash
python3 notebooks/IngestFromExcel_to_Monthly.py
python3 notebooks/Rebuild_combined_from_features.py
python3 notebooks/Monthly_offline_model.py
```

### 🌐 Option 2 — Online Workflow (live FRED/Yahoo/Polygon data)
Create a `.env` file with:
```bash
FRED_API_KEY=your_fred_key
POLYGON_API_KEY=your_polygon_key
```

Then run:
```bash
python3 notebooks/TechMonthly_hardening.py
```

---

## 📉 Download Tech Stock Prices
To quickly visualize and validate data sources:
```bash
python3 notebooks/sanity_plot.py
python3 notebooks/plot_ticker.py --ticker NVDA --period 1y --interval 1d
```

---

## 🧠 How It Works

### 🗂 Data Ingestion Agents
Collect and normalize macroeconomic, benchmark, and stock data.

### ⚙️ Feature Engineering Agents
Build monthly and AI-sector-level combined datasets.

### 📈 Analytics & Modeling Agents
Perform regression, correlation, and return trend analysis.

### 🔄 Orchestration Layer
Manages caching, merging, and dataset updates.

---

## 📊 Outputs

| File | Description |
|------|--------------|
| `tech_features_combined.csv` | Unified macro + tech stock dataset |
| `ret_corr.csv` | Monthly return correlation matrix |
| `macro_monthly.csv` | Key macroeconomic features |
| `*_features_enriched.csv` | Company-specific enriched data |

---

## 📦 Dependencies

All dependencies are listed in `requirements.txt`.  
Key packages include:

- pandas  
- numpy  
- matplotlib  
- requests  
- yfinance  
- fredapi  
- scikit-learn  

Install via:
```bash
pip install -r requirements.txt
```

---

## 🧪 Testing

Run local tests:
```bash
pytest tests/
```

GitHub Actions (`.github/workflows/python-app.yml`) automatically runs CI checks on every commit.

---

## 🧩 Recommended `.gitignore`
```
__pycache__/
*.pyc
*.pyo
*.pyd
notebooks/.ipynb_checkpoints/
*.ipynb.bak
.venv/
.env
data_cache/raw/
data_cache/*prices*.csv
data_cache/tech_*csv
notebooks/*.png
*.tgz
*.zip
*.xlsx
data_sources/
```

---

## 👥 Contributors

| Name | Role | Responsibilities |
|------|------|------------------|
| **Robair Farag** | Lead Developer & AI Engineer | Architecture, model development, and automation |
| **Iman Hamdan** | Data Analyst | Offline Excel dataset prep and integration |
| **Syed M. Sirajuddin** | QA & Testing | Repository structure and validation |

---

