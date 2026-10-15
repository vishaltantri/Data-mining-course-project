################################################################################
# Review 2 — Phase D: Realistic-Prevalence Evaluation
# Script: 04_realistic_eval.R
# Purpose: Train best decision tree on full file (253,680 rows),
#          evaluate at real-world prevalence (~14% diabetes),
#          show threshold trade-offs, and "always No" baseline.
################################################################################

# ---- 0. Setup ----------------------------------------------------------------
library(rpart)
library(rpart.plot)
library(caret)
library(pROC)
set.seed(42)

cat(paste(rep("=", 70), collapse=""), "\n")
cat("REVIEW 2 — PHASE D: REALISTIC-PREVALENCE EVALUATION\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")

# ---- 1. Read the FULL file (253,680 rows) ------------------------------------
full <- read.csv("diabetes_binary_health_indicators_BRFSS2015.csv")
full$Diabetes_binary <- factor(full$Diabetes_binary,
                                levels = c(0, 1),
                                labels = c("No", "Yes"))

cat("Full dataset loaded:", nrow(full), "rows x", ncol(full), "columns\n")
cat("Full dataset class distribution:\n")
print(table(full$Diabetes_binary))
cat("  Proportions:", round(prop.table(table(full$Diabetes_binary)), 4), "\n\n")

# ---- 2. Separate stratified 70/30 split of the full file ---------------------
full_idx <- createDataPartition(full$Diabetes_binary, p = 0.7, list = FALSE)
full_train <- full[full_idx, ]
full_test  <- full[-full_idx, ]

cat("Full-file stratified 70/30 split:\n")
cat("  Training set:", nrow(full_train), "rows\n")
cat("  Test set:    ", nrow(full_test),  "rows\n\n")

cat("Full-file test set class distribution:\n")
print(table(full_test$Diabetes_binary))
cat("  Proportions:", round(prop.table(table(full_test$Diabetes_binary)), 4), "\n\n")

# ---- 3. Train the best decision tree (CART) on full-file training set --------
cat(paste(rep("-", 60), collapse=""), "\n")
cat("Training CART decision tree on full-file training set...\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

fit_full <- rpart(Diabetes_binary ~ ., data = full_train,
                   method = "class",
                   parms = list(split = "gini"),
                   control = rpart.control(cp = 0.001))

best_cp_full <- fit_full$cptable[which.min(fit_full$cptable[, "xerror"]), "CP"]
pruned_full <- prune(fit_full, cp = best_cp_full)

cat(sprintf("Best CP: %.6f\n", best_cp_full))
cat(sprintf("Tree size: %d terminal nodes\n\n",
            sum(pruned_full$frame$var == "<leaf>")))

# ---- 4. Evaluate at default threshold (0.5) ----------------------------------
pred_class_05 <- predict(pruned_full, full_test, type = "class")
pred_prob     <- predict(pruned_full, full_test, type = "prob")[, "Yes"]

cm_05 <- confusionMatrix(pred_class_05, full_test$Diabetes_binary, positive = "Yes")
roc_full <- roc(full_test$Diabetes_binary, pred_prob,
                levels = c("No", "Yes"), direction = "<", quiet = TRUE)
auc_full <- auc(roc_full)

cat("Evaluation at threshold = 0.5:\n")
print(cm_05$table)
cat(sprintf("\nAccuracy: %.4f | Precision: %.4f | Recall: %.4f | F1: %.4f | AUC: %.4f\n\n",
            cm_05$overall["Accuracy"],
            cm_05$byClass["Precision"],
            cm_05$byClass["Recall"],
            cm_05$byClass["F1"],
            auc_full))

# ---- 5. "Always say No" baseline --------------------------------------------
always_no_acc <- sum(full_test$Diabetes_binary == "No") / nrow(full_test)
cat(sprintf("\"Always No\" baseline accuracy: %.4f (%.1f%%)\n\n",
            always_no_acc, always_no_acc * 100))

# ---- 6. Threshold trade-off table -------------------------------------------
cat(paste(rep("-", 60), collapse=""), "\n")
cat("Threshold Trade-Off Analysis\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

thresholds <- c(0.2, 0.3, 0.4, 0.5)
threshold_results <- data.frame(
  Threshold = numeric(),
  Accuracy  = numeric(),
  Precision = numeric(),
  Recall    = numeric(),
  F1        = numeric()
)

for (t in thresholds) {
  pred_t <- factor(ifelse(pred_prob >= t, "Yes", "No"),
                    levels = c("No", "Yes"))
  cm_t <- confusionMatrix(pred_t, full_test$Diabetes_binary, positive = "Yes")

  acc_t  <- cm_t$overall["Accuracy"]
  prec_t <- cm_t$byClass["Precision"]
  rec_t  <- cm_t$byClass["Recall"]
  f1_t   <- cm_t$byClass["F1"]

  threshold_results <- rbind(threshold_results,
    data.frame(Threshold = t, Accuracy = acc_t, Precision = prec_t,
               Recall = rec_t, F1 = f1_t))

  cat(sprintf("  Threshold = %.1f: Acc=%.4f  Prec=%.4f  Rec=%.4f  F1=%.4f\n",
              t, acc_t, prec_t, rec_t, f1_t))
}

# Add the "Always No" row
threshold_results <- rbind(
  data.frame(Threshold = NA, Accuracy = always_no_acc,
             Precision = NA, Recall = 0, F1 = NA),
  threshold_results
)

cat(sprintf("\n\"Always No\" baseline: Acc=%.4f  Prec=NA  Rec=0  F1=NA\n\n", always_no_acc))

# Save threshold table
write.csv(threshold_results, "review2/results/threshold_tradeoff.csv", row.names = FALSE)
cat("Threshold table saved to review2/results/threshold_tradeoff.csv\n\n")

# ---- 7. ROC curve for realistic prevalence -----------------------------------
png("review2/figures/05_realistic_roc_curve.png", width = 800, height = 600, res = 120)
plot(roc_full, main = "ROC Curve — Realistic Prevalence (Full File)",
     col = "darkred", lwd = 2)
abline(a = 0, b = 1, lty = 2, col = "gray")
legend("bottomright",
       legend = sprintf("AUC = %.4f", auc_full),
       col = "darkred", lwd = 2)
dev.off()
cat("ROC curve saved: review2/figures/05_realistic_roc_curve.png\n")

# ---- Save console output ----------------------------------------------------
sink("review2/results/04_realistic_eval_output.txt")
cat("REVIEW 2 — REALISTIC-PREVALENCE EVALUATION\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")
cat(sprintf("Full dataset: %d rows\n", nrow(full)))
cat(sprintf("Full training: %d rows | Full test: %d rows\n\n",
            nrow(full_train), nrow(full_test)))
cat("Test set class distribution:\n")
print(table(full_test$Diabetes_binary))
cat(sprintf("\n\"Always No\" baseline accuracy: %.4f\n\n", always_no_acc))
cat("Threshold trade-off table:\n")
print(threshold_results, row.names = FALSE)
cat(sprintf("\nAUC: %.4f\n", auc_full))
sink()
cat("Output saved to review2/results/04_realistic_eval_output.txt\n")

# Save model objects
save(pruned_full, roc_full, auc_full, threshold_results, always_no_acc,
     file = "review2/results/realistic_eval_models.RData")

cat("\n")
cat(paste(rep("=", 70), collapse=""), "\n")
cat("REALISTIC-PREVALENCE EVALUATION COMPLETE\n")
cat(paste(rep("=", 70), collapse=""), "\n")
