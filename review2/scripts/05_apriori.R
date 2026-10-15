################################################################################
# Review 2 — Phase E: Association Rules (Apriori)
# Script: 05_apriori.R
# Purpose: Mine association rules with fixed RHS = Diabetes_binary=Yes,
#          grid search over support/confidence, remove redundant rules.
################################################################################

# ---- 0. Setup ----------------------------------------------------------------
library(arules)
set.seed(42)

cat(paste(rep("=", 70), collapse=""), "\n")
cat("REVIEW 2 — PHASE E: APRIORI ASSOCIATION RULES\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")

# Load preprocessed data
load("review2/results/preprocessed.RData")
cat("Preprocessed data loaded.\n\n")

# ---- 1. Prepare data for Apriori ---------------------------------------------
# Use the full balanced dataset (not split) for rule mining
# Use only categorical columns + binned BMI, drop MentHlth and PhysHlth (continuous)
df_apriori <- bal[, c("Diabetes_binary", "HighBP", "HighChol", "CholCheck",
                       "Smoker", "Stroke", "HeartDiseaseorAttack",
                       "PhysActivity", "Fruits", "Veggies",
                       "HvyAlcoholConsump", "AnyHealthcare", "NoDocbcCost",
                       "DiffWalk", "Sex", "GenHlth", "Age",
                       "Education", "Income", "BMI_binned")]

# Drop the original BMI (continuous) — we use BMI_binned instead
# Convert all remaining columns to factor
df_apriori[] <- lapply(df_apriori, as.factor)

cat("Columns for Apriori:\n")
cat(names(df_apriori), sep = ", ")
cat("\n\n")

# Convert to transactions
trans <- as(df_apriori, "transactions")
cat("Transactions created:", length(trans), "transactions,",
    length(itemLabels(trans)), "items\n\n")

# ---- 2. Grid search over support and confidence ------------------------------
cat(paste(rep("-", 60), collapse=""), "\n")
cat("Grid Search: Support × Confidence\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

supp_vals <- c(0.05, 0.1, 0.2)
conf_vals <- c(0.6, 0.7, 0.8)

grid_results <- data.frame(
  Support    = numeric(),
  Confidence = numeric(),
  NumRules   = integer()
)

for (s in supp_vals) {
  for (c in conf_vals) {
    rules_temp <- apriori(trans,
      parameter = list(supp = s, conf = c, minlen = 2),
      appearance = list(rhs = "Diabetes_binary=Yes", default = "lhs"),
      control = list(verbose = FALSE))

    n_rules <- length(rules_temp)
    grid_results <- rbind(grid_results,
      data.frame(Support = s, Confidence = c, NumRules = n_rules))

    cat(sprintf("  Support=%.2f, Confidence=%.1f → %d rules\n", s, c, n_rules))
  }
}

cat("\nGrid summary:\n")
print(grid_results)
cat("\n")

# Save grid
write.csv(grid_results, "review2/results/apriori_grid.csv", row.names = FALSE)

# ---- 3. Mine rules with chosen parameters ------------------------------------
cat(paste(rep("-", 60), collapse=""), "\n")
cat("Mining rules with support=0.05, confidence=0.7\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

rules <- apriori(trans,
  parameter = list(supp = 0.05, conf = 0.7, minlen = 2),
  appearance = list(rhs = "Diabetes_binary=Yes", default = "lhs"),
  control = list(verbose = FALSE))

cat(sprintf("Total rules mined: %d\n", length(rules)))

# ---- 4. Remove redundant rules -----------------------------------------------
rules_clean <- rules[!is.redundant(rules)]
cat(sprintf("After removing redundant: %d rules\n\n", length(rules_clean)))

# ---- 5. Sort by lift and inspect top rules -----------------------------------
rules_sorted <- sort(rules_clean, by = "lift")

cat("Top 10 Rules (sorted by lift):\n")
cat(paste(rep("-", 60), collapse=""), "\n")
inspect(head(rules_sorted, 10))
cat("\n")

# ---- 6. Extract top 5-8 readable rules for the results sheet -----------------
# The very top-lift rules all have 6-item antecedents; for the slide we also
# keep short, readable rules (at most 3 items on the left-hand side).
rules_readable <- rules_sorted[lengths(LIST(rules_sorted@lhs)) <= 3]
cat(sprintf("Readable rules (LHS <= 3 items): %d\n", length(rules_readable)))
cat("Top 10 readable rules (sorted by lift):\n")
inspect(head(rules_readable, 10))
cat("\n")

top_rules <- head(rules_readable, 8)
top_df <- data.frame(
  Rule_No = 1:min(8, length(top_rules)),
  Rule = labels(top_rules),
  Support = round(quality(top_rules)$support, 4),
  Confidence = round(quality(top_rules)$confidence, 4),
  Lift = round(quality(top_rules)$lift, 4)
)

cat("\nTop Rules for Results Sheet:\n")
print(top_df, right = FALSE)
cat("\n")

write.csv(top_df, "review2/results/apriori_top_rules.csv", row.names = FALSE)

# ---- 7. Note on balanced sample ----------------------------------------------
cat("NOTE: Since these rules are mined on the balanced 50/50 sample,\n")
cat("support values reflect the design of this sample, NOT population\n")
cat("prevalence. The rules describe patterns within this balanced dataset.\n\n")

# ---- Save console output ----------------------------------------------------
sink("review2/results/05_apriori_output.txt")
cat("REVIEW 2 — APRIORI ASSOCIATION RULES\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")
cat("Grid search results:\n")
print(grid_results)
cat("\n\nTop rules (sorted by lift):\n")
inspect(head(rules_sorted, 10))
cat("\n\nTop rules table:\n")
print(top_df, right = FALSE)
cat("\nNote: Support values reflect the 50/50 balanced sample design.\n")
sink()
cat("Output saved to review2/results/05_apriori_output.txt\n")

# Save objects
save(trans, rules, rules_clean, rules_sorted, top_df, grid_results,
     file = "review2/results/apriori_models.RData")

cat("\n")
cat(paste(rep("=", 70), collapse=""), "\n")
cat("APRIORI ASSOCIATION RULES COMPLETE\n")
cat(paste(rep("=", 70), collapse=""), "\n")
