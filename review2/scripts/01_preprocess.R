################################################################################
# Review 2 — Phase B: Preprocessing
# Script: 01_preprocess.R
# Purpose: Read balanced CSV, convert factors, bin BMI, stratified 70/30 split,
#          scale predictors for KNN/K-Means, and save split indices.
################################################################################

# ---- 0. Setup ----------------------------------------------------------------
library(caret)
set.seed(42)

cat(paste(rep("=", 70), collapse = ""), "\n")
cat("REVIEW 2 — PHASE B: PREPROCESSING\n")
cat(paste(rep("=", 70), collapse = ""), "\n\n")

# ---- 1. Read the balanced CSV -------------------------------------------------
bal <- read.csv("diabetes_binary_5050split_health_indicators_BRFSS2015.csv")
cat("Dataset loaded:", nrow(bal), "rows x", ncol(bal), "columns\n\n")

# ---- 2. Convert Diabetes_binary to factor with levels No/Yes ------------------
bal$Diabetes_binary <- factor(bal$Diabetes_binary,
                               levels = c(0, 1),
                               labels = c("No", "Yes"))
cat("Target variable distribution:\n")
print(table(bal$Diabetes_binary))
cat("\n")

# ---- 3. Convert ordinal columns to factors for decision tree & Apriori --------
# We keep a copy of the original numeric data for KNN/K-Means scaling
bal_numeric <- bal  # preserve numeric version

bal$GenHlth   <- factor(bal$GenHlth,   levels = 1:5,
                        labels = c("Excellent", "VeryGood", "Good", "Fair", "Poor"))
bal$Age       <- factor(bal$Age,       levels = 1:13)
bal$Education <- factor(bal$Education, levels = 1:6)
bal$Income    <- factor(bal$Income,    levels = 1:8)

cat("Factor conversions applied (GenHlth, Age, Education, Income)\n")
cat("str() of converted dataset:\n")
str(bal)
cat("\n")

# ---- 4. Bin BMI into WHO bands for Apriori -----------------------------------
bal$BMI_binned <- cut(bal$BMI,
                       breaks = c(-Inf, 18.5, 25, 30, Inf),
                       right = FALSE,
                       labels = c("Underweight", "Normal", "Overweight", "Obese"))
cat("BMI binning (WHO bands):\n")
print(table(bal$BMI_binned))
cat("\n")

# ---- 5. Stratified 70/30 split -----------------------------------------------
idx <- createDataPartition(bal$Diabetes_binary, p = 0.7, list = FALSE)
train <- bal[idx, ]
test  <- bal[-idx, ]

cat("Stratified 70/30 Split:\n")
cat("  Training set:", nrow(train), "rows\n")
cat("  Test set:    ", nrow(test),  "rows\n\n")

cat("Training set class balance:\n")
print(table(train$Diabetes_binary))
cat("  Proportions:", round(prop.table(table(train$Diabetes_binary)), 4), "\n\n")

cat("Test set class balance:\n")
print(table(test$Diabetes_binary))
cat("  Proportions:", round(prop.table(table(test$Diabetes_binary)), 4), "\n\n")

# ---- 6. Save split indices ---------------------------------------------------
write.csv(data.frame(row = as.vector(idx)),
          "review2/results/train_index.csv", row.names = FALSE)
cat("Train indices saved to review2/results/train_index.csv\n\n")

# ---- 7. Scale predictors for KNN and K-Means ---------------------------------
# Use ONLY the numeric version of the data; scale using training stats only
feat <- setdiff(names(bal_numeric), "Diabetes_binary")
tr_x <- bal_numeric[idx, feat]
te_x <- bal_numeric[-idx, feat]

pp <- preProcess(tr_x, method = c("center", "scale"))
tr_scaled <- predict(pp, tr_x)
te_scaled <- predict(pp, te_x)

cat("Scaling applied using training set means and SDs\n")
cat("Scaled training set dimensions:", nrow(tr_scaled), "x", ncol(tr_scaled), "\n")
cat("Scaled test set dimensions:    ", nrow(te_scaled), "x", ncol(te_scaled), "\n\n")

# Quick sanity check: training means should be ~0, SDs ~1
cat("Sanity check — Training set column means (should be ~0):\n")
print(round(colMeans(tr_scaled), 4))
cat("\nTraining set column SDs (should be ~1):\n")
print(round(apply(tr_scaled, 2, sd), 4))
cat("\n")

# ---- 8. Save preprocessed objects for downstream scripts ----------------------
save(bal, bal_numeric, train, test, idx, tr_scaled, te_scaled, pp, feat,
     file = "review2/results/preprocessed.RData")
cat("All preprocessed objects saved to review2/results/preprocessed.RData\n")

cat("\n")
cat(paste(rep("=", 70), collapse = ""), "\n")
cat("PREPROCESSING COMPLETE\n")
cat(paste(rep("=", 70), collapse = ""), "\n")

# ---- 9. Save console output --------------------------------------------------
sink("review2/results/01_preprocess_output.txt")
cat("REVIEW 2 — PHASE B: PREPROCESSING OUTPUT\n")
cat(paste(rep("=", 70), collapse = ""), "\n\n")
cat("Dataset:", nrow(bal), "rows x", ncol(bal), "columns\n\n")
cat("Target distribution:\n")
print(table(bal$Diabetes_binary))
cat("\nTrain rows:", nrow(train), "\n")
cat("Test rows: ", nrow(test), "\n\n")
cat("Train class balance:\n")
print(table(train$Diabetes_binary))
cat("\nTest class balance:\n")
print(table(test$Diabetes_binary))
cat("\nstr():\n")
str(bal)
cat("\nBMI binning:\n")
print(table(bal$BMI_binned))
sink()
cat("Output saved to review2/results/01_preprocess_output.txt\n")
