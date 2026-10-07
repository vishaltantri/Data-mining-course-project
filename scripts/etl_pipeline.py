#!/usr/bin/env python3
"""
=============================================================================
 DMDW PROJECT — Review 1: ETL Pipeline (Presentation-Ready Code)
 Team: Data Miners | Member: 24MIC0068
 
 Extract  → Raw CSV from Kaggle
 Transform → Deduplication, Clinical Binning, Surrogate Key Generation
 Load     → SQLite Star Schema (diabetes_dw.db)
=============================================================================
"""

import pandas as pd
import sqlite3

# ── EXTRACT ──────────────────────────────────────────────────────────────
df = pd.read_csv("data/diabetes_prediction_dataset.csv")
print(f"Extracted: {df.shape[0]:,} rows × {df.shape[1]} columns")

# ── TRANSFORM ────────────────────────────────────────────────────────────
# Step 1: Remove exact duplicate rows
df = df.drop_duplicates()
print(f"After deduplication: {df.shape[0]:,} rows")

# Step 2: Clinical feature binning
df['age_group'] = pd.cut(df['age'],
    bins=[0, 18, 30, 45, 60, 80],
    labels=['0-17 (Child/Teen)', '18-29 (Young Adult)',
            '30-44 (Adult)', '45-59 (Middle-Aged)', '60-80 (Senior)'])

df['bmi_category'] = pd.cut(df['bmi'],
    bins=[0, 18.5, 25, 30, 100],
    labels=['Underweight', 'Normal', 'Overweight', 'Obese'])

df['hba1c_category'] = pd.cut(df['HbA1c_level'],
    bins=[0, 5.7, 6.5, 100],
    labels=['Normal (<5.7)', 'Prediabetes (5.7-6.4)', 'Diabetes (≥6.5)'])

df['glucose_category'] = pd.cut(df['blood_glucose_level'],
    bins=[0, 140, 200, 500],
    labels=['Normal (<140)', 'Impaired (140-199)', 'High (≥200)'])

# Step 3: Build dimension tables with surrogate keys
dim_demographics = df[['gender', 'age_group']].drop_duplicates().reset_index(drop=True)
dim_demographics.insert(0, 'demographic_key', range(1, len(dim_demographics) + 1))

dim_clinical_risk = df[['hypertension', 'heart_disease', 'smoking_history']].drop_duplicates().reset_index(drop=True)
dim_clinical_risk.insert(0, 'risk_key', range(1, len(dim_clinical_risk) + 1))

dim_metric_ranges = df[['bmi_category', 'hba1c_category', 'glucose_category']].drop_duplicates().reset_index(drop=True)
dim_metric_ranges.insert(0, 'metric_key', range(1, len(dim_metric_ranges) + 1))

print(f"Dimensions: {len(dim_demographics)} demographics, "
      f"{len(dim_clinical_risk)} risk profiles, "
      f"{len(dim_metric_ranges)} metric ranges")

# ── LOAD ─────────────────────────────────────────────────────────────────
conn = sqlite3.connect("database/diabetes_dw.db")
dim_demographics.to_sql('dim_demographics', conn, if_exists='replace', index=False)
dim_clinical_risk.to_sql('dim_clinical_risk', conn, if_exists='replace', index=False)
dim_metric_ranges.to_sql('dim_metric_ranges', conn, if_exists='replace', index=False)
print(f"✅ Loaded into SQLite: database/diabetes_dw.db")
conn.close()
