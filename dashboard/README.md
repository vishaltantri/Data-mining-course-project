# BRFSS Diabetes Analytics Dashboard

An interactive **dark-theme** dashboard built on verified Review 1 and Review 2 artifacts. It visualizes saved outputs rather than silently retraining models.

## Run locally

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r dashboard/requirements.txt
.venv/bin/streamlit run dashboard/app.py
```

Open the printed local URL (normally http://localhost:8501).

## Dashboard sections

- **Executive Overview** — dataset KPIs, diabetes/no-diabetes risk-factor comparison, precision-vs-recall model map, and model-score heatmap.
- **Explore the Data** — age, sex, and income filters with age/health gradients, BMI distribution, and correlations.
- **Warehouse & OLAP** — actual Review 1 Roll-up, Drill-down, Slice, Dice, and Pivot output tables, dark interactive charts, CSV downloads, a custom query builder, and **The Cube (SQL)** — an interactive 3D OLAP cube whose every operation (Explore, Roll-up, Drill-down, Slice, Dice, Pivot) runs as real read-only SQL against `review1/diabetes_dw.db`, with the generated SQL and result set shown beside it.
- **Model Arena** — detailed comparison of accuracy, precision, recall, F1, and AUC; radar comparison; KNN k-selection; and CART importance.
- **Population Reality Check** — full-file threshold trade-offs, precision/recall/F1/accuracy comparison, and the always-No baseline.
- **Patterns & Clusters** — interactive Apriori rule filtering, K-Means cluster profiling, and a live PCA cluster explorer (choose features, k and sample size; re-plot hulls; edit or seed cluster centres).
- **My Health Profile** — one form, three views: a **risk gauge** (CART model fitted on the balanced sample, prior-adjusted to the population prevalence), a **cohort comparison** against matched BRFSS respondents, and the **cluster context** (nearest saved K-Means centroid, radar vs centroids, per-cluster diabetes share). It replaced the former duplicate *What-If Explorer* page.
- **Methods & Limitations** — reproducibility steps, provenance, and scope cautions.

## My Health Profile: scope and safety

The profile page accepts all 21 Review 2 predictors: the original nine-factor profile plus cholesterol checks, smoking, stroke, heart disease, fruit and vegetable intake, heavy alcohol use, health-care access, cost barriers, mental-health days, physical-health days, and education. It then shows three linked views: a **risk gauge**, a **cohort comparison** with matching BRFSS respondents, and **cluster context** against the saved K-Means centroids. The gauge reports both the all-parameter estimate and the original nine-factor check.

The gauge is a real model output: two decision trees (CART, scikit-learn, seed 42, depth 6) are fitted on the same balanced sample—one with the nine original factors and one with all 21 predictors. Because that sample is 50/50 by design, each raw probability is shifted onto the population odds (13.9% prevalence) with the standard prior-shift formula, which preserves the model's ranking of profiles. The held-out accuracy and both raw and adjusted numbers are printed on the *How this estimate is built* tab.

It is **not** a disease diagnosis, clinical-risk prediction, medical device, or medical advice, and the gauge bands are illustrative demo cut-points rather than clinical thresholds. The cohort panel remains a descriptive observed share inside a deliberately balanced research sample, and the cluster panel is a nearest-centroid comparison against saved aggregate profiles.

## Data sources

The app reads root-level BRFSS CSVs and already-generated artifacts under `review1/` and `review2/results/`. Preserve those paths when moving or deploying the dashboard.

## Important limitations

- The primary modeling file is deliberately balanced; it does not estimate population prevalence.
- The realistic-prevalence evaluation uses a separate split of the full data file.
- WEKA values use 10-fold cross-validation while R model values use a held-out split.
- Data are self-reported, cross-sectional, and limited to 2015; association is not causation.
- Some ROC/calibration data were not exported by the original scripts and are not fabricated by this interface.
