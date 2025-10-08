# **Final Report: A Multi-Modal, Comparative Financial Analysis Agent**

Author:Iman

Course:AAI 520 – Final Team Project

### **1\. Abstract**

This report documents the final architecture and validation of the InvestmentResearchAgent, a sophisticated autonomous system for financial analysis. The agent was iteratively enhanced from a single-stock prototype into a multi-modal, comparative analysis tool. The final version successfully integrates three distinct data sources: quantitative market data (Yahoo Finance), macroeconomic indicators (FRED), and qualitative news analysis (NewsAPI with VADER sentiment). It demonstrates the ability to analyze and compare multiple equities simultaneously against this rich dataset. The agent's Plan-Execute-Reflect-Learn (PERL) architecture proved robust, enabling dynamic tool use and risk-aware self-assessment. This document details the agent's final methodology, summarizes the key enhancements, and presents validation results confirming its successful operation.

### **2\. Methodology: The Agent's Cognitive Cycle**

The agent operates on a **Plan-Execute-Reflect-Learn (PERL)** architecture, allowing it to autonomously manage a complex, multi-tool workflow.

* **Plan:** The agent parses a user's topic (e.g., "Compare NVDA, AMD, and JPM...") to create a research plan, identifying the target companies for analysis.  
* **Execute:** The agent dynamically uses its full toolset:  
  1. **Market Data Tool:** Fetches historical stock prices.  
  2. **Macroeconomic Tool:** Fetches data for four key economic indicators (DGS10, FEDFUNDS, CPIAUCSL, UNRATE).  
  3. Sentiment Analysis Tool: Fetches recent news and calculates a VADER sentiment score for each target company.  
     The agent then synthesizes these three data streams into a single, comprehensive comparative insight.  
* **Reflect:** The agent performs a final quality check on its output, programmatically verifying that all quantitative indicators and the qualitative sentiment analysis were successfully included for all target stocks.  
* **Learn:** Based on the reflection, the agent logs a structured memory of the cycle's outcome, marking it as a "success" or "failure" for future reference.

---

### **3\. Debugging and Enhancement Summary**

The agent's development involved several key enhancement stages to meet and exceed the project rubric.

| Enhancement Stage | Description of Improvement | Impact on Performance |
| :---- | :---- | :---- |
| **Dynamic Tool Use** | The agent was upgraded from using one hardcoded indicator to dynamically analyzing against all four required FRED macro series. | Drastically increased the analytical depth and met a core project requirement. |
| **Risk-Aware Reflection** | The self\_reflect method was enhanced to check for the presence of all required indicators and key risk-related terminology. | Made the agent capable of true self-assessment, a key feature of autonomous systems. |
| **Comparative Analysis** | The execution logic was rewritten to handle and compare a list of multiple stock tickers in a single run. | Elevated the agent from a single-entity analyzer to a more powerful comparative analysis tool. |
| **Sentiment Integration** | A third data modality was added, allowing the agent to fetch and analyze real-time news sentiment. | Provided crucial qualitative context to the agent's quantitative analysis, creating a more holistic and powerful insight. |

---

### **4\. Validation Results**

The final, fully integrated agent was validated using the complex topic "Compare NVDA, AMD, and JPM against the US Economy". The agent successfully executed all stages of its workflow, producing a comprehensive report.

Validated Outcome:

The agent's output included:

1. A detailed breakdown of correlations for **all three stocks** against **all four macroeconomic indicators**.  
2. A unique **news sentiment score** calculated for each of the three companies.  
3. A final summary insight combining all findings.

The agent's self\_reflect method subsequently confirmed that the analysis was **COMPLETE** (all indicators and stocks included) and **SENTIMENT-AWARE**, providing definitive proof that the final integrated pipeline is fully functional and robust.

### **5\. Next Steps and Future Work**

The current agent is a complete and successful implementation of the project requirements. Future work could focus on enhancing its intelligence and capabilities even further:

* **Time-Series Sentiment:** Instead of a single point-in-time score, the agent could track sentiment changes over time to identify trends and momentum.  
* **Source-Based Weighting:** The sentiment tool could be upgraded to give more weight to articles from highly reputable financial news sources.  
* **Autonomous Learning:** The agent's plan method could be enhanced to consult its memory log, allowing it to learn from past analyses to refine its strategy for future research tasks.