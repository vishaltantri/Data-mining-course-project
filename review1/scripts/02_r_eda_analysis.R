# R Script for Review 1 Exploratory Data Analysis & Statistical Testing
# CSI3010 Data Mining & Warehousing - Lab Project

sink("review1/r_eda_output.txt")

cat("=========================================================\n")
cat(" R EXPLORATORY DATA ANALYSIS & STATISTICAL AUDIT\n")
cat(" BRFSS 2015 Diabetes Health Indicators Dataset\n")
cat("=========================================================\n\n")

# 1. Load Dataset
dataset_path <- "diabetes_binary_5050split_health_indicators_BRFSS2015.csv"
data <- read.csv(dataset_path)

cat("1. DATASET DIMENSIONS\n")
cat("Number of Rows (Observations):", nrow(data), "\n")
cat("Number of Columns (Variables):", ncol(data), "\n\n")

cat("2. DATA TYPES & STRUCTURE\n")
str(data)
cat("\n")

cat("3. MISSING VALUE AUDIT\n")
total_na <- sum(is.na(data))
cat("Total Missing (NA) values across all cells:", total_na, "\n\n")

cat("4. TARGET CLASS DISTRIBUTION\n")
target_tbl <- table(data$Diabetes_binary)
cat("Frequency Count:\n")
print(target_tbl)
cat("Proportion:\n")
print(prop.table(target_tbl) * 100)
cat("\n")

cat("5. DESCRIPTIVE STATISTICS FOR NUMERIC & ORDINAL FEATURES\n")
summary_stats <- data.frame(
  Mean = sapply(data, mean),
  SD = sapply(data, sd),
  Median = sapply(data, median),
  Min = sapply(data, min),
  Max = sapply(data, max)
)
print(round(summary_stats, 4))
cat("\n")

cat("6. PEARSON CORRELATION WITH TARGET (Diabetes_binary)\n")
cor_matrix <- cor(data)
cor_target <- cor_matrix[, "Diabetes_binary"]
cor_target_sorted <- sort(cor_target, decreasing = TRUE)
print(round(cor_target_sorted, 4))
cat("\n")

cat("7. CHI-SQUARE TESTS OF INDEPENDENCE WITH TARGET\n")
cat("Testing association of clinical/lifestyle factors with Diabetes status:\n\n")

test_features <- c("HighBP", "HighChol", "Smoker", "Stroke", "HeartDiseaseorAttack", "PhysActivity", "DiffWalk", "Sex")

for (feat in test_features) {
  tbl <- table(data[[feat]], data$Diabetes_binary)
  chi <- chisq.test(tbl)
  cat(sprintf("Feature: %-20s | Chi-sq Statistic: %10.2f | p-value: %e\n", 
              feat, chi$statistic, chi$p.value))
}

cat("\n=========================================================\n")
cat(" R EDA EXECUTION COMPLETED SUCCESSFULLY\n")
cat("=========================================================\n")

sink()
cat("R EDA script finished. Output saved to review1/r_eda_output.txt\n")
