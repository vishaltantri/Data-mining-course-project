#!/usr/bin/env python3
"""
=============================================================================
 DMDW PROJECT — Review 1: Data Warehouse Build & OLAP Operations
 Team: Data Miners | Member: 24MIC0068
 Star Schema: FACT_PATIENT_SCREENING + 3 Dimension Tables
=============================================================================
"""

import pandas as pd
import numpy as np
import sqlite3
import os

# ─── Configuration ──────────────────────────────────────────────────────
DATA_CLEAN = "/home/vct/Desktop/DMDW PROJECT/data/cleaned_diabetes.csv"
DB_PATH    = "/home/vct/Desktop/DMDW PROJECT/database/diabetes_dw.db"
SQL_DIR    = "/home/vct/Desktop/DMDW PROJECT/sql"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(SQL_DIR, exist_ok=True)

# =====================================================================
# STEP 1: LOAD CLEANED DATA
# =====================================================================
print("=" * 70)
print(" STEP 1: LOADING CLEANED DATASET")
print("=" * 70)

df = pd.read_csv(DATA_CLEAN)
print(f"📊 Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")

# =====================================================================
# STEP 2: FEATURE ENGINEERING — CREATE BINNED DIMENSIONS
# =====================================================================
print("\n" + "=" * 70)
print(" STEP 2: FEATURE ENGINEERING — DIMENSION BINNING")
print("=" * 70)

# Age Groups
age_bins = [0, 18, 30, 45, 60, 80]
age_labels = ['0-17 (Child/Teen)', '18-29 (Young Adult)', '30-44 (Adult)',
              '45-59 (Middle-Aged)', '60-80 (Senior)']
df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, right=True)

# Life Stage (higher hierarchy)
life_stage_map = {
    '0-17 (Child/Teen)': 'Youth',
    '18-29 (Young Adult)': 'Young',
    '30-44 (Adult)': 'Working Age',
    '45-59 (Middle-Aged)': 'Working Age',
    '60-80 (Senior)': 'Senior'
}
df['life_stage'] = df['age_group'].map(life_stage_map)

# BMI Categories (WHO standard)
bmi_bins = [0, 18.5, 25, 30, 100]
bmi_labels = ['Underweight', 'Normal', 'Overweight', 'Obese']
df['bmi_category'] = pd.cut(df['bmi'], bins=bmi_bins, labels=bmi_labels, right=False)

# HbA1c Categories (Clinical)
hba1c_bins = [0, 5.7, 6.5, 100]
hba1c_labels = ['Normal (<5.7)', 'Prediabetes (5.7-6.4)', 'Diabetes (≥6.5)']
df['hba1c_category'] = pd.cut(df['HbA1c_level'], bins=hba1c_bins, labels=hba1c_labels, right=False)

# Glucose Categories (Clinical)
glucose_bins = [0, 140, 200, 500]
glucose_labels = ['Normal (<140)', 'Impaired (140-199)', 'High (≥200)']
df['glucose_category'] = pd.cut(df['blood_glucose_level'], bins=glucose_bins,
                                 labels=glucose_labels, right=False)

print("✅ Binned dimensions created: age_group, life_stage, bmi_category, hba1c_category, glucose_category")
print(f"\n  Age Group Distribution:\n{df['age_group'].value_counts().sort_index()}")
print(f"\n  BMI Category Distribution:\n{df['bmi_category'].value_counts()}")
print(f"\n  HbA1c Category Distribution:\n{df['hba1c_category'].value_counts()}")

# =====================================================================
# STEP 3: BUILD DIMENSION TABLES
# =====================================================================
print("\n" + "=" * 70)
print(" STEP 3: BUILDING DIMENSION TABLES")
print("=" * 70)

# DIM_DEMOGRAPHICS
dim_demo = df[['gender', 'age_group', 'life_stage']].drop_duplicates().reset_index(drop=True)
dim_demo.index += 1
dim_demo.index.name = 'demographic_key'
dim_demo = dim_demo.reset_index()
print(f"✅ DIM_DEMOGRAPHICS: {len(dim_demo)} rows")
print(dim_demo.head(10))

# DIM_CLINICAL_RISK
dim_risk = df[['hypertension', 'heart_disease', 'smoking_history']].drop_duplicates().reset_index(drop=True)
dim_risk.index += 1
dim_risk.index.name = 'risk_key'
dim_risk = dim_risk.reset_index()
# Map binary to descriptive labels
dim_risk['hypertension_status'] = dim_risk['hypertension'].map({0: 'No', 1: 'Yes'})
dim_risk['heart_disease_status'] = dim_risk['heart_disease'].map({0: 'No', 1: 'Yes'})
print(f"\n✅ DIM_CLINICAL_RISK: {len(dim_risk)} rows")
print(dim_risk.head(10))

# DIM_METRIC_RANGES
dim_metrics = df[['bmi_category', 'hba1c_category', 'glucose_category']].drop_duplicates().reset_index(drop=True)
dim_metrics.index += 1
dim_metrics.index.name = 'metric_key'
dim_metrics = dim_metrics.reset_index()
print(f"\n✅ DIM_METRIC_RANGES: {len(dim_metrics)} rows")
print(dim_metrics)

# =====================================================================
# STEP 4: BUILD FACT TABLE WITH SURROGATE KEYS
# =====================================================================
print("\n" + "=" * 70)
print(" STEP 4: BUILDING FACT TABLE")
print("=" * 70)

# Merge surrogate keys
fact = df.copy()

# Join demographic key
fact = fact.merge(dim_demo, on=['gender', 'age_group', 'life_stage'], how='left')

# Join risk key
fact = fact.merge(dim_risk[['risk_key', 'hypertension', 'heart_disease', 'smoking_history']],
                  on=['hypertension', 'heart_disease', 'smoking_history'], how='left')

# Join metric key
fact = fact.merge(dim_metrics, on=['bmi_category', 'hba1c_category', 'glucose_category'], how='left')

# Build final fact table
fact_table = fact[['demographic_key', 'risk_key', 'metric_key',
                   'age', 'bmi', 'HbA1c_level', 'blood_glucose_level', 'diabetes']].copy()
fact_table.insert(0, 'screening_key', range(1, len(fact_table) + 1))
fact_table = fact_table.rename(columns={
    'HbA1c_level': 'hba1c_level',
    'diabetes': 'is_diabetic'
})

print(f"✅ FACT_PATIENT_SCREENING: {len(fact_table):,} rows × {len(fact_table.columns)} columns")
print(f"   Columns: {list(fact_table.columns)}")
print(f"\n{fact_table.head(10)}")

# Verify no orphan keys
print(f"\n  Null demographic_key: {fact_table['demographic_key'].isnull().sum()}")
print(f"  Null risk_key:        {fact_table['risk_key'].isnull().sum()}")
print(f"  Null metric_key:      {fact_table['metric_key'].isnull().sum()}")

# =====================================================================
# STEP 5: LOAD INTO SQLite DATABASE
# =====================================================================
print("\n" + "=" * 70)
print(" STEP 5: LOADING INTO SQLite DATA WAREHOUSE")
print("=" * 70)

# Remove existing DB
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# DDL: Create tables
ddl_script = """
-- ========================================================
-- DMDW PROJECT — Star Schema DDL
-- Team: Data Miners | Member: 24MIC0068
-- Database: diabetes_dw.db (SQLite)
-- ========================================================

-- Dimension: Demographics
CREATE TABLE dim_demographics (
    demographic_key INTEGER PRIMARY KEY,
    gender          TEXT NOT NULL,
    age_group       TEXT NOT NULL,
    life_stage      TEXT NOT NULL
);

-- Dimension: Clinical Risk Factors
CREATE TABLE dim_clinical_risk (
    risk_key              INTEGER PRIMARY KEY,
    hypertension          INTEGER NOT NULL,
    heart_disease         INTEGER NOT NULL,
    smoking_history       TEXT NOT NULL,
    hypertension_status   TEXT NOT NULL,
    heart_disease_status  TEXT NOT NULL
);

-- Dimension: Metric Ranges (Clinical Binning)
CREATE TABLE dim_metric_ranges (
    metric_key        INTEGER PRIMARY KEY,
    bmi_category      TEXT NOT NULL,
    hba1c_category    TEXT NOT NULL,
    glucose_category  TEXT NOT NULL
);

-- Fact: Patient Screening Assessments
CREATE TABLE fact_patient_screening (
    screening_key       INTEGER PRIMARY KEY,
    demographic_key     INTEGER NOT NULL,
    risk_key            INTEGER NOT NULL,
    metric_key          INTEGER NOT NULL,
    age                 REAL,
    bmi                 REAL,
    hba1c_level         REAL,
    blood_glucose_level INTEGER,
    is_diabetic         INTEGER NOT NULL,
    FOREIGN KEY (demographic_key) REFERENCES dim_demographics(demographic_key),
    FOREIGN KEY (risk_key)        REFERENCES dim_clinical_risk(risk_key),
    FOREIGN KEY (metric_key)      REFERENCES dim_metric_ranges(metric_key)
);
"""

# Execute DDL
cursor.executescript(ddl_script)
print("✅ DDL executed: 3 dimension tables + 1 fact table created")

# Save DDL to file
ddl_path = f"{SQL_DIR}/01_star_schema_ddl.sql"
with open(ddl_path, 'w') as f:
    f.write(ddl_script)
print(f"💾 DDL saved: {ddl_path}")

# Load data
dim_demo.to_sql('dim_demographics', conn, if_exists='append', index=False)
dim_risk.to_sql('dim_clinical_risk', conn, if_exists='append', index=False)
dim_metrics.to_sql('dim_metric_ranges', conn, if_exists='append', index=False)
fact_table.to_sql('fact_patient_screening', conn, if_exists='append', index=False)

print(f"\n📊 Data loaded into SQLite:")
for table in ['dim_demographics', 'dim_clinical_risk', 'dim_metric_ranges', 'fact_patient_screening']:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table}: {count:,} rows")

# =====================================================================
# STEP 6: EXECUTE 5 OLAP OPERATIONS
# =====================================================================
print("\n" + "=" * 70)
print(" STEP 6: EXECUTING 5 OLAP OPERATIONS")
print("=" * 70)

olap_queries = {}

# ─── OLAP 1: ROLL-UP ────────────────────────────────────────────────────
# Roll-up: Age Group → Life Stage (aggregate from finer to coarser grain)
q_rollup = """
-- OLAP OPERATION 1: ROLL-UP
-- Aggregate diabetes prevalence from Age Group → Life Stage
SELECT
    d.life_stage,
    COUNT(*)                            AS total_patients,
    SUM(f.is_diabetic)                  AS diabetic_count,
    ROUND(AVG(f.is_diabetic) * 100, 2)  AS diabetes_prevalence_pct,
    ROUND(AVG(f.hba1c_level), 2)        AS avg_hba1c,
    ROUND(AVG(f.bmi), 2)                AS avg_bmi
FROM fact_patient_screening f
JOIN dim_demographics d ON f.demographic_key = d.demographic_key
GROUP BY d.life_stage
ORDER BY diabetes_prevalence_pct DESC;
"""
olap_queries['rollup'] = q_rollup
print("\n── OLAP 1: ROLL-UP (Age Group → Life Stage) ──")
result = pd.read_sql_query(q_rollup, conn)
print(result.to_string(index=False))

# ─── OLAP 2: DRILL-DOWN ─────────────────────────────────────────────────
# Drill-down: Gender → Gender + BMI Category (expand from coarser to finer)
q_drilldown = """
-- OLAP OPERATION 2: DRILL-DOWN
-- Expand diabetes prevalence from Gender → Gender + BMI Category
SELECT
    d.gender,
    m.bmi_category,
    COUNT(*)                            AS total_patients,
    SUM(f.is_diabetic)                  AS diabetic_count,
    ROUND(AVG(f.is_diabetic) * 100, 2)  AS diabetes_prevalence_pct
FROM fact_patient_screening f
JOIN dim_demographics d ON f.demographic_key = d.demographic_key
JOIN dim_metric_ranges m ON f.metric_key = m.metric_key
GROUP BY d.gender, m.bmi_category
ORDER BY d.gender, diabetes_prevalence_pct DESC;
"""
olap_queries['drilldown'] = q_drilldown
print("\n── OLAP 2: DRILL-DOWN (Gender → Gender + BMI Category) ──")
result = pd.read_sql_query(q_drilldown, conn)
print(result.to_string(index=False))

# ─── OLAP 3: SLICE ──────────────────────────────────────────────────────
# Slice: Fix one dimension — HbA1c Category = 'Diabetes (≥6.5)'
q_slice = """
-- OLAP OPERATION 3: SLICE
-- Fix dimension: HbA1c Category = 'Diabetes (≥6.5)'
-- Analyze diabetes prevalence across age groups for high-risk HbA1c patients
SELECT
    d.age_group,
    d.gender,
    COUNT(*)                            AS total_patients,
    SUM(f.is_diabetic)                  AS diabetic_count,
    ROUND(AVG(f.is_diabetic) * 100, 2)  AS diabetes_prevalence_pct,
    ROUND(AVG(f.blood_glucose_level), 1) AS avg_glucose
FROM fact_patient_screening f
JOIN dim_demographics d ON f.demographic_key = d.demographic_key
JOIN dim_metric_ranges m ON f.metric_key = m.metric_key
WHERE m.hba1c_category = 'Diabetes (≥6.5)'
GROUP BY d.age_group, d.gender
ORDER BY d.age_group, d.gender;
"""
olap_queries['slice'] = q_slice
print("\n── OLAP 3: SLICE (HbA1c Category = 'Diabetes ≥6.5') ──")
result = pd.read_sql_query(q_slice, conn)
print(result.to_string(index=False))

# ─── OLAP 4: DICE ───────────────────────────────────────────────────────
# Dice: Select sub-cube — Age Group '45-59' AND Hypertension = Yes AND BMI = Obese
q_dice = """
-- OLAP OPERATION 4: DICE
-- Sub-cube: Age 45-59 (Middle-Aged) AND Hypertension = Yes AND BMI = Obese
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
ORDER BY diabetes_prevalence_pct DESC;
"""
olap_queries['dice'] = q_dice
print("\n── OLAP 4: DICE (Age 45-59 & Hypertension & Obese) ──")
result = pd.read_sql_query(q_dice, conn)
print(result.to_string(index=False))

# ─── OLAP 5: PIVOT ──────────────────────────────────────────────────────
# Pivot: Swap axes — Gender on rows, BMI Category on columns, value = Diabetes %
q_pivot = """
-- OLAP OPERATION 5: PIVOT
-- Rows: Gender | Columns: BMI Category | Cell: Diabetes Prevalence %
SELECT
    d.gender,
    ROUND(AVG(CASE WHEN m.bmi_category = 'Underweight' THEN f.is_diabetic END) * 100, 2)
        AS "Underweight_%",
    ROUND(AVG(CASE WHEN m.bmi_category = 'Normal' THEN f.is_diabetic END) * 100, 2)
        AS "Normal_%",
    ROUND(AVG(CASE WHEN m.bmi_category = 'Overweight' THEN f.is_diabetic END) * 100, 2)
        AS "Overweight_%",
    ROUND(AVG(CASE WHEN m.bmi_category = 'Obese' THEN f.is_diabetic END) * 100, 2)
        AS "Obese_%"
FROM fact_patient_screening f
JOIN dim_demographics d ON f.demographic_key = d.demographic_key
JOIN dim_metric_ranges m ON f.metric_key = m.metric_key
GROUP BY d.gender
ORDER BY d.gender;
"""
olap_queries['pivot'] = q_pivot
print("\n── OLAP 5: PIVOT (Gender × BMI Category → Diabetes %) ──")
result = pd.read_sql_query(q_pivot, conn)
print(result.to_string(index=False))

# =====================================================================
# STEP 7: SAVE ALL OLAP QUERIES TO .SQL FILE
# =====================================================================
olap_path = f"{SQL_DIR}/02_olap_queries.sql"
with open(olap_path, 'w') as f:
    f.write("-- ========================================================\n")
    f.write("-- DMDW PROJECT — 5 OLAP Operations\n")
    f.write("-- Team: Data Miners | Member: 24MIC0068\n")
    f.write("-- Database: diabetes_dw.db (SQLite)\n")
    f.write("-- ========================================================\n\n")
    for name, query in olap_queries.items():
        f.write(query)
        f.write("\n\n")

print(f"\n💾 All OLAP queries saved: {olap_path}")

conn.close()

print("\n" + "=" * 70)
print(" ✅ DATA WAREHOUSE BUILD & OLAP OPERATIONS COMPLETE")
print("=" * 70)
print(f"  Database:    {DB_PATH}")
print(f"  DDL Script:  {SQL_DIR}/01_star_schema_ddl.sql")
print(f"  OLAP Script: {SQL_DIR}/02_olap_queries.sql")
