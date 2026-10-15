# Review 2 — Master Checklist
**Project:** Diabetes Risk Assessment & Cardiovascular Comorbidity Analysis (CDC BRFSS 2015)
**Branch to work on:** create `review-2` from `review-1-brfss2015`

Tick each box as you go. When you finish a phase, copy the numbers into the **Results Sheet** (Section 10). When all phases are done, send me that sheet plus your screenshots and I'll build the Review 2 slides and speaker notes.

> The Review 2 content below comes from the "Planned for Review 2" rows in your `PROJECT_MASTER.md`. Check your Review 2 template and rubric for slide limits and marking, and adjust.

---

## 0. Ground rules (read once)

1. **Set a seed everywhere:** `set.seed(42)` in R, `random_state=42` in Python.
2. **Split first, then scale.** Learn means and standard deviations from the *training* set only, then apply them to the test set.
3. **Positive class = "Yes" (diabetes).** Report precision, recall, F1 and AUC for it, not just accuracy.
4. **Never test a model trained on the balanced file on the full file.** I checked: all 70,692 balanced rows exist in the full file, so training rows would leak into the test. For realistic-prevalence testing, split the *full* file separately (Phase 4).
5. **Quote numbers only from runs you did.** Don't copy numbers from my quick Python checks into slides as your results. Use them only as a rough range (AUC about 0.80–0.83 on the balanced file).
6. **Save every output** (text, CSV, figure) into the repo, so each slide number can be traced to a file.

---

## 1. Folder structure and Git setup

- [ ] Create the branch
  ```
  git checkout review-1-brfss2015
  git pull
  git checkout -b review-2
  ```
- [ ] Create folders
  ```
  review2/
    scripts/      (R and Python scripts, numbered)
    results/      (text and CSV outputs)
    figures/      (PNG images)
    weka/         (WEKA screenshots and exports)
    screenshots/  (console screenshots for the deck)
  ```
- [ ] Copy in the files from the earlier steps if not already there:
  - `review1/scripts/05_ppt_charts.py`, `06_feasibility_baseline.py`, `07_export_for_weka.py`
  - `review1/baseline_results.json`
  - the three generated files in `review1/weka/`

---

## 2. Phase A — Fix Review 1 loose ends (about half a day)

- [ ] Correct `PROJECT_MASTER.md`. These numbers were wrong:
  | Item | Wrong in file | Correct |
  |---|---|---|
  | Binary target | "prediabetes or diabetes" | Diagnosed diabetes only; 4,631 prediabetes are coded 0 |
  | Duplicates (full file) | 23,899 | 24,206 (9.5%) |
  | BMI > 50 | 572 | 923 (1.3%) |
  | Age 80+ share | 51.6% | 59.1% |
  | Slice "Excellent" / "Poor" | 26.9% / 78.4% | 34.7% / 83.4% |
  | Pivot sex claim | Male > female in bands 6–10 | Male leads only in bands 10–11 (ages 65–74) |
  | Q&A "Excellent" share | 10.8% | 13.8% |
- [ ] Add a short "Data provenance" paragraph: original BRFSS 2015 had 441,455 respondents and 330 columns. The Kaggle author cleaned it to 253,680 × 22. The exact steps are in the author's notebook (link from the Kaggle page).
- [ ] Add a "Limitations" note: the balanced sample is not population prevalence.

---

## 3. Phase B — Preprocessing (about 1 day)

**Script:** `review2/scripts/01_preprocess.R`

- [ ] Read the balanced CSV; convert `Diabetes_binary` to a factor with levels `No`, `Yes`.
- [ ] Convert `GenHlth`, `Age`, `Education`, `Income` to factors for the decision tree and Apriori.
- [ ] Bin BMI into WHO bands for Apriori: Underweight (<18.5), Normal (18.5–24.9), Overweight (25–29.9), Obese (≥30).
- [ ] Create the stratified 70/30 split with `caret::createDataPartition` and `set.seed(42)`.
- [ ] Save the split indices (`review2/results/train_index.csv`) so R and WEKA use identical data.
- [ ] For KNN and K-Means, scale all 21 predictors using training means and standard deviations only.
- [ ] Check the class balance of train and test (should be 50/50 in both).

**Screenshots:** `str()` and `table(train$Diabetes_binary)` output; the split sizes.
**Note down:** train rows (expected about 49,485) and test rows (about 21,207).

---

## 4. Phase C — Classification (about 2–3 days)

### C1. Decision tree, CART — `02_decision_tree.R`
- [ ] Build with `rpart(..., method="class", parms=list(split="gini"))` and a small `cp` (such as 0.001).
- [ ] Run `printcp()`; prune at the `cp` with the lowest cross-validated error.
- [ ] Plot the pruned tree with `rpart.plot`. Save it to `review2/figures/`.
- [ ] Test-set confusion matrix with `caret::confusionMatrix(..., positive="Yes")`.
- [ ] AUC with `pROC`.
- [ ] Variable importance: save `fit$variable.importance`.

### C2. ID3-style tree (information gain)
- [ ] Repeat C1 with `parms=list(split="information")`.
- [ ] Compare tree size and metrics with CART in one small table.

### C3. KNN — `03_knn.R`
- [ ] Choose k with 5-fold cross-validation on a **sample of about 10,000 training rows** (the full set is slow). Try odd k from 1 to 31.
- [ ] Plot accuracy against k and save it.
- [ ] Train the final KNN with the chosen k on the full training set (`class::knn` with the scaled data).
- [ ] Confusion matrix, precision, recall, F1.
- [ ] State in one sentence that KNN treats 0/1 columns as distances.

**Screenshots:** pruned tree plot; `printcp` table; confusion matrices; k-vs-accuracy plot.
**Note down:** accuracy, precision, recall, F1, AUC for each model; chosen `cp`; chosen k; the top 5 variables by importance.

---

## 5. Phase D — Realistic-prevalence evaluation (about 1 day)

This is your most interesting result, so don't skip it. On the balanced file, recall looked like 77–80%. In my quick check on the full file it fell to about 13–16% at a 0.5 threshold. You need to show this with your own R models.

**Script:** `review2/scripts/04_realistic_eval.R`

- [ ] Read the **full** file (253,680 rows). Make a *separate* stratified 70/30 split of it.
- [ ] Train the best decision tree on the full-file training set.
- [ ] Evaluate on the full-file test set (14% diabetes, as in real life).
- [ ] Report accuracy, precision, recall, F1, AUC.
- [ ] Try a lower threshold (for example 0.2, 0.3, 0.4) and show how recall and precision trade off. Save a small table.
- [ ] A baseline "always say No" model has about 86% accuracy. Report it so the audience sees why accuracy is misleading.

**Screenshots:** the threshold table.
**Note down:** metrics at 0.5 and at your chosen threshold; the "always No" accuracy.

---

## 6. Phase E — Association rules (about 1 day)

**Script:** `review2/scripts/05_apriori.R` (follow Experiment 5)

- [ ] Use only categorical columns plus binned BMI. Convert to `transactions` with `as(df, "transactions")`.
- [ ] Run `apriori` on a grid, for example support {0.05, 0.1, 0.2} and confidence {0.6, 0.7, 0.8}. Record the number of rules for each pair.
- [ ] Fix the right-hand side: `appearance = list(rhs = "Diabetes_binary=Yes")`.
- [ ] Sort by **lift**; remove redundant rules (`is.redundant`).
- [ ] Choose 5–8 readable rules, for example High BP + High cholesterol + age band → Diabetes.
- [ ] Note: on the balanced file, support reflects the 50/50 design, so say rules describe patterns in this sample.

**Screenshots:** `inspect(head(sort(rules, by="lift"), 10))`; the rule-count grid.
**Note down:** the grid table; the top 5 rules with support, confidence, lift.

---

## 7. Phase F — Clustering (about 1–2 days)

**Script:** `review2/scripts/06_clustering.R` (follow Experiment 7)

- [ ] Use the scaled predictors; **leave out** `Diabetes_binary`.
- [ ] Choose k with the elbow plot (`fviz_nbclust(..., "wss")`) and silhouette.
  - Silhouette on 70k rows is too slow: use a random sample of about 5,000 rows.
- [ ] Run `kmeans(centers = k, nstart = 25)` on all rows.
- [ ] For each cluster, report size, mean BMI, % high BP, % high cholesterol, mean age band, and **% with diabetes** (the label you held out).
- [ ] Hierarchical clustering with `hclust`: sample about 2,000–3,000 rows (it needs a full distance matrix), cut the dendrogram at the same k.
- [ ] Compare K-Means and hierarchical results in 2–3 lines (as in the Mixed Exercise).

**Screenshots:** elbow plot; silhouette plot; cluster profile table; dendrogram.
**Note down:** chosen k and why; the cluster profile table.

---

## 8. Phase G — WEKA (about half a day)

Use `review1/weka/diabetes_dw_export.arff` (made from your warehouse by `07_export_for_weka.py`).

- [ ] Preprocess tab: screenshot the loaded data (70,692 instances, 22 attributes).
- [ ] Classify tab → `trees.J48` with **10-fold cross-validation**. Screenshot the result panel.
- [ ] Classify tab → `bayes.NaiveBayes` with 10-fold cross-validation. Screenshot.
- [ ] Right-click each result → **Visualize threshold curve** (class Yes) → screenshot the ROC.
- [ ] Optionally: right-click the J48 result → **Visualize tree** → screenshot.
- [ ] Select attributes tab: `InfoGainAttributeEval` + `Ranker` → screenshot the ranked list.
- [ ] Compare WEKA J48 with your R decision tree in 2–3 lines.

**Note down:** accuracy, precision, recall, F1 and ROC area for J48 and Naive Bayes; the top 5 attributes by information gain.

---

## 9. Phase H — Final comparison and write-up (about 1–2 days)

- [ ] Fill the **comparison table** (Section 10) for all models on the same test set.
- [ ] Write 3–5 lines: which model is best, whether complex models beat simple ones, and what recall means for a screening tool.
- [ ] Write the limitations (copy from Review 1): balanced sample, prediabetes coded 0, self-reported single-year survey, association not causation.
- [ ] *(Optional, for your paper)* Evaluate the best model separately by age group (18–44, 45–64, 65+), income (low, mid, high) and sex. Report AUC and recall for each. Tell me the numbers and I'll add a slide.

---

## 10. Results Sheet — fill this in and send it to me

### 10.1 Setup
| Item | Value |
|---|---|
| Train / test rows (balanced) | |
| Seed | 42 |
| Chosen `cp` (CART) | |
| Chosen k (KNN) | |

### 10.2 Model comparison (balanced test set)
| Model | Accuracy | Precision | Recall | F1 | AUC |
|---|---|---|---|---|---|
| Decision tree, CART (R) | | | | | |
| Decision tree, information gain (R) | | | | | |
| KNN (R) | | | | | |
| J48 (WEKA, 10-fold CV) | | | | | |
| Naive Bayes (WEKA, 10-fold CV) | | | | | |

### 10.3 Realistic prevalence (full-file test set)
| Threshold | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| "Always No" baseline | | – | 0 | – |
| 0.5 | | | | |
| 0.3 (or your choice) | | | | |

### 10.4 Association rules
| # | Rule | Support | Confidence | Lift |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

### 10.5 Clustering
| Cluster | Size | Mean BMI | % High BP | % High Chol | % Diabetes |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

### 10.6 Also send
- [ ] All screenshots from Phases B–G
- [ ] The saved figures from `review2/figures/`
- [ ] Anything that surprised you or didn't work
- [ ] Your Review 2 template and rubric, if you have them

---

## 11. GitHub push checklist

- [ ] Every script runs from the repo root without editing paths.
- [ ] Every figure in the slides has a script that creates it.
- [ ] `review2/README.md` lists: the scripts in order, the packages needed, and the exact commands to reproduce each result.
- [ ] Commit in small steps:
  ```
  git add review2
  git commit -m "Review 2: preprocessing and decision tree"
  git push origin review-2
  ```
- [ ] Don't commit large files that don't need to be there (the three raw CSVs are already in the repo; avoid adding copies).
- [ ] Note any package versions: run `sessionInfo()` in R and paste it into the README.

---

## 12. Common mistakes to avoid

| Mistake | Why it matters |
|---|---|
| Scaling before splitting | Leaks test information into training |
| Testing the balanced-trained model on the full file | Training rows are in the full file, so results are inflated |
| Reporting only accuracy | On real data, "always No" scores 86% |
| Running silhouette or `hclust` on all 70k rows | Runs out of memory or takes hours |
| Different splits in R and WEKA | Results can't be compared |
| Using the Python numbers from my check as your results | They aren't from your R runs |
| Claiming "diabetes causes heart disease" | The data is a one-time survey: say "associated with" |

---

## 13. Starter R code (untested — adjust and run yourself)

I couldn't run R in my environment, so treat these as starting points and fix any errors.

**Preprocessing and split**
```r
library(caret)
set.seed(42)
bal <- read.csv("diabetes_binary_5050split_health_indicators_BRFSS2015.csv")
bal$Diabetes_binary <- factor(bal$Diabetes_binary, levels = c(0, 1), labels = c("No", "Yes"))
idx <- createDataPartition(bal$Diabetes_binary, p = 0.7, list = FALSE)
train <- bal[idx, ]; test <- bal[-idx, ]
table(train$Diabetes_binary); table(test$Diabetes_binary)
write.csv(data.frame(row = as.vector(idx)), "review2/results/train_index.csv", row.names = FALSE)
```

**CART with pruning**
```r
library(rpart); library(rpart.plot); library(pROC)
fit <- rpart(Diabetes_binary ~ ., data = train, method = "class",
             parms = list(split = "gini"), control = rpart.control(cp = 0.001))
printcp(fit)
best_cp <- fit$cptable[which.min(fit$cptable[, "xerror"]), "CP"]
pruned <- prune(fit, cp = best_cp)
rpart.plot(pruned)
pred <- predict(pruned, test, type = "class")
confusionMatrix(pred, test$Diabetes_binary, positive = "Yes")
prob <- predict(pruned, test, type = "prob")[, "Yes"]
auc(roc(test$Diabetes_binary, prob))
```
For the information-gain version, change `split = "gini"` to `split = "information"`.

**KNN (scale with training statistics)**
```r
library(class); library(caret)
num <- read.csv("diabetes_binary_5050split_health_indicators_BRFSS2015.csv")
y <- bal$Diabetes_binary
feat <- setdiff(names(num), "Diabetes_binary")
tr_x <- num[idx, feat]; te_x <- num[-idx, feat]
pp <- preProcess(tr_x, method = c("center", "scale"))
tr_s <- predict(pp, tr_x); te_s <- predict(pp, te_x)
pred <- knn(tr_s, te_s, cl = y[idx], k = 15)      # replace 15 with your cross-validated k
confusionMatrix(pred, y[-idx], positive = "Yes")
```

**Apriori with a fixed right-hand side**
```r
library(arules)
df <- bal   # use factors only; bin BMI first with cut()
df$BMI <- cut(df$BMI, c(0, 18.5, 25, 30, Inf), right = FALSE,
              labels = c("Underweight", "Normal", "Overweight", "Obese"))
df$MentHlth <- NULL; df$PhysHlth <- NULL        # or bin them too
df[] <- lapply(df, as.factor)
trans <- as(df, "transactions")
rules <- apriori(trans, parameter = list(supp = 0.05, conf = 0.7, minlen = 2),
                 appearance = list(rhs = "Diabetes_binary=Yes", default = "lhs"))
rules <- sort(rules[!is.redundant(rules)], by = "lift")
inspect(head(rules, 10))
```

**K-Means with a sampled silhouette**
```r
library(cluster); library(factoextra)
X <- predict(pp, num[, feat])                    # scaled predictors, label excluded
set.seed(42)
s <- X[sample(nrow(X), 5000), ]
fviz_nbclust(s, kmeans, method = "wss")
fviz_nbclust(s, kmeans, method = "silhouette")
km <- kmeans(X, centers = 3, nstart = 25)        # replace 3 with your chosen k
aggregate(as.numeric(y == "Yes"), by = list(cluster = km$cluster), FUN = mean)
```

---

## 14. Review 3 / paper (provisional — confirm with your faculty)

Nothing in the repo describes Review 3, so this is a guess at a final review:

- [ ] Tune the best models (hyperparameters, feature selection, class weights).
- [ ] Final comparison with confidence intervals and a significance test between the top two models.
- [ ] Realistic-prevalence evaluation and subgroup analysis by age, income and sex.
- [ ] Optional demo (for example an R Shiny risk screener).
- [ ] Final report or paper draft, final deck, and a clean README that reproduces every result.

When Review 2 is done, send me the Results Sheet and screenshots, and I'll build the slides, speaker notes and observations.
