# Smart Home Network Analytics

> End-to-end product analytics pipeline simulating smart home WiFi telemetry — covering churn prediction, anomaly detection, A/B testing, and network health monitoring across 5,000 households and 450,000+ events.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2-green?logo=pandas&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.5-orange?logo=scikit-learn&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-8%20Queries-blue?logo=postgresql&logoColor=white)
![Jupyter](https://img.shields.io/badge/Notebooks-4-orange?logo=jupyter&logoColor=white)

---

## Overview

Smart home WiFi providers need to understand network quality, customer churn drivers, and firmware update impact before customers complain — or cancel. This project mirrors the daily work of a Product Data Analyst: exploring device telemetry, predicting churn before it happens, detecting anomalous households, and measuring whether product changes actually work.

**Core business question:** *Can you predict which household is about to cancel — before they even know it themselves?*

---

## Key Results

| Analysis | Result |
|---|---|
| Churn prediction (Logistic Regression) | ROC-AUC **0.962**, PR-AUC **0.849** |
| Churn prediction (Gradient Boosting) | ROC-AUC **0.935**, PR-AUC **0.800** |
| Anomaly detection churn lift | **11.95x** (93.6% vs 7.8% baseline) |
| Firmware A/B test impact | **32.1% reduction** in connection drops (p < 0.001) |
| Optimal cost threshold | $0.10 → estimated **$10,512/year** net savings |
| Top churn predictors | `avg_latency_30d`, `avg_drops_7d`, `support_tickets_total` |

---

## Findings

- **Firmware is the #1 retention lever** — households on v6.1.0 churn at 20.3% vs 8.9% on v6.5.0. Pushing updates proactively could cut churn by more than half for at-risk segments.
- **Anomalies predict churn with high precision** — IsolationForest flags 5% of households; these churn at nearly 12x the rate of normal households, making them a high-priority intervention list.
- **Support tickets are a leading indicator** — churned households raise 2.4x more tickets on average, suggesting that unresolved support issues are a stronger churn signal than network metrics alone.
- **Firmware 6.5.0 update is statistically validated** — A/B test confirms 32.1% reduction in daily connection drops with p < 0.001, providing product teams with rigorous evidence before full rollout.
- **Logistic Regression outperforms Gradient Boosting** on this dataset — linear separability in latency and drop features means simpler models generalize better, a useful reminder that model complexity ≠ model performance.

---

## Dataset

All data synthetically generated via `src/simulate_data.py` (`np.random.seed(42)`).

| File | Rows | Description |
|---|---|---|
| `households.csv` | 5,000 | Device model, firmware, plan type, region, churn label |
| `network_events.csv` | 450,000 | Daily telemetry: drops, latency, bandwidth, packet loss |
| `user_sessions.csv` | 373,313 | App engagement: feature usage, session duration, support tickets |
| `firmware_updates.csv` | 2,351 | A/B test data: pre/post connection drops by firmware version |

Churn rate: **12.1%** (realistic for subscription hardware products)

---

## Project Structure

```
smart-home-analytics/
├── README.md
├── requirements.txt
├── src/
│   └── simulate_data.py          # Full data simulation pipeline
├── data/
│   ├── households.csv
│   ├── firmware_updates.csv
│   └── (network_events + user_sessions generated locally — see How to Run)
├── notebooks/
│   ├── 01_eda.ipynb              # Exploratory analysis, 6 visualizations
│   ├── 02_churn_model.ipynb      # Logistic Regression vs Gradient Boosting
│   ├── 03_anomaly_detection.ipynb # IsolationForest, 11.95x churn lift
│   └── 04_ab_testing.ipynb       # Firmware A/B test, t-test + Mann-Whitney
├── images/
│   └── (12 dark-themed PNG plots, 300 DPI)
└── sql/
    └── validation_queries.sql    # 8 validation queries (PostgreSQL/SQLite)
```

---

## How to Run

```bash
# 1. Clone and install
git clone https://github.com/harthikrm/smart-home-analytics.git
cd smart-home-analytics
pip install -r requirements.txt

# 2. Generate full dataset (creates network_events.csv and user_sessions.csv)
python src/simulate_data.py

# 3. Run notebooks in order
jupyter notebook notebooks/
```

---

## Notebooks

| Notebook | What it covers |
|---|---|
| `01_eda.ipynb` | Churn by firmware, latency distributions, support ticket patterns, regional heatmap |
| `02_churn_model.ipynb` | Feature engineering (7d/30d rolling), model comparison, cost-threshold optimization |
| `03_anomaly_detection.ipynb` | IsolationForest, anomaly score distribution, churn lift validation |
| `04_ab_testing.ipynb` | Pre/post firmware analysis, t-test, Mann-Whitney U, confidence intervals |

---

## Tech Stack

- **Python 3.11** — core language
- **Pandas / NumPy** — data simulation and manipulation
- **Scikit-learn** — Logistic Regression, Gradient Boosting, IsolationForest
- **SciPy** — statistical testing (t-test, Mann-Whitney U)
- **Matplotlib / Seaborn** — dark-themed visualizations at 300 DPI
- **SQL** — 8 validation queries (PostgreSQL / SQLite compatible)

---

## Known Limitations

- Data is synthetic — real-world churn distributions may differ significantly
- Churn modeled as binary; real churn is often gradual disengagement
- A/B test assumes random firmware assignment; real rollouts may introduce selection bias
- IsolationForest contamination fixed at 5% — production use requires tuning
- No time-series cross-validation applied to churn model

---

## Author

**Harthik Mallichetty**
MSBA, UT Dallas | [LinkedIn](https://linkedin.com/in/harthikrm) | [GitHub](https://github.com/harthikrm)
