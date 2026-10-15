################################################################################
# Review 2 — Phase H: Final Comparison and Write-Up
# Script: 07_final_comparison.R
# Purpose: Compile metrics from all models, generate comparison table,
#          and produce summary write-up for the Results Sheet.
################################################################################

# ---- 0. Setup ----------------------------------------------------------------
set.seed(42)

cat(paste(rep("=", 70), collapse=""), "\n")
cat("REVIEW 2 — PHASE H: FINAL COMPARISON AND WRITE-UP\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")

# ---- 1. Load all model results -----------------------------------------------
load("review2/results/decision_tree_models.RData")
load("review2/results/knn_model.RData")
load("review2/results/realistic_eval_models.RData")
load("review2/results/apriori_models.RData")
load("review2/results/clustering_models.RData")
load("review2/results/preprocessed.RData")

cat("All model results loaded.\n\n")

# ---- 2. Section 10.1 — Setup ------------------------------------------------
cat(paste(rep("=", 70), collapse=""), "\n")
cat("10.1 SETUP\n")
cat(paste(rep("-", 60), collapse=""), "\n")
cat(sprintf("Train rows (balanced): %d\n", nrow(train)))
cat(sprintf("Test rows (balanced):  %d\n", nrow(test)))
cat(sprintf("Seed: 42\n"))

dt_comp <- read.csv("review2/results/decision_tree_comparison.csv")
knn_met <- read.csv("review2/results/knn_metrics.csv")

cat(sprintf("Chosen cp (CART):    %.6f\n", dt_comp$Best_CP[1]))
cat(sprintf("Chosen cp (InfoGain): %.6f\n", dt_comp$Best_CP[2]))
cat(sprintf("Chosen k (KNN):      %d\n\n", knn_met$k[1]))

# ---- 3. Section 10.2 — Model comparison (balanced test set) -----------------
cat(paste(rep("=", 70), collapse=""), "\n")
cat("10.2 MODEL COMPARISON (BALANCED TEST SET)\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

comparison_table <- data.frame(
  Model = c("Decision Tree, CART (R)",
            "Decision Tree, Information Gain (R)",
            "KNN (R)",
            "J48 (WEKA, 10-fold CV)",
            "Naive Bayes (WEKA, 10-fold CV)"),
  Accuracy  = c(dt_comp$Accuracy[1],  dt_comp$Accuracy[2],  knn_met$Accuracy,
                0.7213, 0.7074),
  Precision = c(dt_comp$Precision[1], dt_comp$Precision[2], knn_met$Precision,
                0.7120, 0.7420),
  Recall    = c(dt_comp$Recall[1],    dt_comp$Recall[2],    knn_met$Recall,
                0.7420, 0.6360),
  F1        = c(dt_comp$F1[1],        dt_comp$F1[2],        knn_met$F1,
                0.7270, 0.6850),
  AUC       = c(dt_comp$AUC[1],       dt_comp$AUC[2],       knn_met$AUC,
                0.7460, 0.7970)
)

# Round for display
comparison_display <- comparison_table
comparison_display[, 2:6] <- round(comparison_display[, 2:6], 4)

print(comparison_display, row.names = FALSE)
cat("\n")


# ---- 4. Section 10.3 — Realistic prevalence ---------------------------------
cat(paste(rep("=", 70), collapse=""), "\n")
cat("10.3 REALISTIC PREVALENCE (FULL-FILE TEST SET)\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

thresh_table <- read.csv("review2/results/threshold_tradeoff.csv")
print(thresh_table, row.names = FALSE)
cat("\n")

# ---- 5. Section 10.4 — Association rules ------------------------------------
cat(paste(rep("=", 70), collapse=""), "\n")
cat("10.4 ASSOCIATION RULES (TOP 5)\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

top_rules_df <- read.csv("review2/results/apriori_top_rules.csv")
print(head(top_rules_df, 5), row.names = FALSE)
cat("\n")

# ---- 6. Section 10.5 — Clustering -------------------------------------------
cat(paste(rep("=", 70), collapse=""), "\n")
cat("10.5 CLUSTERING\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

clust_prof <- read.csv("review2/results/cluster_profiles.csv")
print(round(clust_prof, 2), row.names = FALSE)
cat("\n")

# ---- 7. Write-up (3-5 lines) ------------------------------------------------
cat(paste(rep("=", 70), collapse=""), "\n")
cat("WRITE-UP (3-5 LINES)\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

best_model <- comparison_table$Model[which.max(comparison_table$F1)]
best_f1 <- max(comparison_table$F1)
best_auc <- comparison_table$AUC[which.max(comparison_table$F1)]

cat(sprintf("1. Best model: %s (F1 = %.4f, AUC = %.4f on balanced test set).\n",
            best_model, best_f1, best_auc))
cat("2. All three R models perform similarly (~73-74% accuracy), suggesting\n")
cat("   that the signal in these 21 survey features has a natural ceiling.\n")
cat("   KNN achieved the highest AUC, likely because it captures non-linear\n")
cat("   local patterns missed by single decision trees.\n")
cat("3. On realistic-prevalence data (14% diabetes), recall at the default\n")
cat("   0.5 threshold drops below 11%, because the model rarely predicts the\n")
cat("   rare class. Lowering the threshold to 0.2 raises recall to ~61% but\n")
cat("   precision falls to ~32%. A screening tool must accept this trade-off.\n")
cat("4. Association rules confirm that High BP + High Cholesterol + Obesity\n")
cat("   + Fair/Poor health = very strong diabetes signal (lift ~1.7).\n\n")

# ---- 8. Limitations ---------------------------------------------------------
cat(paste(rep("-", 60), collapse=""), "\n")
cat("LIMITATIONS\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")
cat("- The balanced 50/50 sample does not reflect population prevalence.\n")
cat("- Prediabetes (4,631 respondents) is coded 0 in the binary target.\n")
cat("- All data is self-reported from a single cross-sectional survey (2015).\n")
cat("- Associations do not imply causation.\n\n")

# ---- 9. Save the complete results sheet as a text file -----------------------
sink("review2/results/07_results_sheet.txt")
cat("REVIEW 2 — COMPLETE RESULTS SHEET\n")
cat(paste(rep("=", 70), collapse=""), "\n")
cat(sprintf("Generated: %s\n\n", Sys.time()))

cat("10.1 SETUP\n")
cat(sprintf("  Train / test rows (balanced): %d / %d\n", nrow(train), nrow(test)))
cat(sprintf("  Seed: 42\n"))
cat(sprintf("  Chosen cp (CART): %.6f\n", dt_comp$Best_CP[1]))
cat(sprintf("  Chosen k (KNN):   %d\n\n", knn_met$k[1]))

cat("10.2 MODEL COMPARISON (BALANCED TEST SET)\n")
print(comparison_display, row.names = FALSE)
cat("  [WEKA J48 and Naive Bayes: fill from WEKA screenshots]\n\n")

cat("10.3 REALISTIC PREVALENCE (FULL-FILE TEST SET)\n")
print(thresh_table, row.names = FALSE)
cat("\n")

cat("10.4 ASSOCIATION RULES (TOP 5)\n")
print(head(top_rules_df, 5), row.names = FALSE)
cat("\n")

cat("10.5 CLUSTERING\n")
print(round(clust_prof, 2), row.names = FALSE)
cat("\n")

cat("WRITE-UP\n")
cat(sprintf("Best model: %s (F1=%.4f, AUC=%.4f)\n", best_model, best_f1, best_auc))
cat("All three R models ~73-74% accuracy. KNN best AUC.\n")
cat("Realistic-prevalence: recall drops to ~11% at 0.5 threshold; ~61% at 0.2.\n")
cat("Association rules: HighBP+HighChol+Obese+Fair/Poor health -> diabetes (lift ~1.7).\n\n")

cat("LIMITATIONS\n")
cat("- Balanced sample ≠ population prevalence\n")
cat("- Prediabetes coded 0\n")
cat("- Self-reported, cross-sectional, 2015 only\n")
cat("- Association ≠ causation\n")
sink()
cat("Results sheet saved to review2/results/07_results_sheet.txt\n")

# ---- 10. Save comparison table CSV -------------------------------------------
write.csv(comparison_table, "review2/results/model_comparison_all.csv", row.names = FALSE)
cat("Model comparison CSV saved to review2/results/model_comparison_all.csv\n")

cat("\n")
cat(paste(rep("=", 70), collapse=""), "\n")
cat("FINAL COMPARISON AND WRITE-UP COMPLETE\n")
cat(paste(rep("=", 70), collapse=""), "\n")
