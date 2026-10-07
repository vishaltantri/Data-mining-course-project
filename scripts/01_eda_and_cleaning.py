#!/usr/bin/env python3
"""
=============================================================================
 DMDW PROJECT — Review 1: Exploratory Data Analysis & Data Cleaning
 Team: Data Miners | Member: 24MIC0068
 Dataset: Diabetes Prediction Dataset (Kaggle — iammustafatz)
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

# ─── Configuration ──────────────────────────────────────────────────────
DATA_RAW = "/home/vct/Desktop/DMDW PROJECT/data/diabetes_prediction_dataset.csv"
DATA_CLEAN = "/home/vct/Desktop/DMDW PROJECT/data/cleaned_diabetes.csv"
IMG_DIR = "/home/vct/Desktop/DMDW PROJECT/images"
os.makedirs(IMG_DIR, exist_ok=True)

# ─── Visual style ───────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
})
sns.set_theme(style="whitegrid", palette="muted")

# =====================================================================
# STEP 1: LOAD RAW DATASET & BASIC PROFILING
# =====================================================================
print("=" * 70)
print(" STEP 1: LOADING RAW DATASET")
print("=" * 70)
df = pd.read_csv(DATA_RAW)

print(f"\n📊 Dataset Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"\n📋 Columns: {list(df.columns)}")
print(f"\n🔤 Data Types:\n{df.dtypes}")
print(f"\n📈 First 5 Rows:\n{df.head()}")

# =====================================================================
# STEP 2: DESCRIPTIVE STATISTICS
# =====================================================================
print("\n" + "=" * 70)
print(" STEP 2: DESCRIPTIVE STATISTICS")
print("=" * 70)

# Numerical features
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = df.select_dtypes(include=['object']).columns.tolist()

print(f"\n🔢 Numerical Columns ({len(num_cols)}): {num_cols}")
print(f"🏷️  Categorical Columns ({len(cat_cols)}): {cat_cols}")

print(f"\n📊 Numerical Summary:\n{df[num_cols].describe().round(3)}")

# Per-column stats
print("\n📐 Detailed Per-Column Statistics:")
for col in num_cols:
    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    iqr_val = q3 - q1
    lower_fence = q1 - 1.5 * iqr_val
    upper_fence = q3 + 1.5 * iqr_val
    outliers = ((df[col] < lower_fence) | (df[col] > upper_fence)).sum()
    print(f"  {col:25s} | Mean={df[col].mean():.3f} | Std={df[col].std():.3f} "
          f"| Min={df[col].min():.3f} | Max={df[col].max():.3f} "
          f"| IQR Outliers={outliers:,}")

# Categorical summaries
print("\n🏷️  Categorical Value Counts:")
for col in cat_cols:
    print(f"\n  {col}:")
    vc = df[col].value_counts()
    for val, cnt in vc.items():
        print(f"    {val:20s} → {cnt:>6,} ({cnt/len(df)*100:.1f}%)")

# =====================================================================
# STEP 3: DATA QUALITY AUDIT
# =====================================================================
print("\n" + "=" * 70)
print(" STEP 3: DATA QUALITY AUDIT")
print("=" * 70)

# 3a. Missing Values
print("\n🔍 Missing Values (NaN) per Column:")
missing = df.isnull().sum()
print(missing)
total_missing = missing.sum()
print(f"  Total NaN cells: {total_missing}")

# 3b. Implicit Missing ("No Info" in smoking_history)
no_info_count = (df['smoking_history'] == 'No Info').sum()
print(f"\n⚠️  Implicit Missing — smoking_history = 'No Info': {no_info_count:,} ({no_info_count/len(df)*100:.1f}%)")

# 3c. Duplicates
dup_count = df.duplicated().sum()
print(f"\n🔁 Exact Duplicate Rows: {dup_count:,} ({dup_count/len(df)*100:.2f}%)")

# 3d. Target Distribution (Class Imbalance)
target_counts = df['diabetes'].value_counts()
print(f"\n🎯 Target Variable Distribution (diabetes):")
for val, cnt in target_counts.items():
    label = "Non-Diabetic" if val == 0 else "Diabetic"
    print(f"  {val} ({label}): {cnt:>6,} ({cnt/len(df)*100:.1f}%)")

imbalance_ratio = target_counts[0] / target_counts[1]
print(f"  Imbalance Ratio: {imbalance_ratio:.1f}:1")

# =====================================================================
# STEP 4: DATA CLEANING
# =====================================================================
print("\n" + "=" * 70)
print(" STEP 4: DATA CLEANING")
print("=" * 70)

df_clean = df.drop_duplicates()
print(f"✅ Duplicates removed: {dup_count:,}")
print(f"✅ Clean dataset shape: {df_clean.shape[0]:,} rows × {df_clean.shape[1]} columns")

# Save cleaned dataset
df_clean.to_csv(DATA_CLEAN, index=False)
print(f"💾 Saved cleaned dataset to: {DATA_CLEAN}")

# Re-check target distribution after cleaning
target_clean = df_clean['diabetes'].value_counts()
print(f"\n🎯 Target Distribution (After Cleaning):")
for val, cnt in target_clean.items():
    label = "Non-Diabetic" if val == 0 else "Diabetic"
    print(f"  {val} ({label}): {cnt:>6,} ({cnt/len(df_clean)*100:.1f}%)")

# =====================================================================
# STEP 5: CORRELATION ANALYSIS
# =====================================================================
print("\n" + "=" * 70)
print(" STEP 5: CORRELATION ANALYSIS")
print("=" * 70)

corr_matrix = df_clean[num_cols].corr()
print("\n🔗 Correlation Matrix:")
print(corr_matrix.round(3))

print("\n📌 Top Correlations with 'diabetes':")
diabetes_corr = corr_matrix['diabetes'].drop('diabetes').abs().sort_values(ascending=False)
for feat, val in diabetes_corr.items():
    print(f"  {feat:25s} → {corr_matrix['diabetes'][feat]:+.4f}")

# =====================================================================
# STEP 6: GENERATE VISUALIZATIONS
# =====================================================================
print("\n" + "=" * 70)
print(" STEP 6: GENERATING VISUALIZATIONS")
print("=" * 70)

# ─── FIGURE 1: Target Distribution Bar Chart ────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
colors = ['#3498db', '#e74c3c']
bars = ax.bar(['Non-Diabetic (0)', 'Diabetic (1)'],
              [target_clean[0], target_clean[1]],
              color=colors, edgecolor='white', linewidth=1.5)
for bar, cnt in zip(bars, [target_clean[0], target_clean[1]]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 500,
            f'{cnt:,}\n({cnt/len(df_clean)*100:.1f}%)',
            ha='center', va='bottom', fontweight='bold', fontsize=11)
ax.set_title('Target Variable Distribution (diabetes)\nAfter Deduplication', fontweight='bold')
ax.set_ylabel('Number of Patients')
ax.set_xlabel('Diabetes Status')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/01_target_distribution.png")
plt.close()
print("  ✅ Saved: 01_target_distribution.png")

# ─── FIGURE 2: Correlation Heatmap ──────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 7))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.3f',
            cmap='RdBu_r', center=0, vmin=-1, vmax=1,
            square=True, linewidths=0.5,
            cbar_kws={'shrink': 0.8, 'label': 'Pearson Correlation'},
            ax=ax)
ax.set_title('Feature Correlation Heatmap\n(Pearson Correlation)', fontweight='bold')
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/02_correlation_heatmap.png")
plt.close()
print("  ✅ Saved: 02_correlation_heatmap.png")

# ─── FIGURE 3: Boxplots of Clinical Metrics vs Diabetes ─────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
clinical_cols = ['HbA1c_level', 'blood_glucose_level', 'bmi']
titles = ['HbA1c Level', 'Blood Glucose Level', 'BMI']

for ax, col, title in zip(axes, clinical_cols, titles):
    sns.boxplot(data=df_clean, x='diabetes', y=col, ax=ax,
                palette={0: '#3498db', 1: '#e74c3c'},
                hue='diabetes', legend=False)
    ax.set_xticklabels(['Non-Diabetic', 'Diabetic'])
    ax.set_title(f'{title} vs Diabetes Status', fontweight='bold')
    ax.set_xlabel('')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.suptitle('Clinical Metrics Distribution by Diabetes Status', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/03_clinical_boxplots.png", bbox_inches='tight')
plt.close()
print("  ✅ Saved: 03_clinical_boxplots.png")

# ─── FIGURE 4: Comorbidity Stacked Bar Chart ────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, col, title in zip(axes, ['hypertension', 'heart_disease'],
                           ['Hypertension', 'Heart Disease']):
    ct = pd.crosstab(df_clean[col], df_clean['diabetes'], normalize='index') * 100
    ct.plot(kind='bar', stacked=True, color=['#3498db', '#e74c3c'],
            ax=ax, edgecolor='white', linewidth=0.5)
    ax.set_xticklabels(['No', 'Yes'], rotation=0)
    ax.set_title(f'Diabetes Prevalence by {title}', fontweight='bold')
    ax.set_xlabel(title)
    ax.set_ylabel('Percentage (%)')
    ax.legend(['Non-Diabetic', 'Diabetic'], loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add percentage labels
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', label_type='center', fontsize=9)

plt.suptitle('Comorbidity Analysis: Hypertension & Heart Disease vs Diabetes',
             fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/04_comorbidity_analysis.png", bbox_inches='tight')
plt.close()
print("  ✅ Saved: 04_comorbidity_analysis.png")

# ─── FIGURE 5: Age Distribution by Diabetes Status ──────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(data=df_clean, x='age', hue='diabetes',
             palette={0: '#3498db', 1: '#e74c3c'},
             multiple='stack', bins=40, edgecolor='white', ax=ax)
ax.set_title('Age Distribution by Diabetes Status', fontweight='bold')
ax.set_xlabel('Age (years)')
ax.set_ylabel('Count')
ax.legend(['Non-Diabetic', 'Diabetic'])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/05_age_distribution.png")
plt.close()
print("  ✅ Saved: 05_age_distribution.png")

# ─── FIGURE 6: Smoking History vs Diabetes ───────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
smoking_diabetes = pd.crosstab(df_clean['smoking_history'], df_clean['diabetes'],
                                normalize='index') * 100
smoking_diabetes = smoking_diabetes.sort_values(by=1, ascending=False)
smoking_diabetes.plot(kind='barh', stacked=True, color=['#3498db', '#e74c3c'],
                      ax=ax, edgecolor='white')
ax.set_title('Diabetes Prevalence by Smoking History', fontweight='bold')
ax.set_xlabel('Percentage (%)')
ax.set_ylabel('Smoking History')
ax.legend(['Non-Diabetic', 'Diabetic'], loc='lower right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/06_smoking_vs_diabetes.png")
plt.close()
print("  ✅ Saved: 06_smoking_vs_diabetes.png")

# ─── FIGURE 7: BMI Distribution with WHO Categories ─────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(data=df_clean, x='bmi', hue='diabetes',
             palette={0: '#3498db', 1: '#e74c3c'},
             multiple='layer', bins=50, alpha=0.6, edgecolor='white', ax=ax)
# WHO cut-off lines
for val, label in [(18.5, 'Underweight'), (25, 'Normal'), (30, 'Overweight/Obese')]:
    ax.axvline(x=val, color='gray', linestyle='--', alpha=0.7)
    ax.text(val + 0.3, ax.get_ylim()[1] * 0.9, label, fontsize=8, rotation=90,
            va='top', color='gray')
ax.set_title('BMI Distribution with WHO Categories', fontweight='bold')
ax.set_xlabel('BMI (kg/m²)')
ax.set_ylabel('Count')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/07_bmi_distribution.png")
plt.close()
print("  ✅ Saved: 07_bmi_distribution.png")

# ─── FIGURE 8: Feature Importance (Correlation with Target) ─────────────
fig, ax = plt.subplots(figsize=(8, 5))
target_corr = corr_matrix['diabetes'].drop('diabetes').sort_values(ascending=True)
colors_bar = ['#e74c3c' if v > 0 else '#3498db' for v in target_corr.values]
target_corr.plot(kind='barh', ax=ax, color=colors_bar, edgecolor='white')
ax.set_title('Feature Correlation with Diabetes Target', fontweight='bold')
ax.set_xlabel('Pearson Correlation Coefficient')
ax.axvline(x=0, color='black', linewidth=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
for i, (val, name) in enumerate(zip(target_corr.values, target_corr.index)):
    ax.text(val + 0.005 if val > 0 else val - 0.005,
            i, f'{val:+.3f}',
            ha='left' if val > 0 else 'right',
            va='center', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{IMG_DIR}/08_feature_importance.png")
plt.close()
print("  ✅ Saved: 08_feature_importance.png")

# =====================================================================
# STEP 7: EXPORT EDA SUMMARY REPORT
# =====================================================================
print("\n" + "=" * 70)
print(" STEP 7: EDA SUMMARY REPORT")
print("=" * 70)

summary = {
    "raw_shape": list(df.shape),
    "clean_shape": list(df_clean.shape),
    "duplicates_removed": int(dup_count),
    "columns": list(df.columns),
    "numerical_columns": num_cols,
    "categorical_columns": cat_cols,
    "total_nan": int(total_missing),
    "no_info_smoking": int(no_info_count),
    "target_distribution_raw": {str(k): int(v) for k, v in df['diabetes'].value_counts().items()},
    "target_distribution_clean": {str(k): int(v) for k, v in target_clean.items()},
    "imbalance_ratio": round(float(imbalance_ratio), 1),
    "correlation_with_diabetes": {k: round(float(v), 4) for k, v in
                                   corr_matrix['diabetes'].drop('diabetes').sort_values(ascending=False).items()}
}

summary_path = "/home/vct/Desktop/DMDW PROJECT/data/eda_summary.json"
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)
print(f"💾 Saved EDA summary: {summary_path}")

print("\n" + "=" * 70)
print(" ✅ EDA & CLEANING COMPLETE")
print("=" * 70)
print(f"  Raw dataset:     {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"  Cleaned dataset: {df_clean.shape[0]:,} rows × {df_clean.shape[1]} columns")
print(f"  Duplicates:      {dup_count:,} removed")
print(f"  Images saved:    {len(os.listdir(IMG_DIR))} visualizations")
print(f"  Clean CSV:       {DATA_CLEAN}")
