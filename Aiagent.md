# Multi-Modal Financial Analysis Agent

**Course:** AAI 520 – Final Team Project
**Author (Agent Logic & Integration):** Iman
**Team Members:** Robair (Data Acquisition), Syed (Preprocessing & Workflows)
**Date:** October 7, 2025

---

## 1. Project Overview

This project implements a sophisticated, autonomous AI agent for comprehensive financial analysis. The agent, built in Python and designed for a Jupyter Notebook environment, goes beyond simple data retrieval to perform a multi-modal analysis. It integrates three distinct data sources—**market prices**, **macroeconomic indicators**, and **news sentiment**—to generate a holistic and actionable insight on one or more publicly traded companies.

The system is built on a Plan-Execute-Reflect-Learn (PERL) cognitive architecture, allowing it to autonomously manage its workflow, assess the quality of its own analysis, and log its findings for future reference.



---

## 2. Core Features

* **Multi-Stock Comparative Analysis:** The agent can analyze multiple stocks (e.g., NVDA, AMD, JPM) in a single run, providing a direct comparison of their sensitivity to economic factors.
* **Dynamic Macroeconomic Tooling:** It automatically fetches and correlates stock performance against four key FRED economic indicators:
    * `DGS10` (10-Year Treasury Yield)
    * `FEDFUNDS` (Federal Funds Rate)
    * `CPIAUCSL` (Consumer Price Index / Inflation)
    * `UNRATE` (Unemployment Rate)
* **Real-Time News Sentiment:** The agent fetches recent news articles for each target company from the NewsAPI and uses the VADER library to calculate a real-time sentiment score, adding crucial qualitative context to its quantitative analysis.
* **Risk-Aware Self-Reflection:** After each run, the agent programmatically checks its own output to ensure all required analytical components (all four macro indicators and the sentiment score) are present, validating the quality of its insight.
* **Colab-Compatible:** The entire project is contained within a single, self-contained notebook, ensuring it can be run in any standard Python environment (including Google Colab) without dependency issues.

---

## 3. Setup and Installation

To run this project, you will need Python 3 and the following libraries.

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2.  **Install Dependencies:**
    The following libraries are required. You can install them using pip:
    ```bash
    pip install pandas yfinance requests vaderSentiment jupyterlab
    ```

3.  **Add API Keys:**
    Open the notebook (`final_submission.ipynb`) and replace the placeholder API keys at the top with your own valid keys:
    ```python
    FRED_API_KEY = "YOUR_FRED_API_KEY_HERE"
    NEWS_API_KEY = "YOUR_NEWS_API_KEY_HERE"
    ```

---

## 4. How to Use

The entire project is orchestrated by the `main()` function within the notebook.

1.  **Open the Notebook:**
    Launch Jupyter Lab or Jupyter Notebook:
    ```bash
    jupyter lab
    ```
    Then, open the `final_submission.ipynb` file.

2.  **Define a Research Topic:**
    Modify the `topic` variable at the bottom of the script to define your analysis. The agent is designed to parse topics in the format `"TICKER1, TICKER2, ... vs. the US Economy"`.

    **Example:**
    ```python
    # --- Run the project ---
    topic = "Compare NVDA, AMD, and JPM against the US Economy"
    main(topic)
    ```

3.  **Run All Cells:**
    Execute all the cells in the notebook from top to bottom. The agent will run its full analysis cycle and print the final, comprehensive insight at the end.