################################################################################
# Review 2 — Phase C1 & C2: Decision Tree Classification
# Script: 02_decision_tree.R
# Purpose: CART (Gini) and ID3-style (Information Gain) decision trees
#          with pruning, evaluation, and variable importance.
################################################################################

# ---- 0. Setup ----------------------------------------------------------------
library(rpart)
library(rpart.plot)
library(caret)
library(pROC)
set.seed(42)

cat(paste(rep("=", 70), collapse=""), "\n")
cat("REVIEW 2 — PHASE C: DECISION TREE CLASSIFICATION\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")

# Load preprocessed data
load("review2/results/preprocessed.RData")
cat("Preprocessed data loaded.\n")
cat("Training set:", nrow(train), "rows | Test set:", nrow(test), "rows\n\n")

# ---- Helper function for evaluation ------------------------------------------
evaluate_tree <- function(model, test_data, model_name) {
  cat(paste(rep("-", 60), collapse=""), "\n")
  cat("Model:", model_name, "\n")
  cat(paste(rep("-", 60), collapse=""), "\n\n")

  # Predictions
  pred_class <- predict(model, test_data, type = "class")
  pred_prob  <- predict(model, test_data, type = "prob")[, "Yes"]

  # Confusion matrix
  cm <- confusionMatrix(pred_class, test_data$Diabetes_binary, positive = "Yes")
  cat("Confusion Matrix:\n")
  print(cm$table)
  cat("\n")

  # Key metrics
  acc  <- cm$overall["Accuracy"]
  prec <- cm$byClass["Precision"]
  rec  <- cm$byClass["Recall"]
  f1   <- cm$byClass["F1"]

  cat(sprintf("Accuracy:  %.4f\n", acc))
  cat(sprintf("Precision: %.4f\n", prec))
  cat(sprintf("Recall:    %.4f\n", rec))
  cat(sprintf("F1 Score:  %.4f\n", f1))

  # AUC
  roc_obj <- roc(test_data$Diabetes_binary, pred_prob, levels = c("No", "Yes"),
                  direction = "<", quiet = TRUE)
  auc_val <- auc(roc_obj)
  cat(sprintf("AUC:       %.4f\n\n", auc_val))

  return(list(cm = cm, roc = roc_obj, auc = auc_val,
              accuracy = acc, precision = prec, recall = rec, f1 = f1))
}

# ==============================================================================
# C1. CART (Gini) Decision Tree
# ==============================================================================
cat("\n")
cat(paste(rep("=", 70), collapse=""), "\n")
cat("C1. CART DECISION TREE (GINI IMPURITY)\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")

# Build unpruned tree with small cp
fit_gini <- rpart(Diabetes_binary ~ . - BMI_binned, data = train,
                   method = "class",
                   parms = list(split = "gini"),
                   control = rpart.control(cp = 0.001))

# Print cp table
cat("CP Table (CART/Gini):\n")
printcp(fit_gini)
cat("\n")

# Find best cp (lowest cross-validated error)
best_cp_gini <- fit_gini$cptable[which.min(fit_gini$cptable[, "xerror"]), "CP"]
cat(sprintf("Best CP (lowest xerror): %.6f\n\n", best_cp_gini))

# Prune the tree
pruned_gini <- prune(fit_gini, cp = best_cp_gini)
cat(sprintf("Pruned tree size: %d terminal nodes\n\n",
            sum(pruned_gini$frame$var == "<leaf>")))

# Plot the pruned tree
png("review2/figures/01_cart_pruned_tree.png", width = 1200, height = 800, res = 120)
rpart.plot(pruned_gini, main = "CART Decision Tree (Gini) — Pruned",
           extra = 104, under = TRUE, faclen = 0, cex = 0.7)
dev.off()
cat("Pruned tree plot saved: review2/figures/01_cart_pruned_tree.png\n\n")

# Evaluate on test set
results_gini <- evaluate_tree(pruned_gini, test, "CART (Gini) — Pruned")

# Variable importance
cat("Variable Importance (CART/Gini):\n")
vi_gini <- sort(pruned_gini$variable.importance, decreasing = TRUE)
print(round(vi_gini, 2))
cat("\nTop 5 variables:\n")
print(names(vi_gini)[1:min(5, length(vi_gini))])
cat("\n")

# Save variable importance
write.csv(data.frame(Variable = names(vi_gini), Importance = as.numeric(vi_gini)),
          "review2/results/cart_variable_importance.csv", row.names = FALSE)

# ROC curve plot
png("review2/figures/02_cart_roc_curve.png", width = 800, height = 600, res = 120)
plot(results_gini$roc, main = "ROC Curve — CART (Gini)", col = "steelblue", lwd = 2)
abline(a = 0, b = 1, lty = 2, col = "gray")
legend("bottomright",
       legend = sprintf("AUC = %.4f", results_gini$auc),
       col = "steelblue", lwd = 2)
dev.off()
cat("ROC curve saved: review2/figures/02_cart_roc_curve.png\n\n")

# ==============================================================================
# C2. ID3-style Decision Tree (Information Gain)
# ==============================================================================
cat(paste(rep("=", 70), collapse=""), "\n")
cat("C2. DECISION TREE (INFORMATION GAIN)\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")

# Build with information gain
fit_info <- rpart(Diabetes_binary ~ . - BMI_binned, data = train,
                   method = "class",
                   parms = list(split = "information"),
                   control = rpart.control(cp = 0.001))

# CP table
cat("CP Table (Information Gain):\n")
printcp(fit_info)
cat("\n")

# Best cp
best_cp_info <- fit_info$cptable[which.min(fit_info$cptable[, "xerror"]), "CP"]
cat(sprintf("Best CP (lowest xerror): %.6f\n\n", best_cp_info))

# Prune
pruned_info <- prune(fit_info, cp = best_cp_info)
cat(sprintf("Pruned tree size: %d terminal nodes\n\n",
            sum(pruned_info$frame$var == "<leaf>")))

# Plot
png("review2/figures/03_info_gain_pruned_tree.png", width = 1200, height = 800, res = 120)
rpart.plot(pruned_info, main = "Decision Tree (Information Gain) — Pruned",
           extra = 104, under = TRUE, faclen = 0, cex = 0.7)
dev.off()
cat("Pruned tree plot saved: review2/figures/03_info_gain_pruned_tree.png\n\n")

# Evaluate
results_info <- evaluate_tree(pruned_info, test, "Information Gain — Pruned")

# Variable importance
cat("Variable Importance (Information Gain):\n")
vi_info <- sort(pruned_info$variable.importance, decreasing = TRUE)
print(round(vi_info, 2))
cat("\n")

# ==============================================================================
# COMPARISON TABLE
# ==============================================================================
cat(paste(rep("=", 70), collapse=""), "\n")
cat("COMPARISON: CART vs INFORMATION GAIN\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")

comparison <- data.frame(
  Model = c("CART (Gini)", "Information Gain"),
  Best_CP = c(best_cp_gini, best_cp_info),
  Tree_Size = c(sum(pruned_gini$frame$var == "<leaf>"),
                sum(pruned_info$frame$var == "<leaf>")),
  Accuracy  = c(results_gini$accuracy, results_info$accuracy),
  Precision = c(results_gini$precision, results_info$precision),
  Recall    = c(results_gini$recall, results_info$recall),
  F1        = c(results_gini$f1, results_info$f1),
  AUC       = c(results_gini$auc, results_info$auc)
)
print(comparison, digits = 4)

# Save comparison
write.csv(comparison, "review2/results/decision_tree_comparison.csv", row.names = FALSE)
cat("\nComparison saved to review2/results/decision_tree_comparison.csv\n")

# Save all tree objects
save(fit_gini, pruned_gini, fit_info, pruned_info,
     results_gini, results_info, best_cp_gini, best_cp_info, comparison,
     file = "review2/results/decision_tree_models.RData")
cat("Model objects saved to review2/results/decision_tree_models.RData\n")

# ---- Save console output ----------------------------------------------------
sink("review2/results/02_decision_tree_output.txt")
cat("REVIEW 2 — DECISION TREE RESULTS\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")

cat("C1. CART (Gini)\n")
cat(sprintf("Best CP: %.6f\n", best_cp_gini))
cat(sprintf("Tree size: %d terminal nodes\n\n",
            sum(pruned_gini$frame$var == "<leaf>")))
cat("Confusion Matrix:\n")
print(results_gini$cm$table)
cat(sprintf("\nAccuracy: %.4f | Precision: %.4f | Recall: %.4f | F1: %.4f | AUC: %.4f\n\n",
            results_gini$accuracy, results_gini$precision,
            results_gini$recall, results_gini$f1, results_gini$auc))
cat("Variable Importance:\n")
print(round(vi_gini, 2))

cat("\n\nC2. Information Gain\n")
cat(sprintf("Best CP: %.6f\n", best_cp_info))
cat(sprintf("Tree size: %d terminal nodes\n\n",
            sum(pruned_info$frame$var == "<leaf>")))
cat("Confusion Matrix:\n")
print(results_info$cm$table)
cat(sprintf("\nAccuracy: %.4f | Precision: %.4f | Recall: %.4f | F1: %.4f | AUC: %.4f\n\n",
            results_info$accuracy, results_info$precision,
            results_info$recall, results_info$f1, results_info$auc))
cat("Variable Importance:\n")
print(round(vi_info, 2))

cat("\n\nComparison:\n")
print(comparison, digits = 4)
sink()
cat("Output saved to review2/results/02_decision_tree_output.txt\n")

cat("\n")
cat(paste(rep("=", 70), collapse=""), "\n")
cat("DECISION TREE CLASSIFICATION COMPLETE\n")
cat(paste(rep("=", 70), collapse=""), "\n")
