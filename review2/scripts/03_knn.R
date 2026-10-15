################################################################################
# Review 2 — Phase C3: KNN Classification
# Script: 03_knn.R
# Purpose: Choose k via 5-fold CV on a sample, train final KNN, evaluate.
################################################################################

# ---- 0. Setup ----------------------------------------------------------------
library(class)
library(caret)
library(pROC)
set.seed(42)

cat(paste(rep("=", 70), collapse=""), "\n")
cat("REVIEW 2 — PHASE C3: KNN CLASSIFICATION\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")

# Load preprocessed data
load("review2/results/preprocessed.RData")
cat("Preprocessed data loaded.\n")

# Labels
y_train <- bal$Diabetes_binary[idx]
y_test  <- bal$Diabetes_binary[-idx]

cat("Training set:", nrow(tr_scaled), "rows\n")
cat("Test set:    ", nrow(te_scaled), "rows\n\n")

# Note about KNN and binary features
cat("NOTE: KNN treats all features (including binary 0/1 columns) as\n")
cat("continuous distances. After z-score scaling, binary features contribute\n")
cat("proportionally to the Euclidean distance alongside continuous features.\n\n")

# ---- 1. Choose k with 5-fold CV on a sample of ~10,000 training rows --------
cat(paste(rep("-", 60), collapse=""), "\n")
cat("Step 1: Choosing k via 5-fold Cross-Validation (sample of 10,000)\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

set.seed(42)
sample_idx <- sample(nrow(tr_scaled), min(10000, nrow(tr_scaled)))
sample_x   <- tr_scaled[sample_idx, ]
sample_y   <- y_train[sample_idx]

# Try odd k from 1 to 31
k_values <- seq(1, 31, by = 2)
cv_results <- data.frame(k = k_values, accuracy = numeric(length(k_values)))

# 5-fold CV
folds <- createFolds(sample_y, k = 5, list = TRUE, returnTrain = FALSE)

for (i in seq_along(k_values)) {
  k <- k_values[i]
  fold_accs <- numeric(5)

  for (f in 1:5) {
    fold_test_idx  <- folds[[f]]
    fold_train_idx <- setdiff(1:nrow(sample_x), fold_test_idx)

    fold_pred <- knn(train = sample_x[fold_train_idx, ],
                     test  = sample_x[fold_test_idx, ],
                     cl    = sample_y[fold_train_idx],
                     k     = k)
    fold_accs[f] <- mean(fold_pred == sample_y[fold_test_idx])
  }

  cv_results$accuracy[i] <- mean(fold_accs)
  cat(sprintf("  k = %2d: CV Accuracy = %.4f\n", k, cv_results$accuracy[i]))
}

# Best k
best_k <- cv_results$k[which.max(cv_results$accuracy)]
best_acc <- max(cv_results$accuracy)
cat(sprintf("\nBest k = %d (CV Accuracy = %.4f)\n\n", best_k, best_acc))

# Save CV results
write.csv(cv_results, "review2/results/knn_cv_results.csv", row.names = FALSE)

# ---- 2. Plot accuracy vs k --------------------------------------------------
png("review2/figures/04_knn_accuracy_vs_k.png", width = 800, height = 600, res = 120)
plot(cv_results$k, cv_results$accuracy,
     type = "b", pch = 19, col = "steelblue", lwd = 2,
     xlab = "k (Number of Neighbors)", ylab = "5-Fold CV Accuracy",
     main = "KNN: Accuracy vs k (5-Fold CV on 10,000 sample)")
abline(v = best_k, lty = 2, col = "red", lwd = 1.5)
text(best_k + 1, best_acc, sprintf("k=%d\nAcc=%.4f", best_k, best_acc),
     pos = 4, col = "red", cex = 0.9)
grid()
dev.off()
cat("k-vs-accuracy plot saved: review2/figures/04_knn_accuracy_vs_k.png\n\n")

# ---- 3. Train final KNN on full training set ---------------------------------
cat(paste(rep("-", 60), collapse=""), "\n")
cat(sprintf("Step 2: Training Final KNN (k = %d) on full training set\n", best_k))
cat(paste(rep("-", 60), collapse=""), "\n\n")

knn_pred <- knn(train = tr_scaled,
                test  = te_scaled,
                cl    = y_train,
                k     = best_k,
                prob  = TRUE)

# Probability of class "Yes" for each test row:
# knn's "prob" attribute is the winning-class vote share, so for rows
# predicted "No" the Yes probability is 1 - prob.
vote_share <- attr(knn_pred, "prob")
knn_prob_yes <- ifelse(knn_pred == "Yes", vote_share, 1 - vote_share)

# ---- 4. Evaluation -----------------------------------------------------------
cm_knn <- confusionMatrix(knn_pred, y_test, positive = "Yes")

cat("Confusion Matrix:\n")
print(cm_knn$table)
cat("\n")

acc_knn  <- cm_knn$overall["Accuracy"]
prec_knn <- cm_knn$byClass["Precision"]
rec_knn  <- cm_knn$byClass["Recall"]
f1_knn   <- cm_knn$byClass["F1"]

roc_knn <- roc(y_test, knn_prob_yes, levels = c("No", "Yes"),
               direction = "<", quiet = TRUE)
auc_knn <- as.numeric(auc(roc_knn))

cat(sprintf("Accuracy:  %.4f\n", acc_knn))
cat(sprintf("Precision: %.4f\n", prec_knn))
cat(sprintf("Recall:    %.4f\n", rec_knn))
cat(sprintf("F1 Score:  %.4f\n", f1_knn))
cat(sprintf("AUC:       %.4f\n\n", auc_knn))

# Save results
knn_metrics <- data.frame(
  Model = "KNN",
  k = best_k,
  Accuracy  = acc_knn,
  Precision = prec_knn,
  Recall    = rec_knn,
  F1        = f1_knn,
  AUC       = auc_knn
)
write.csv(knn_metrics, "review2/results/knn_metrics.csv", row.names = FALSE)

# Save model objects
save(knn_pred, cm_knn, best_k, cv_results, knn_metrics, roc_knn,
     file = "review2/results/knn_model.RData")

# ---- 5. Save console output -------------------------------------------------
sink("review2/results/03_knn_output.txt")
cat("REVIEW 2 — KNN CLASSIFICATION RESULTS\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")
cat("Cross-validation results (5-fold, 10,000 sample):\n")
print(cv_results)
cat(sprintf("\nBest k = %d\n\n", best_k))
cat("Full test set evaluation:\n")
cat("Confusion Matrix:\n")
print(cm_knn$table)
cat(sprintf("\nAccuracy: %.4f | Precision: %.4f | Recall: %.4f | F1: %.4f | AUC: %.4f\n",
            acc_knn, prec_knn, rec_knn, f1_knn, auc_knn))
cat("\nNote: KNN treats 0/1 binary columns as continuous distances after scaling.\n")
sink()
cat("Output saved to review2/results/03_knn_output.txt\n")

cat("\n")
cat(paste(rep("=", 70), collapse=""), "\n")
cat("KNN CLASSIFICATION COMPLETE\n")
cat(paste(rep("=", 70), collapse=""), "\n")
