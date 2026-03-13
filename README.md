# Smart Home Network Analytics

**End-to-end data analytics project simulating product analytics for a smart home WiFi company (eero / Amazon), covering EDA, churn prediction, anomaly detection, and A/B testing.**

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.2-green?logo=pandas)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.5-orange?logo=scikit-learn)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL%20%7C%20SQLite-blue?logo=postgresql)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-orange?logo=jupyter)

---

## Business Context

Smart home WiFi providers like eero need to understand network quality, customer churn drivers, and the impact of firmware updates on user experience. This project mirrors the daily work of a Product Data Analyst — from exploring telemetry data to building predictive models that inform retention strategy and product decisions.

---

## Dataset Overview

All data is synthetically generated via `src/simulate_data.py` with `np.random.seed(42)` for reproducibility.

| Dataset | Rows | Description |
|---|---|---|
| `households.csv` | 5,000 | Customer profiles with device model, plan, firmware, churn label |
| `network_events.csv` | 450,000 | Daily network telemetry (drops, latency, bandwidth, packet loss) |
| `user_sessions.csv` | 373,313 | App engagement data (feature usage, session duration, support tickets) |
| `firmware_updates.csv` | 2,351 | Firmware A/B test data (pre/post update connection drops) |

---

## Key Findings

- **Firmware drives churn**: Households on firmware 6.1.0 churn at 2-3x the rate of those on 6.5.0, confirming that keeping devices updated is the strongest retention lever.
- **Network quality predicts churn**: Churned households average significantly more connection drops and higher latency. A Logistic Regression model achieves **0.96 ROC-AUC** using network + engagement features.
- **Anomaly detection validates churn signals**: IsolationForest flags 5% of households as anomalous; these churn at **11.95x** the rate of normal households (93.6% vs 7.8%).
- **Firmware 6.5.0 update is effective**: A/B test shows a statistically significant **32.1% reduction** in connection drops (p < 0.001, 95% CI: [1.07, 1.50]).
- **Support tickets are a leading indicator**: Churned households raise ~2.4x more support tickets on average.

---

## Model Results

| Metric | Logistic Regression | Gradient Boosting |
|---|---|---|
| ROC-AUC | 0.9618 | 0.9347 |
| PR-AUC | 0.8491 | 0.8001 |
| Precision@10% | 0.85 | 0.80 |

**Optimal threshold**: 0.10 | **Expected net savings**: $10,512/year

Top predictive features: `avg_latency_30d`, `avg_drops_7d`, `support_tickets_total`

---

## Project Structure

```
smart-home-analytics/
├── README.md
├── requirements.txt
├── data/
│   ├── households.csv
│   ├── network_events.csv
│   ├── user_sessions.csv
│   └── firmware_updates.csv
├── src/
│   └── simulate_data.py
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_churn_model.ipynb
│   ├── 03_anomaly_detection.ipynb
│   └── 04_ab_testing.ipynb
├── images/
│   └── (12 PNG plots at 300 DPI)
└── sql/
    └── validation_queries.sql
```

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate simulated data
python src/simulate_data.py

# 3. Run notebooks (or open in Jupyter)
jupyter notebook notebooks/
```

---

## Tech Stack

- **Python 3.11** — core language
- **Pandas / NumPy** — data manipulation
- **Matplotlib / Seaborn** — visualization (dark-themed, 300 DPI)
- **Scikit-learn** — Logistic Regression, Gradient Boosting, IsolationForest
- **SciPy** — statistical testing (t-test, Mann-Whitney U)
- **SQL** — validation queries (PostgreSQL / SQLite compatible)

---

## Known Limitations

- Data is synthetic — real-world distributions may differ significantly
- Churn is modeled as binary; real churn is often a gradual disengagement process
- The A/B test assumes random assignment; real firmware rollouts may have selection bias
- IsolationForest contamination is set at 5% — tuning required for production use
- No time-series cross-validation applied to the churn model

---

## Author

Harthik Mallichetty
