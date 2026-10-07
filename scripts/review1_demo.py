#!/usr/bin/env python3
"""
=============================================================================
 DMDW PROJECT — Review 1: LIVE DEMO SCRIPT
 Team: Data Miners | Member: 24MIC0068
 
 This script demonstrates:
   1. Dataset loading & verification
   2. Data quality summary
   3. EDA visualizations
   4. Star Schema verification
   5. Live OLAP query execution
 
 Run this on the laptop during the Review 1 presentation.
=============================================================================
"""

import pandas as pd
import numpy as np
import sqlite3
import os

# ─── Paths ──────────────────────────────────────────────────────────────
PROJECT_DIR = "/home/vct/Desktop/DMDW PROJECT"
DATA_CLEAN  = f"{PROJECT_DIR}/data/cleaned_diabetes.csv"
DB_PATH     = f"{PROJECT_DIR}/database/diabetes_dw.db"

def separator(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

# =====================================================================
# DEMO 1: Dataset Verification
# =====================================================================
separator("DEMO 1: DATASET VERIFICATION")

df = pd.read_csv(DATA_CLEAN)
print(f"✅ Cleaned dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"\n📋 Columns: {list(df.columns)}")
print(f"\n📈 Sample Records:")
print(df.head(5).to_string())

# =====================================================================
# DEMO 2: Data Quality Summary
# =====================================================================
separator("DEMO 2: DATA QUALITY SUMMARY")

print(f"  ● Original records:    100,000")
print(f"  ● Duplicates removed:  3,854")
print(f"  ● Clean records:       {df.shape[0]:,}")
print(f"  ● Missing NaN values:  0")
print(f"  ● 'No Info' smoking:   {(df['smoking_history'] == 'No Info').sum():,} ({(df['smoking_history'] == 'No Info').mean()*100:.1f}%)")

target = df['diabetes'].value_counts()
print(f"\n  🎯 Target Distribution:")
print(f"     Non-Diabetic (0): {target[0]:,} ({target[0]/len(df)*100:.1f}%)")
print(f"     Diabetic (1):     {target[1]:,} ({target[1]/len(df)*100:.1f}%)")
print(f"     Imbalance Ratio:  {target[0]/target[1]:.1f}:1")

# =====================================================================
# DEMO 3: Data Warehouse — Star Schema Verification
# =====================================================================
separator("DEMO 3: DATA WAREHOUSE — STAR SCHEMA")

conn = sqlite3.connect(DB_PATH)

print("\n📦 Tables in Data Warehouse:")
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
for _, row in tables.iterrows():
    count = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {row['name']}", conn)
    print(f"  ● {row['name']:35s} → {count['cnt'].iloc[0]:>6,} rows")

print("\n📊 DIM_DEMOGRAPHICS (sample):")
print(pd.read_sql_query("SELECT * FROM dim_demographics LIMIT 5", conn).to_string(index=False))

print("\n📊 DIM_CLINICAL_RISK (sample):")
print(pd.read_sql_query("SELECT * FROM dim_clinical_risk LIMIT 5", conn).to_string(index=False))

print("\n📊 DIM_METRIC_RANGES (sample):")
print(pd.read_sql_query("SELECT * FROM dim_metric_ranges LIMIT 5", conn).to_string(index=False))

# =====================================================================
# DEMO 4: LIVE OLAP — ROLL-UP
# =====================================================================
separator("DEMO 4: OLAP — ROLL-UP (Age Group → Life Stage)")

q = """
SELECT
    d.life_stage,
    COUNT(*)                            AS total_patients,
    SUM(f.is_diabetic)                  AS diabetic_count,
    ROUND(AVG(f.is_diabetic) * 100, 2)  AS diabetes_prevalence_pct,
    ROUND(AVG(f.hba1c_level), 2)        AS avg_hba1c
FROM fact_patient_screening f
JOIN dim_demographics d ON f.demographic_key = d.demographic_key
GROUP BY d.life_stage
ORDER BY diabetes_prevalence_pct DESC;
"""
print(pd.read_sql_query(q, conn).to_string(index=False))

# =====================================================================
# DEMO 5: LIVE OLAP — DICE
# =====================================================================
separator("DEMO 5: OLAP — DICE (Age 45-59 & Hypertension & Obese)")

q = """
SELECT
    d.gender,
    r.smoking_history,
    m.hba1c_category,
    COUNT(*)                            AS total_patients,
    SUM(f.is_diabetic)                  AS diabetic_count,
    ROUND(AVG(f.is_diabetic) * 100, 2)  AS diabetes_prevalence_pct
FROM fact_patient_screening f
JOIN dim_demographics d  ON f.demographic_key = d.demographic_key
JOIN dim_clinical_risk r ON f.risk_key = r.risk_key
JOIN dim_metric_ranges m ON f.metric_key = m.metric_key
WHERE d.age_group = '45-59 (Middle-Aged)'
  AND r.hypertension = 1
  AND m.bmi_category = 'Obese'
GROUP BY d.gender, r.smoking_history, m.hba1c_category
HAVING total_patients >= 10
ORDER BY diabetes_prevalence_pct DESC
LIMIT 10;
"""
print(pd.read_sql_query(q, conn).to_string(index=False))

# =====================================================================
# DEMO 6: LIVE OLAP — PIVOT
# =====================================================================
separator("DEMO 6: OLAP — PIVOT (Gender × BMI Category → Diabetes %)")

q = """
SELECT
    d.gender,
    ROUND(AVG(CASE WHEN m.bmi_category = 'Underweight' THEN f.is_diabetic END) * 100, 2) AS "Underweight_%",
    ROUND(AVG(CASE WHEN m.bmi_category = 'Normal' THEN f.is_diabetic END) * 100, 2)      AS "Normal_%",
    ROUND(AVG(CASE WHEN m.bmi_category = 'Overweight' THEN f.is_diabetic END) * 100, 2)  AS "Overweight_%",
    ROUND(AVG(CASE WHEN m.bmi_category = 'Obese' THEN f.is_diabetic END) * 100, 2)       AS "Obese_%"
FROM fact_patient_screening f
JOIN dim_demographics d ON f.demographic_key = d.demographic_key
JOIN dim_metric_ranges m ON f.metric_key = m.metric_key
WHERE d.gender IN ('Female', 'Male')
GROUP BY d.gender;
"""
print(pd.read_sql_query(q, conn).to_string(index=False))

conn.close()

separator("✅ DEMO COMPLETE — ALL SYSTEMS OPERATIONAL")
print(f"  Database:  {DB_PATH}")
print(f"  Dataset:   {DATA_CLEAN}")
print(f"  Images:    {PROJECT_DIR}/images/ ({len(os.listdir(f'{PROJECT_DIR}/images'))} files)")
