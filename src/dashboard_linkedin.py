import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ── THEME ────────────────────────────────────────────────────────────────────
BG      = "#0d1117"
CARD    = "#161b22"
RED     = "#e94560"
BLUE    = "#58a6ff"
GREEN   = "#3fb950"
YELLOW  = "#d29922"
WHITE   = "#e6edf3"
GRAY    = "#8b949e"

def set_card(ax, title=None):
    ax.set_facecolor(CARD)
    ax.tick_params(colors=GRAY, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")
    if title:
        ax.set_title(title, color=WHITE, fontsize=11,
                     fontweight='bold', pad=12)

# ── LOAD DATA ────────────────────────────────────────────────────────────────
households = pd.read_csv('data/households.csv')
firmware_updates = pd.read_csv('data/firmware_updates.csv')

# ── COMPUTED METRICS ─────────────────────────────────────────────────────────
churn_by_fw = households.groupby('firmware_version')['churned'].mean().sort_index() * 100
churn_by_plan = households.groupby('plan_type')['churned'].mean() * 100
churn_by_region = households.groupby('region')['churned'].mean() * 100
churn_by_nodes = households.groupby('num_nodes')['churned'].mean() * 100

total_hh       = len(households)
overall_churn  = households['churned'].mean() * 100
at_risk        = int(total_hh * 0.05)
arr_at_risk    = at_risk * 120
net_savings    = 10512

# ────────────────────────────────────────────────────────────────────────────
# DASHBOARD 1 — BUSINESS STORY
# ────────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 10), facecolor=BG)
fig.suptitle("Smart Home Network Analytics  |  Churn Intelligence Dashboard",
             color=WHITE, fontsize=16, fontweight='bold', y=0.97)

gs = GridSpec(3, 4, figure=fig, hspace=0.55, wspace=0.4,
              left=0.06, right=0.97, top=0.91, bottom=0.07)

# ── KPI CARDS (row 0) ────────────────────────────────────────────────────────
kpis = [
    ("5,000",       "Households Monitored", BLUE),
    (f"{overall_churn:.1f}%", "Overall Churn Rate",  RED),
    (f"{at_risk:,}", "At-Risk Households",   YELLOW),
    (f"${net_savings:,}", "Est. Annual Savings",  GREEN),
]
for i, (val, label, color) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor(CARD)
    for spine in ax.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(2)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5, 0.62, val,   transform=ax.transAxes, ha='center',
            va='center', color=color,  fontsize=22, fontweight='bold')
    ax.text(0.5, 0.22, label, transform=ax.transAxes, ha='center',
            va='center', color=GRAY,   fontsize=9)

# ── CHURN BY FIRMWARE (row 1, col 0-1) ───────────────────────────────────────
ax1 = fig.add_subplot(gs[1, 0:2])
set_card(ax1, "Churn Rate by Firmware Version")
colors_fw = [RED if v == churn_by_fw.max() else BLUE for v in churn_by_fw.values]
bars = ax1.bar(churn_by_fw.index, churn_by_fw.values, color=colors_fw,
               edgecolor=BG, linewidth=0.5, width=0.6)
for bar, val in zip(bars, churn_by_fw.values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f'{val:.1f}%', ha='center', va='bottom', color=WHITE,
             fontsize=8.5, fontweight='bold')
ax1.set_xlabel("Firmware Version", color=GRAY, fontsize=9)
ax1.set_ylabel("Churn Rate (%)", color=GRAY, fontsize=9)
ax1.set_facecolor(CARD)
ax1.set_ylim(0, churn_by_fw.max() * 1.25)
highest = churn_by_fw.idxmax()
ax1.annotate(f'2.3x higher\nthan latest',
             xy=(list(churn_by_fw.index).index(highest), churn_by_fw.max()),
             xytext=(1.5, churn_by_fw.max() * 1.1),
             color=RED, fontsize=8, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))

# ── CHURN BY PLAN (row 1, col 2) ─────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1, 2])
set_card(ax2, "Churn by Plan Type")
plan_order = churn_by_plan.sort_values(ascending=True)
colors_plan = [GREEN, YELLOW, RED]
hbars = ax2.barh(plan_order.index, plan_order.values,
                 color=colors_plan, edgecolor=BG, linewidth=0.5, height=0.5)
for bar, val in zip(hbars, plan_order.values):
    ax2.text(val + 0.2, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}%', va='center', color=WHITE, fontsize=8.5, fontweight='bold')
ax2.set_xlabel("Churn Rate (%)", color=GRAY, fontsize=9)
ax2.set_xlim(0, plan_order.max() * 1.3)

# ── CHURN BY REGION (row 1, col 3) ───────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 3])
set_card(ax3, "Churn by Region")
region_sorted = churn_by_region.sort_values(ascending=False)
ax3.bar(range(len(region_sorted)), region_sorted.values,
        color=BLUE, edgecolor=BG, linewidth=0.5, width=0.6)
ax3.set_xticks(range(len(region_sorted)))
ax3.set_xticklabels([r[:3] for r in region_sorted.index],
                    color=GRAY, fontsize=8)
ax3.set_ylabel("Churn Rate (%)", color=GRAY, fontsize=9)
for i, val in enumerate(region_sorted.values):
    ax3.text(i, val + 0.1, f'{val:.1f}%', ha='center',
             color=WHITE, fontsize=7.5, fontweight='bold')

# ── ANOMALY INSIGHT (row 2, col 0-1) ─────────────────────────────────────────
ax4 = fig.add_subplot(gs[2, 0:2])
set_card(ax4, "Anomaly Detection — Churn Lift (IsolationForest)")
categories = ['Normal Households\n(95%)', 'Anomalous Households\n(5% flagged)']
values     = [7.8, 93.6]
colors_a   = [BLUE, RED]
bars4 = ax4.bar(categories, values, color=colors_a,
                edgecolor=BG, linewidth=0.5, width=0.4)
for bar, val in zip(bars4, values):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{val}%', ha='center', color=WHITE,
             fontsize=13, fontweight='bold')
ax4.set_ylabel("Churn Rate (%)", color=GRAY, fontsize=9)
ax4.set_ylim(0, 115)
ax4.text(0.5, 0.92, '11.95x Churn Lift', transform=ax4.transAxes,
         ha='center', color=RED, fontsize=12, fontweight='bold')

# ── A/B TEST (row 2, col 2-3) ────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[2, 2:4])
set_card(ax5, "Firmware A/B Test — Connection Drops (6.4.2 → 6.5.0)")
groups  = ['Control\n(v6.4.2)', 'Treatment\n(v6.5.0)']
ab_vals = [100, 67.9]
bar_colors = [YELLOW, GREEN]
bars5 = ax5.bar(groups, ab_vals, color=bar_colors,
                edgecolor=BG, linewidth=0.5, width=0.35)
ax5.text(bars5[0].get_x() + bars5[0].get_width()/2,
         bars5[0].get_height() + 1.5, 'Baseline',
         ha='center', color=WHITE, fontsize=10, fontweight='bold')
ax5.text(bars5[1].get_x() + bars5[1].get_width()/2,
         bars5[1].get_height() + 1.5, '−32.1%',
         ha='center', color=GREEN, fontsize=13, fontweight='bold')
ax5.set_ylabel("Relative Connection Drops (%)", color=GRAY, fontsize=9)
ax5.set_ylim(0, 125)
ax5.text(0.5, 0.9, 'p < 0.001  |  Statistically Significant',
         transform=ax5.transAxes, ha='center',
         color=GRAY, fontsize=9, style='italic')

# watermark
fig.text(0.97, 0.01, 'github.com/harthikrm/smart-home-analytics',
         ha='right', color=GRAY, fontsize=8, style='italic')

plt.savefig('images/dashboard_1_business_story.png',
            dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("Dashboard 1 saved.")

# ────────────────────────────────────────────────────────────────────────────
# DASHBOARD 2 — MODEL PERFORMANCE
# ────────────────────────────────────────────────────────────────────────────
from sklearn.metrics import roc_curve, precision_recall_curve
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Rebuild features from households only (no network events needed)
df = households.copy()
le = LabelEncoder()
df['fw_enc']   = le.fit_transform(df['firmware_version'])
df['plan_enc'] = le.fit_transform(df['plan_type'])
df['region_enc'] = le.fit_transform(df['region'])
df['model_enc']  = le.fit_transform(df['device_model'])

features = ['fw_enc', 'plan_enc', 'region_enc', 'model_enc',
            'num_nodes', 'connected_devices', 'tenure_days']
X = df[features]
y = df['churned']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

lr  = LogisticRegression(max_iter=1000, random_state=42).fit(X_train, y_train)
gb  = GradientBoostingClassifier(n_estimators=100, random_state=42).fit(X_train, y_train)

lr_probs = lr.predict_proba(X_test)[:, 1]
gb_probs = gb.predict_proba(X_test)[:, 1]

lr_fpr,  lr_tpr,  _  = roc_curve(y_test, lr_probs)
gb_fpr,  gb_tpr,  _  = roc_curve(y_test, gb_probs)
lr_prec, lr_rec,  _  = precision_recall_curve(y_test, lr_probs)
gb_prec, gb_rec,  _  = precision_recall_curve(y_test, gb_probs)

from sklearn.metrics import roc_auc_score, average_precision_score
lr_auc  = roc_auc_score(y_test, lr_probs)
gb_auc  = roc_auc_score(y_test, gb_probs)
lr_pr   = average_precision_score(y_test, lr_probs)
gb_pr   = average_precision_score(y_test, gb_probs)

# Feature importance
feat_imp = pd.Series(gb.feature_importances_, index=features).sort_values()
feat_labels = {
    'fw_enc': 'Firmware Version',
    'plan_enc': 'Plan Type',
    'region_enc': 'Region',
    'model_enc': 'Device Model',
    'num_nodes': 'Number of Nodes',
    'connected_devices': 'Connected Devices',
    'tenure_days': 'Tenure (Days)'
}

# Threshold analysis
thresholds = np.arange(0.05, 0.95, 0.01)
retention_cost = 8
ltv = 120
net_savings_list = []
for t in thresholds:
    preds = (gb_probs >= t).astype(int)
    tp = ((preds == 1) & (y_test == 1)).sum()
    fp = ((preds == 1) & (y_test == 0)).sum()
    net = tp * ltv - (tp + fp) * retention_cost
    net_savings_list.append(net)
best_t = thresholds[np.argmax(net_savings_list)]

fig2 = plt.figure(figsize=(16, 9), facecolor=BG)
fig2.suptitle("Smart Home Network Analytics  |  Model Performance Dashboard",
              color=WHITE, fontsize=16, fontweight='bold', y=0.97)

gs2 = GridSpec(2, 4, figure=fig2, hspace=0.5, wspace=0.4,
               left=0.06, right=0.97, top=0.91, bottom=0.08)

# KPI cards
kpis2 = [
    (f"{lr_auc:.3f}",  "LR ROC-AUC",      BLUE),
    (f"{gb_auc:.3f}",  "GB ROC-AUC",       RED),
    (f"{lr_pr:.3f}",   "LR PR-AUC",        GREEN),
    (f"{best_t:.2f}",  "Optimal Threshold", YELLOW),
]
for i, (val, label, color) in enumerate(kpis2):
    ax = fig2.add_subplot(gs2[0, i])
    ax.set_facecolor(CARD)
    for spine in ax.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(2)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5, 0.62, val,   transform=ax.transAxes, ha='center',
            va='center', color=color, fontsize=22, fontweight='bold')
    ax.text(0.5, 0.22, label, transform=ax.transAxes, ha='center',
            va='center', color=GRAY,  fontsize=9)

# ROC curve
ax6 = fig2.add_subplot(gs2[1, 0:2])
set_card(ax6, "ROC Curve Comparison")
ax6.plot(lr_fpr, lr_tpr, color=BLUE,  lw=2,
         label=f'Logistic Regression (AUC={lr_auc:.3f})')
ax6.plot(gb_fpr, gb_tpr, color=RED,   lw=2,
         label=f'Gradient Boosting (AUC={gb_auc:.3f})')
ax6.plot([0,1], [0,1], color=GRAY, lw=1, linestyle='--', label='Random')
ax6.set_xlabel("False Positive Rate", color=GRAY, fontsize=9)
ax6.set_ylabel("True Positive Rate",  color=GRAY, fontsize=9)
ax6.legend(fontsize=8, facecolor=CARD, labelcolor=WHITE, edgecolor=GRAY)

# Feature importance
ax7 = fig2.add_subplot(gs2[1, 2])
set_card(ax7, "Feature Importance (GB)")
colors_fi = [RED if v == feat_imp.max() else BLUE for v in feat_imp.values]
ax7.barh([feat_labels[f] for f in feat_imp.index],
         feat_imp.values, color=colors_fi,
         edgecolor=BG, linewidth=0.5, height=0.6)
ax7.set_xlabel("Importance", color=GRAY, fontsize=9)

# Threshold analysis
ax8 = fig2.add_subplot(gs2[1, 3])
set_card(ax8, "Cost Threshold Optimization")
ax8.plot(thresholds, net_savings_list, color=GREEN, lw=2)
ax8.axvline(x=best_t, color=YELLOW, lw=1.5, linestyle='--',
            label=f'Optimal: {best_t:.2f}')
ax8.fill_between(thresholds, net_savings_list,
                 where=[v > 0 for v in net_savings_list],
                 alpha=0.2, color=GREEN)
ax8.set_xlabel("Decision Threshold", color=GRAY, fontsize=9)
ax8.set_ylabel("Net Savings ($)",    color=GRAY, fontsize=9)
ax8.legend(fontsize=8, facecolor=CARD, labelcolor=WHITE, edgecolor=GRAY)

fig2.text(0.97, 0.01, 'github.com/harthikrm/smart-home-analytics',
          ha='right', color=GRAY, fontsize=8, style='italic')

plt.savefig('images/dashboard_2_model_performance.png',
            dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("Dashboard 2 saved.")
print("\nBoth dashboards saved to images/")
print("  → images/dashboard_1_business_story.png")
print("  → images/dashboard_2_model_performance.png")