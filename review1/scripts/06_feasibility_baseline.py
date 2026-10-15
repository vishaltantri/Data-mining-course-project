#!/usr/bin/env python3
"""Review 1 — feasibility baselines (quick sanity check, random_state=42).

Run from the repository root:   python3 review1/scripts/06_feasibility_baseline.py
Reads : diabetes_binary_5050split_health_indicators_BRFSS2015.csv,
        diabetes_binary_health_indicators_BRFSS2015.csv
Writes: review1/baseline_results.json  (consumed by 05_ppt_charts.py)

NOTE: These are quick Python checks used only to confirm the problem is
solvable (AUC ~0.80-0.83 on the balanced file). They are NOT the reported
Review 2 results - those come from the R scripts in review2/scripts/.
"""
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

SEED = 42
BAL = "diabetes_binary_5050split_health_indicators_BRFSS2015.csv"
FULL = "diabetes_binary_health_indicators_BRFSS2015.csv"
OUT = "review1/baseline_results.json"

bal = pd.read_csv(BAL)
full = pd.read_csv(FULL)

X = bal.drop(columns=["Diabetes_binary"])
y = bal["Diabetes_binary"].astype(int)

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.30,
                                          random_state=SEED, stratify=y)
scaler = StandardScaler().fit(X_tr)
X_tr_s = scaler.transform(X_tr)
X_te_s = scaler.transform(X_te)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=SEED),
    "Decision Tree": DecisionTreeClassifier(random_state=SEED),
    "KNN (k=15)": KNeighborsClassifier(n_neighbors=15),
}

balanced = {}
for name, m in models.items():
    m.fit(X_tr_s, y_tr)
    pred = m.predict(X_te_s)
    prob = m.predict_proba(X_te_s)[:, 1]
    balanced[name] = {
        "accuracy": round(float(accuracy_score(y_te, pred)), 4),
        "precision": round(float(precision_score(y_te, pred)), 4),
        "recall": round(float(recall_score(y_te, pred)), 4),
        "f1": round(float(f1_score(y_te, pred)), 4),
        "auc": round(float(roc_auc_score(y_te, prob)), 4),
    }
    print(f"{name:22s} acc={balanced[name]['accuracy']:.4f} "
          f"prec={balanced[name]['precision']:.4f} rec={balanced[name]['recall']:.4f} "
          f"f1={balanced[name]['f1']:.4f} auc={balanced[name]['auc']:.4f}")

always_no = float((full["Diabetes_binary"] == 0).mean())
print(f'"Always No" accuracy on full file: {always_no:.4f}')

results = {
    "seed": SEED,
    "train_rows": int(len(X_tr)),
    "test_rows": int(len(X_te)),
    "balanced": balanced,
    "full_file": {
        "rows": int(len(full)),
        "prevalence": round(float(full["Diabetes_binary"].mean()), 4),
        "always_no_accuracy": round(always_no, 4),
    },
    "note": "Quick feasibility check only; Review 2 reported numbers come from the R scripts in review2/scripts/.",
}

with open(OUT, "w") as f:
    json.dump(results, f, indent=2)
print(f"Saved {OUT}")
