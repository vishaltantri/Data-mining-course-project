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
- **Warehouse & OLAP** — actual Review 1 Roll-up, Drill-down, Slice, Dice, and Pivot output tables, dark interactive charts, and CSV downloads.
- **Model Arena** — detailed comparison of accuracy, precision, recall, F1, and AUC; radar comparison; KNN k-selection; and CART importance.
- **Population Reality Check** — full-file threshold trade-offs, precision/recall/F1/accuracy comparison, and the always-No baseline.
- **Patterns & Clusters** — interactive Apriori rule filtering, K-Means cluster profiling, and a live PCA cluster explorer (choose features, k and sample size; re-plot hulls; edit or seed cluster centres).
- **My Health Profile** — user-entered factors compared descriptively with BRFSS cohorts, BMI distribution, and saved cluster context.
- **Methods & Limitations** — reproducibility steps, provenance, and scope cautions.

## My Health Profile: scope and safety

The profile page accepts an age band, sex, BMI, reported health factors, self-rated health, and income band. It then compares those entries with matching BRFSS respondents from the balanced survey sample.

It is **not** a disease diagnosis, clinical-risk prediction, medical device, or medical advice. The displayed diabetes share is an observed descriptive value within a comparison cohort from an intentionally balanced research sample—not the user’s probability and not population prevalence. The nearest-cluster display is only a distance comparison against saved aggregate cluster profiles.

## Data sources

The app reads root-level BRFSS CSVs and already-generated artifacts under `review1/` and `review2/results/`. Preserve those paths when moving or deploying the dashboard.

## Important limitations

- The primary modeling file is deliberately balanced; it does not estimate population prevalence.
- The realistic-prevalence evaluation uses a separate split of the full data file.
- WEKA values use 10-fold cross-validation while R model values use a held-out split.
- Data are self-reported, cross-sectional, and limited to 2015; association is not causation.
- Some ROC/calibration data were not exported by the original scripts and are not fabricated by this interface.
