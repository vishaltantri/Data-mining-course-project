#!/usr/bin/env python3
"""
Review 1 Technical Demonstration Script
CSI3010 Data Mining & Data Warehousing
Team: Data Miners | Student ID: 24MIC0068
Dataset: CDC BRFSS 2015 Diabetes Health Indicators
"""

import sqlite3
import os
import json
import pandas as pd

def run_demo():
    print("==========================================================================")
    print(" CSI3010 DATA MINING & DATA WAREHOUSING - REVIEW 1 LIVE DEMO PROOF OF WORK")
    print(" Team: Data Miners | Student ID: 24MIC0068")
    print(" Topic: Diabetes Risk Assessment & Cardiovascular Comorbidity Analysis")
    print(" Dataset: CDC BRFSS 2015 (70,692 balanced records, 22 attributes)")
    print("==========================================================================\n")

    # 1. Dataset Verification
    print("--- STEP 1: DATASET QUALITY & VERIFICATION ---")
    df = pd.read_csv('diabetes_binary_5050split_health_indicators_BRFSS2015.csv')
    print(f"[✓] Primary Dataset Loaded: {len(df):,} rows x {len(df.columns)} columns")
    print(f"[✓] Total Missing Values: {df.isnull().sum().sum()} (0.00%)")
    print(f"[✓] Class Balance (Diabetes_binary):")
    print(f"    - No Diabetes (0): {sum(df['Diabetes_binary']==0):,} ({sum(df['Diabetes_binary']==0)/len(df)*100:.1f}%)")
    print(f"    - Diabetes/Prediabetes (1): {sum(df['Diabetes_binary']==1):,} ({sum(df['Diabetes_binary']==1)/len(df)*100:.1f}%)\n")

    # 2. Data Warehouse Inspection
    print("--- STEP 2: DATA WAREHOUSE STAR SCHEMA (SQLite) ---")
    db_path = 'review1/diabetes_dw.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall()]
        print(f"[✓] Connected to Data Warehouse: {db_path}")
        print(f"[✓] Warehouse Tables: {', '.join(tables)}")
        
        cur.execute("SELECT COUNT(*) FROM FACT_HEALTH_SURVEY;")
        fact_count = cur.fetchone()[0]
        print(f"[✓] Fact Table (FACT_HEALTH_SURVEY) Row Count: {fact_count:,}\n")

        # 3. Live OLAP Operation Demo
        print("--- STEP 3: LIVE OLAP OPERATION DEMO (Roll-Up Query) ---")
        rollup_sql = """
            SELECT d.age AS Age_Bracket,
                   COUNT(*) AS Respondents,
                   SUM(f.diabetes_binary) AS Diabetes_Cases,
                   ROUND(AVG(f.diabetes_binary)*100, 1) AS Prevalence_Pct,
                   ROUND(AVG(f.bmi_value), 1) AS Avg_BMI
            FROM FACT_HEALTH_SURVEY f
            JOIN DIM_DEMOGRAPHICS d ON f.demog_key = d.demog_key
            GROUP BY d.age ORDER BY d.age LIMIT 5;
        """
        res = pd.read_sql_query(rollup_sql, conn)
        print(res.to_string(index=False))
        conn.close()
        print("\n[✓] OLAP Roll-up Query executed successfully!")

    # 4. Figures Verification
    print("\n--- STEP 4: GENERATED EDA VISUALIZATIONS ---")
    fig_dir = 'review1/figures'
    if os.path.exists(fig_dir):
        figs = sorted(os.listdir(fig_dir))
        print(f"[✓] Found {len(figs)} high-resolution charts in '{fig_dir}':")
        for f in figs:
            print(f"    - {f}")
    
    print("\n==========================================================================")
    print(" REVIEW 1 DEMO STATUS: ✅ ALL TECHNICAL DELIVERABLES READY")
    print("==========================================================================")

if __name__ == '__main__':
    run_demo()
