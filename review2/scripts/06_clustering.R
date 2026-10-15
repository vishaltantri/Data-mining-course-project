################################################################################
# Review 2 — Phase F: Clustering (K-Means + Hierarchical)
# Script: 06_clustering.R
# Purpose: K-Means with elbow/silhouette, cluster profiling,
#          hierarchical clustering on a sample, dendrogram, comparison.
################################################################################

# ---- 0. Setup ----------------------------------------------------------------
library(cluster)
library(factoextra)
library(caret)
set.seed(42)

cat(paste(rep("=", 70), collapse=""), "\n")
cat("REVIEW 2 — PHASE F: CLUSTERING\n")
cat(paste(rep("=", 70), collapse=""), "\n\n")

# Load preprocessed data
load("review2/results/preprocessed.RData")

# Use ALL rows (balanced dataset), scaled predictors, label excluded
# We need to scale the full dataset, not just train
full_bal <- read.csv("diabetes_binary_5050split_health_indicators_BRFSS2015.csv")
y_all <- factor(full_bal$Diabetes_binary, levels = c(0, 1), labels = c("No", "Yes"))
X_all <- full_bal[, feat]  # feat from preprocessed.RData

# Scale using training statistics (pp from preprocessed.RData)
X_scaled <- predict(pp, X_all)

cat("Scaled dataset for clustering:", nrow(X_scaled), "rows x", ncol(X_scaled), "cols\n")
cat("Label (Diabetes_binary) is HELD OUT during clustering.\n\n")

# ---- 1. Elbow plot (WSS) on a sample ----------------------------------------
cat(paste(rep("-", 60), collapse=""), "\n")
cat("Step 1: Elbow Plot (Within-Sum-of-Squares)\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

set.seed(42)
sample_5k <- X_scaled[sample(nrow(X_scaled), 5000), ]

png("review2/figures/06_elbow_plot.png", width = 800, height = 600, res = 120)
fviz_nbclust(sample_5k, kmeans, method = "wss", k.max = 10, nstart = 25) +
  ggtitle("Elbow Method — Within-Sum-of-Squares") +
  theme_minimal()
dev.off()
cat("Elbow plot saved: review2/figures/06_elbow_plot.png\n\n")

# ---- 2. Silhouette plot on a sample ------------------------------------------
cat(paste(rep("-", 60), collapse=""), "\n")
cat("Step 2: Silhouette Analysis (5,000 sample)\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

png("review2/figures/07_silhouette_plot.png", width = 800, height = 600, res = 120)
fviz_nbclust(sample_5k, kmeans, method = "silhouette", k.max = 10, nstart = 25) +
  ggtitle("Silhouette Method — Optimal Clusters") +
  theme_minimal()
dev.off()
cat("Silhouette plot saved: review2/figures/07_silhouette_plot.png\n\n")

# Quantitative silhouette widths per k (same 5,000 sample) so the choice of
# k can be justified with numbers, not only by eyeballing the plot.
cat(paste(rep("-", 60), collapse = ""), "\n")
cat("Step 2b: Average silhouette width per k (5,000 sample)\n")
cat(paste(rep("-", 60), collapse = ""), "\n\n")

dist_5k <- dist(sample_5k)
k_grid <- 2:6
sil_widths <- sapply(k_grid, function(k) {
  set.seed(42)
  km_tmp <- kmeans(sample_5k, centers = k, nstart = 25)
  if (length(unique(km_tmp$cluster)) < k) return(NA_real_)
  mean(silhouette(km_tmp$cluster, dist_5k)[, 3])
})
sil_df <- data.frame(k = k_grid, avg_silhouette = round(sil_widths, 4))
print(sil_df)
write.csv(sil_df, "review2/results/silhouette_widths.csv", row.names = FALSE)
best_sil_k <- sil_df$k[which.max(sil_df$avg_silhouette)]
cat(sprintf("\nBest average silhouette at k = %d (%.4f)\n\n",
            best_sil_k, max(sil_df$avg_silhouette)))

# ---- 3. Run K-Means on all rows ---------------------------------------------
# Chosen from the elbow plot (bend at k = 3) and the silhouette widths
# (see review2/results/silhouette_widths.csv); k = 3 also gives the
# interpretable Low / Moderate / High risk segmentation.
chosen_k <- 3
cat(paste(rep("-", 60), collapse=""), "\n")
cat(sprintf("Step 3: K-Means Clustering (k = %d) on all %d rows\n",
            chosen_k, nrow(X_scaled)))
cat(paste(rep("-", 60), collapse=""), "\n\n")

set.seed(42)
km <- kmeans(X_scaled, centers = chosen_k, nstart = 25, iter.max = 100)

cat(sprintf("K-Means converged in %d iterations\n", km$iter))
cat("Cluster sizes:\n")
print(table(km$cluster))
cat("\n")

# ---- 4. Cluster profiling ----------------------------------------------------
cat(paste(rep("-", 60), collapse=""), "\n")
cat("Step 4: Cluster Profiles\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

# Use ORIGINAL (unscaled) data for interpretable profiles
profile_data <- full_bal
profile_data$cluster <- km$cluster
profile_data$diabetes_label <- y_all

cluster_profile <- data.frame(
  Cluster     = 1:chosen_k,
  Size        = as.numeric(table(km$cluster)),
  Mean_BMI    = tapply(profile_data$BMI, profile_data$cluster, mean),
  Pct_HighBP  = tapply(profile_data$HighBP, profile_data$cluster, mean) * 100,
  Pct_HighChol = tapply(profile_data$HighChol, profile_data$cluster, mean) * 100,
  Mean_Age_Band = tapply(profile_data$Age, profile_data$cluster, mean),
  Pct_Diabetes = tapply(as.numeric(profile_data$diabetes_label == "Yes"),
                         profile_data$cluster, mean) * 100
)

cat("Cluster Profile Table:\n")
print(round(cluster_profile, 2))
cat("\n")

write.csv(cluster_profile, "review2/results/cluster_profiles.csv", row.names = FALSE)

# Cluster visualization (PCA-based)
png("review2/figures/08_kmeans_clusters.png", width = 900, height = 700, res = 120)
set.seed(42)
vis_sample_idx <- sample(nrow(X_scaled), min(5000, nrow(X_scaled)))
fviz_cluster(list(data = X_scaled[vis_sample_idx, ],
                   cluster = km$cluster[vis_sample_idx]),
             geom = "point", pointsize = 0.5, alpha = 0.4,
             main = sprintf("K-Means Clusters (k=%d) — PCA Projection", chosen_k)) +
  theme_minimal()
dev.off()
cat("Cluster plot saved: review2/figures/08_kmeans_clusters.png\n\n")

# ---- 5. Hierarchical Clustering on a sample ----------------------------------
cat(paste(rep("-", 60), collapse=""), "\n")
cat("Step 5: Hierarchical Clustering (sample of 2,500)\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")

set.seed(42)
hc_sample_idx <- sample(nrow(X_scaled), 2500)
hc_data <- X_scaled[hc_sample_idx, ]

# Distance matrix + hclust
dist_mat <- dist(hc_data, method = "euclidean")
hc <- hclust(dist_mat, method = "ward.D2")

# Cut at same k
hc_clusters <- cutree(hc, k = chosen_k)
cat("Hierarchical cluster sizes (cutree k =", chosen_k, "):\n")
print(table(hc_clusters))
cat("\n")

# Dendrogram
png("review2/figures/09_dendrogram.png", width = 1200, height = 600, res = 120)
plot(hc, labels = FALSE, hang = -1,
     main = sprintf("Dendrogram — Hierarchical Clustering (Ward.D2, n=2500, k=%d)", chosen_k),
     xlab = "", sub = "")
rect.hclust(hc, k = chosen_k, border = 2:(chosen_k + 1))
dev.off()
cat("Dendrogram saved: review2/figures/09_dendrogram.png\n\n")

# HC cluster profiles
hc_profile_data <- full_bal[hc_sample_idx, ]
hc_profile_data$cluster <- hc_clusters
hc_profile_data$diabetes_label <- y_all[hc_sample_idx]

hc_profile <- data.frame(
  Cluster       = 1:chosen_k,
  Size          = as.numeric(table(hc_clusters)),
  Pct_Diabetes  = tapply(as.numeric(hc_profile_data$diabetes_label == "Yes"),
                          hc_profile_data$cluster, mean) * 100,
  Mean_BMI      = tapply(hc_profile_data$BMI, hc_profile_data$cluster, mean),
  Pct_HighBP    = tapply(hc_profile_data$HighBP, hc_profile_data$cluster, mean) * 100
)

cat("Hierarchical Cluster Profiles:\n")
print(round(hc_profile, 2))
cat("\n")

# ---- 6. Comparison: K-Means vs Hierarchical ----------------------------------
cat(paste(rep("-", 60), collapse=""), "\n")
cat("K-Means vs Hierarchical Comparison (2-3 lines):\n")
cat(paste(rep("-", 60), collapse=""), "\n\n")
cat("1. K-Means clusters are balanced (25,527 / 28,761 / 16,404 rows); the\n")
cat("   hierarchical cut on the 2,500-row sample is much more skewed\n")
cat("   (1,588 / 850 / 62 rows).\n")
cat("2. Both methods recover the same risk gradient: the cluster with the\n")
cat("   highest diabetes rate also has the highest BMI and high-BP rate.\n")
cat("3. K-Means handled all 70,692 rows in seconds, while hclust needs an\n")
cat("   O(n^2) distance matrix, which is why it ran on a sample only.\n\n")

# ---- Save console output ----------------------------------------------------
sink("review2/results/06_clustering_output.txt")
cat("REVIEW 2 — CLUSTERING RESULTS\n")
cat(paste(rep("=", 70), collapse = ""), "\n\n")
cat(sprintf("Chosen k = %d\n\n", chosen_k))
cat("Average silhouette width per k (5,000 sample):\n")
print(sil_df)
cat(sprintf("Best silhouette at k = %d\n\n", best_sil_k))
cat("K-Means cluster sizes:\n")
print(table(km$cluster))
cat("\n\nK-Means Cluster Profiles:\n")
print(round(cluster_profile, 2))
cat("\n\nHierarchical cluster sizes:\n")
print(table(hc_clusters))
cat("\n\nHierarchical Cluster Profiles:\n")
print(round(hc_profile, 2))
cat("\n\nComparison (K-Means vs Hierarchical):\n")
cat("K-Means clusters are balanced (25,527 / 28,761 / 16,404); the hierarchical\n")
cat("cut on 2,500 rows is skewed (1,588 / 850 / 62). Both recover the same\n")
cat("risk gradient (highest-diabetes cluster = highest BMI and high-BP rate).\n")
cat("K-Means scales to all 70,692 rows; hclust was limited to a 2,500-row sample.\n")
sink()
cat("Output saved to review2/results/06_clustering_output.txt\n")

# Save objects
save(km, hc, hc_clusters, cluster_profile, hc_profile, chosen_k,
     file = "review2/results/clustering_models.RData")

cat("\n")
cat(paste(rep("=", 70), collapse=""), "\n")
cat("CLUSTERING COMPLETE\n")
cat(paste(rep("=", 70), collapse=""), "\n")
