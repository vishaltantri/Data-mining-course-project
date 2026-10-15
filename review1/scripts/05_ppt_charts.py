#!/usr/bin/env python3
"""Regenerates every chart used in the Review 1 PPT (slides 3, 5, 6, 7, 11, 15) as PNG files.
Run from the repository root:   python review1/scripts/05_ppt_charts.py
Reads : the three BRFSS CSVs, review1/diabetes_dw.db, review1/baseline_results.json (from 06 script)
Writes: review1/figures/ppt/*.png
"""
import os, json, sqlite3
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "review1/figures/ppt"; os.makedirs(OUT, exist_ok=True)
BLACK, MID, LIGHT = "#111111", "#8C8C8C", "#BFBFBF"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#D9D9D9", "axes.axisbelow": True, "figure.dpi": 150})

bal = pd.read_csv("diabetes_binary_5050split_health_indicators_BRFSS2015.csv")
full = pd.read_csv("diabetes_binary_health_indicators_BRFSS2015.csv")
y = bal.Diabetes_binary
save = lambda name: (plt.tight_layout(), plt.savefig(f"{OUT}/{name}", dpi=200), plt.close())

# 1  slide 3: class distribution, full vs balanced
fig, ax = plt.subplots(figsize=(6, 4))
x = np.arange(2); w = 0.38
f_vals = [(full.Diabetes_binary == 0).sum(), (full.Diabetes_binary == 1).sum()]
b_vals = [(bal.Diabetes_binary == 0).sum(), (bal.Diabetes_binary == 1).sum()]
r1 = ax.bar(x - w/2, f_vals, w, color=MID, label="Full file (253,680)")
r2 = ax.bar(x + w/2, b_vals, w, color=BLACK, label="Balanced file (70,692)")
for r in list(r1) + list(r2):
    ax.text(r.get_x() + r.get_width()/2, r.get_height() + 3000, f"{int(r.get_height()):,}", ha="center", fontsize=9)
ax.set_xticks(x, ["No diabetes (0)", "Diabetes (1)"]); ax.set_ylabel("Respondents"); ax.legend(frameon=False)
ax.set_title("Class distribution: full vs balanced file", loc="left", fontweight="bold")
save("01_class_distribution.png")

# 2  slide 5: correlation of every attribute with the target
corr = bal.corr()["Diabetes_binary"].drop("Diabetes_binary").sort_values()
fig, ax = plt.subplots(figsize=(6.5, 6))
ax.barh(corr.index, corr.values, color=[BLACK if v >= 0 else MID for v in corr.values])
for i, v in enumerate(corr.values):
    ax.text(v + (0.01 if v >= 0 else -0.01), i, f"{v:+.2f}", va="center", ha="left" if v >= 0 else "right", fontsize=8)
ax.set_xlim(-0.3, 0.5); ax.set_xlabel("Pearson r with Diabetes_binary"); ax.grid(axis="y", visible=False)
ax.set_title("Correlation with diabetes (n = 70,692)", loc="left", fontweight="bold")
save("02_correlation_with_target.png")

# 3  slide 6: risk-factor prevalence, diabetes vs no diabetes
fac = [("High BP", "HighBP"), ("High cholesterol", "HighChol"), ("Difficulty walking", "DiffWalk"),
       ("Heart disease / attack", "HeartDiseaseorAttack"), ("Physically active", "PhysActivity"), ("Stroke", "Stroke"), ("Smoker", "Smoker")]
d1 = [bal.loc[y == 1, c].mean() * 100 for _, c in fac]; d0 = [bal.loc[y == 0, c].mean() * 100 for _, c in fac]
fig, ax = plt.subplots(figsize=(8, 4.2)); x = np.arange(len(fac))
a = ax.bar(x - w/2, d1, w, color=BLACK, label="Diabetes"); b = ax.bar(x + w/2, d0, w, color=LIGHT, label="No diabetes")
for r in list(a) + list(b):
    ax.text(r.get_x() + r.get_width()/2, r.get_height() + 1, f"{r.get_height():.1f}", ha="center", fontsize=8)
ax.set_xticks(x, [n for n, _ in fac], fontsize=8, rotation=15); ax.set_ylabel("% of respondents"); ax.legend(frameon=False)
ax.set_title("Risk factors by diabetes status (%)", loc="left", fontweight="bold")
save("03_comorbidity_prevalence.png")

# 4  slide 7: gradients by general health and income
fig, axs = plt.subplots(1, 2, figsize=(10, 4))
g = bal.groupby("GenHlth").Diabetes_binary.mean() * 100
axs[0].bar(["1 Excellent", "2 Very good", "3 Good", "4 Fair", "5 Poor"], g.values, color=BLACK)
inc = bal.groupby("Income").Diabetes_binary.mean() * 100
axs[1].bar(["<10k", "10-15k", "15-20k", "20-25k", "25-35k", "35-50k", "50-75k", ">75k"], inc.values, color=MID)
for ax, s, t in ((axs[0], g, "By self-rated general health"), (axs[1], inc, "By household income (US$)")):
    for i, v in enumerate(s.values): ax.text(i, v + 1, f"{v:.1f}", ha="center", fontsize=8)
    ax.set_ylim(0, 100); ax.set_ylabel("Diabetes share in balanced sample (%)"); ax.set_title(t, loc="left", fontweight="bold")
    ax.tick_params(axis="x", labelsize=8, rotation=20)
save("04_health_income_gradients.png")

# 5  slide 11: OLAP roll-up and pivot, computed straight from the warehouse
con = sqlite3.connect("review1/diabetes_dw.db")
ru = pd.read_sql("""SELECT d.age, ROUND(AVG(f.diabetes_binary)*100,2) AS pct FROM FACT_HEALTH_SURVEY f
                    JOIN DIM_DEMOGRAPHICS d ON f.demog_key=d.demog_key GROUP BY d.age ORDER BY d.age""", con)
pv = pd.read_sql("""SELECT d.age,
  SUM(CASE WHEN d.sex=0 THEN f.diabetes_binary ELSE 0 END) AS female,
  SUM(CASE WHEN d.sex=1 THEN f.diabetes_binary ELSE 0 END) AS male
  FROM FACT_HEALTH_SURVEY f JOIN DIM_DEMOGRAPHICS d ON f.demog_key=d.demog_key GROUP BY d.age ORDER BY d.age""", con)
band = ["18-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80+"]
fig, axs = plt.subplots(1, 2, figsize=(11, 4))
axs[0].bar(band, ru.pct, color=BLACK)
for i, v in enumerate(ru.pct): axs[0].text(i, v + 1, f"{v:.0f}", ha="center", fontsize=8)
axs[0].set_title("Roll-up: diabetes share (%) by age band", loc="left", fontweight="bold"); axs[0].set_ylabel("%")
xx = np.arange(13)
axs[1].bar(xx - 0.2, pv.female, 0.4, color=MID, label="Female"); axs[1].bar(xx + 0.2, pv.male, 0.4, color=BLACK, label="Male")
axs[1].set_xticks(xx, band); axs[1].legend(frameon=False)
axs[1].set_title("Pivot: diabetes cases by sex", loc="left", fontweight="bold"); axs[1].set_ylabel("Cases")
for ax in axs: ax.tick_params(axis="x", labelsize=8, rotation=45); ax.set_xlabel("Age band (years)")
save("05_olap_rollup_pivot.png")

# 6  slide 15: baseline AUC (needs review1/baseline_results.json from 06_feasibility_baseline.py)
p = "review1/baseline_results.json"
if os.path.exists(p):
    res = json.load(open(p))["balanced"]; names = list(res)
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    vals = [res[n]["auc"] for n in names]
    ax.barh(names[::-1], vals[::-1], color=BLACK)
    for i, v in enumerate(vals[::-1]): ax.text(v + 0.003, i, f"{v:.3f}", va="center", fontsize=9)
    ax.set_xlim(0.5, 0.9); ax.set_xlabel("AUC on held-out 30% (axis starts at 0.5 = chance)"); ax.grid(axis="y", visible=False)
    ax.set_title("Baseline models, balanced file", loc="left", fontweight="bold")
    save("06_baseline_auc.png")
else:
    print("skip chart 6: run 06_feasibility_baseline.py first")
print("charts saved in", OUT)
