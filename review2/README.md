# Review 2 — Diabetes Risk Assessment & Cardiovascular Comorbidity Analysis

## Project: CDC BRFSS 2015 Data Mining

### Scripts (run in order from the repo root)

| # | Script | Phase | Description |
|---|--------|-------|-------------|
| 1 | `review2/scripts/01_preprocess.R` | B | Read balanced CSV, factor conversion, BMI binning, stratified 70/30 split, scaling |
| 2 | `review2/scripts/02_decision_tree.R` | C1-C2 | CART (Gini) and ID3-style (Information Gain) decision trees with pruning |
| 3 | `review2/scripts/03_knn.R` | C3 | KNN classification with k selection via 5-fold CV |
| 4 | `review2/scripts/04_realistic_eval.R` | D | Realistic-prevalence evaluation on full 253K file |
| 5 | `review2/scripts/05_apriori.R` | E | Apriori association rule mining with fixed RHS |
| 6 | `review2/scripts/06_clustering.R` | F | K-Means + Hierarchical clustering with profiling |
| 7 | `review2/scripts/07_final_comparison.R` | H | Final model comparison, results sheet, write-up |

### How to reproduce

```bash
# From the repo root:
Rscript review2/scripts/01_preprocess.R
Rscript review2/scripts/02_decision_tree.R
Rscript review2/scripts/03_knn.R
Rscript review2/scripts/04_realistic_eval.R
Rscript review2/scripts/05_apriori.R
Rscript review2/scripts/06_clustering.R
Rscript review2/scripts/07_final_comparison.R
```

### Required R packages

- `caret` — train/test split, preprocessing, confusion matrix
- `rpart` — CART / decision trees
- `rpart.plot` — tree visualization
- `pROC` — ROC curves and AUC
- `class` — KNN classification
- `arules` — Apriori association rule mining
- `cluster` — hierarchical clustering and silhouette
- `factoextra` — elbow plot, silhouette plot, cluster visualization
- `e1071` — support library for caret

Install all packages:
```r
install.packages(c("caret", "rpart", "rpart.plot", "pROC", "class",
                    "arules", "cluster", "factoextra", "e1071"))
```

### Output directories

- `review2/results/` — CSV tables, text outputs, RData model objects
- `review2/figures/` — PNG figures (tree plots, ROC curves, elbow, silhouette, dendrogram)
- `review2/weka/` — WEKA screenshots and exports
- `review2/screenshots/` — Console screenshots for the deck

### Generated Figures

| # | File | Description |
|---|------|-------------|
| 1 | `01_cart_pruned_tree.png` | Pruned CART decision tree plot |
| 2 | `02_cart_roc_curve.png` | ROC curve for CART model |
| 3 | `03_info_gain_pruned_tree.png` | Pruned information gain tree plot |
| 4 | `04_knn_accuracy_vs_k.png` | KNN accuracy vs k plot |
| 5 | `05_realistic_roc_curve.png` | ROC curve on realistic-prevalence data |
| 6 | `06_elbow_plot.png` | K-Means WSS elbow plot |
| 7 | `07_silhouette_plot.png` | Silhouette width plot |
| 8 | `08_kmeans_clusters.png` | K-Means cluster visualization (PCA projection) |
| 9 | `09_dendrogram.png` | Hierarchical clustering dendrogram |

### Seed

All scripts use `set.seed(42)` / `random_state=42`.

### Session Info

```
R version 4.5.2 (2025-10-31)
Platform: x86_64-pc-linux-gnu
Running under: Ubuntu 26.04 LTS

BLAS:   /usr/lib/x86_64-linux-gnu/blas/libblas.so.3.12.1
LAPACK: /usr/lib/x86_64-linux-gnu/lapack/liblapack.so.3.12.1; LAPACK version 3.12.0

Key packages:
  caret, rpart, rpart.plot, pROC, class, arules, cluster, factoextra, e1071, ggplot2
```
