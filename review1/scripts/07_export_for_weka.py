#!/usr/bin/env python3
"""Review 1 — export the star-schema data warehouse to WEKA.

Run from the repository root:   python3 review1/scripts/07_export_for_weka.py
Reads : review1/diabetes_dw.db (star schema built by 03_build_warehouse.py)
        diabetes_binary_5050split_health_indicators_BRFSS2015.csv (for verification)
Writes: review1/weka/diabetes_dw_export.arff   (70,692 instances x 22 attributes)
        review1/weka/diabetes_dw_export.csv    (same table, for other tools)
        review1/weka/weka_export_summary.txt   (attribute list + class counts)

The class attribute Diabetes_binary is written LAST as nominal {No, YES}
so WEKA Explorer picks it up automatically (positive class = YES).
Row order follows fact_id, which matches the original CSV row order, so the
WEKA export can be matched 1:1 with the R split indices.
"""
import os
import sqlite3
import pandas as pd

DB = "review1/diabetes_dw.db"
CSV = "diabetes_binary_5050split_health_indicators_BRFSS2015.csv"
OUT_DIR = "review1/weka"
os.makedirs(OUT_DIR, exist_ok=True)

# Original column order of the balanced CSV (target moved to the end for WEKA)
COLS = ["HighBP", "HighChol", "CholCheck", "BMI", "Smoker", "Stroke",
        "HeartDiseaseorAttack", "PhysActivity", "Fruits", "Veggies",
        "HvyAlcoholConsump", "AnyHealthcare", "NoDocbcCost", "GenHlth",
        "MentHlth", "PhysHlth", "DiffWalk", "Sex", "Age", "Education", "Income",
        "Diabetes_binary"]

conn = sqlite3.connect(DB)
df = pd.read_sql_query("""
    SELECT
        c.high_bp               AS HighBP,
        c.high_chol             AS HighChol,
        c.chol_check            AS CholCheck,
        f.bmi_value             AS BMI,
        l.smoker                AS Smoker,
        c.stroke                AS Stroke,
        c.heart_disease_or_attack AS HeartDiseaseorAttack,
        l.phys_activity         AS PhysActivity,
        l.fruits                AS Fruits,
        l.veggies               AS Veggies,
        l.hvy_alcohol_consump   AS HvyAlcoholConsump,
        c.any_healthcare        AS AnyHealthcare,
        c.no_doc_bc_cost        AS NoDocbcCost,
        g.gen_hlth_rating       AS GenHlth,
        f.ment_hlth_days        AS MentHlth,
        f.phys_hlth_days        AS PhysHlth,
        c.diff_walk             AS DiffWalk,
        d.sex                   AS Sex,
        d.age                  AS Age,
        d.education            AS Education,
        d.income               AS Income,
        f.diabetes_binary      AS Diabetes_binary
    FROM FACT_HEALTH_SURVEY f
    JOIN DIM_DEMOGRAPHICS  d ON f.demog_key    = d.demog_key
    JOIN DIM_LIFESTYLE     l ON f.lifestyle_key = l.lifestyle_key
    JOIN DIM_CLINICAL_RISK c ON f.clinical_key  = c.clinical_key
    JOIN DIM_GENERAL_HEALTH g ON f.genhealth_key = g.genhealth_key
    ORDER BY f.fact_id
""", conn)
conn.close()

df = df[COLS]

# --- Verify against the source CSV -----------------------------------------
src = pd.read_csv(CSV)
assert len(df) == len(src) == 70692, f"row mismatch: {len(df)} vs {len(src)}"
mismatch = 0
for c in COLS:
    a = df[c].astype(float).to_numpy()
    b = src[c].astype(float).to_numpy()
    mismatch += int((a != b).sum())
print(f"Cell mismatches vs source CSV: {mismatch}")
assert mismatch == 0, "DW export does not reproduce the source CSV"

# --- Write CSV ---------------------------------------------------------------
csv_path = os.path.join(OUT_DIR, "diabetes_dw_export.csv")
df.to_csv(csv_path, index=False)

# --- Write ARFF --------------------------------------------------------------
int_cols = [c for c in COLS if c != "BMI"]
arff_path = os.path.join(OUT_DIR, "diabetes_dw_export.arff")
with open(arff_path, "w") as f:
    f.write("% Data warehouse export: FACT_HEALTH_SURVEY joined to 4 dimensions\n")
    f.write("% Source: review1/diabetes_dw.db (CDC BRFSS 2015, balanced 50/50 file)\n")
    f.write("% Instances: 70692   Attributes: 22   Class: Diabetes_binary {NO, YES} (last)\n")
    f.write("@relation diabetes_dw_export\n\n")
    for c in COLS:
        if c == "Diabetes_binary":
            f.write('@attribute Diabetes_binary {NO, YES}\n')
        else:
            f.write(f"@attribute {c} numeric\n")
    f.write("\n@data\n")
    for row in df.itertuples(index=False):
        vals = []
        for c, v in zip(COLS, row):
            if c == "Diabetes_binary":
                vals.append("YES" if float(v) == 1.0 else "NO")
            elif c == "BMI":
                vals.append(f"{float(v):g}")
            else:
                vals.append(str(int(float(v))))
        f.write(",".join(vals) + "\n")

# --- Write summary -----------------------------------------------------------
summary_path = os.path.join(OUT_DIR, "weka_export_summary.txt")
n_yes = int((df["Diabetes_binary"] == 1).sum())
n_no = int((df["Diabetes_binary"] == 0).sum())
with open(summary_path, "w") as f:
    f.write("WEKA EXPORT SUMMARY\n")
    f.write("=" * 60 + "\n")
    f.write(f"Source database : {DB}\n")
    f.write(f"Source CSV      : {CSV}\n")
    f.write(f"Instances       : {len(df)}\n")
    f.write(f"Attributes      : {len(COLS)} (class = Diabetes_binary, last)\n")
    f.write(f"Class NO        : {n_no} ({100 * n_no / len(df):.2f}%)\n")
    f.write(f"Class YES       : {n_yes} ({100 * n_yes / len(df):.2f}%)\n")
    f.write(f"Cell mismatches vs source CSV: {mismatch}\n")
    f.write("\nAttributes (in ARFF order):\n")
    for i, c in enumerate(COLS, 1):
        f.write(f"  {i:2d}. {c}\n")
    f.write("\nFiles written:\n")
    f.write("  diabetes_dw_export.arff\n")
    f.write("  diabetes_dw_export.csv\n")
    f.write("  weka_export_summary.txt\n")

print(f"Instances: {len(df)}, Attributes: {len(COLS)}, "
      f"YES: {n_yes}, NO: {n_no}")
print(f"Wrote {arff_path}, {csv_path}, {summary_path}")
