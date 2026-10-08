import sqlite3
import pandas as pd
import json
import os

db_path = 'review1/diabetes_dw.db'
sql_dir = 'review1/sql'
os.makedirs(sql_dir, exist_ok=True)

if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Create Star Schema DDL
ddl_sql = """
-- Dimension Tables
CREATE TABLE DIM_DEMOGRAPHICS (
    demog_key INTEGER PRIMARY KEY AUTOINCREMENT,
    age INTEGER,
    sex INTEGER,
    education INTEGER,
    income INTEGER
);

CREATE TABLE DIM_LIFESTYLE (
    lifestyle_key INTEGER PRIMARY KEY AUTOINCREMENT,
    smoker INTEGER,
    phys_activity INTEGER,
    fruits INTEGER,
    veggies INTEGER,
    hvy_alcohol_consump INTEGER
);

CREATE TABLE DIM_CLINICAL_RISK (
    clinical_key INTEGER PRIMARY KEY AUTOINCREMENT,
    high_bp INTEGER,
    high_chol INTEGER,
    chol_check INTEGER,
    stroke INTEGER,
    heart_disease_or_attack INTEGER,
    diff_walk INTEGER,
    any_healthcare INTEGER,
    no_doc_bc_cost INTEGER
);

CREATE TABLE DIM_GENERAL_HEALTH (
    genhealth_key INTEGER PRIMARY KEY AUTOINCREMENT,
    gen_hlth_rating INTEGER
);

-- Fact Table
CREATE TABLE FACT_HEALTH_SURVEY (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    demog_key INTEGER,
    lifestyle_key INTEGER,
    clinical_key INTEGER,
    genhealth_key INTEGER,
    diabetes_binary INTEGER,
    ment_hlth_days INTEGER,
    phys_hlth_days INTEGER,
    bmi_value REAL,
    FOREIGN KEY (demog_key) REFERENCES DIM_DEMOGRAPHICS(demog_key),
    FOREIGN KEY (lifestyle_key) REFERENCES DIM_LIFESTYLE(lifestyle_key),
    FOREIGN KEY (clinical_key) REFERENCES DIM_CLINICAL_RISK(clinical_key),
    FOREIGN KEY (genhealth_key) REFERENCES DIM_GENERAL_HEALTH(genhealth_key)
);
"""

cursor.executescript(ddl_sql)
with open(os.path.join(sql_dir, '01_star_schema.sql'), 'w') as f:
    f.write(ddl_sql)

print("Created SQLite Data Warehouse tables.")

# 2. Extract from CSV and Load into DW
df = pd.read_csv('diabetes_binary_5050split_health_indicators_BRFSS2015.csv')

# Unique dimension records
demog_df = df[['Age', 'Sex', 'Education', 'Income']].drop_duplicates().reset_index(drop=True)
demog_df.columns = ['age', 'sex', 'education', 'income']
demog_df.to_sql('DIM_DEMOGRAPHICS', conn, if_exists='append', index=False)

lifestyle_df = df[['Smoker', 'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump']].drop_duplicates().reset_index(drop=True)
lifestyle_df.columns = ['smoker', 'phys_activity', 'fruits', 'veggies', 'hvy_alcohol_consump']
lifestyle_df.to_sql('DIM_LIFESTYLE', conn, if_exists='append', index=False)

clinical_df = df[['HighBP', 'HighChol', 'CholCheck', 'Stroke', 'HeartDiseaseorAttack', 'DiffWalk', 'AnyHealthcare', 'NoDocbcCost']].drop_duplicates().reset_index(drop=True)
clinical_df.columns = ['high_bp', 'high_chol', 'chol_check', 'stroke', 'heart_disease_or_attack', 'diff_walk', 'any_healthcare', 'no_doc_bc_cost']
clinical_df.to_sql('DIM_CLINICAL_RISK', conn, if_exists='append', index=False)

genhealth_df = df[['GenHlth']].drop_duplicates().reset_index(drop=True)
genhealth_df.columns = ['gen_hlth_rating']
genhealth_df.to_sql('DIM_GENERAL_HEALTH', conn, if_exists='append', index=False)

# Fetch surrogate keys mapping
demog_map = pd.read_sql('SELECT demog_key, age, sex, education, income FROM DIM_DEMOGRAPHICS', conn)
lifestyle_map = pd.read_sql('SELECT lifestyle_key, smoker, phys_activity, fruits, veggies, hvy_alcohol_consump FROM DIM_LIFESTYLE', conn)
clinical_map = pd.read_sql('SELECT clinical_key, high_bp, high_chol, chol_check, stroke, heart_disease_or_attack, diff_walk, any_healthcare, no_doc_bc_cost FROM DIM_CLINICAL_RISK', conn)
genhealth_map = pd.read_sql('SELECT genhealth_key, gen_hlth_rating FROM DIM_GENERAL_HEALTH', conn)

# Map surrogate keys to original dataset
df_fact = df.merge(demog_map, left_on=['Age', 'Sex', 'Education', 'Income'], right_on=['age', 'sex', 'education', 'income'])
df_fact = df_fact.merge(lifestyle_map, left_on=['Smoker', 'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump'], right_on=['smoker', 'phys_activity', 'fruits', 'veggies', 'hvy_alcohol_consump'])
df_fact = df_fact.merge(clinical_map, left_on=['HighBP', 'HighChol', 'CholCheck', 'Stroke', 'HeartDiseaseorAttack', 'DiffWalk', 'AnyHealthcare', 'NoDocbcCost'], right_on=['high_bp', 'high_chol', 'chol_check', 'stroke', 'heart_disease_or_attack', 'diff_walk', 'any_healthcare', 'no_doc_bc_cost'])
df_fact = df_fact.merge(genhealth_map, left_on=['GenHlth'], right_on=['gen_hlth_rating'])

fact_insert = df_fact[['demog_key', 'lifestyle_key', 'clinical_key', 'genhealth_key', 'Diabetes_binary', 'MentHlth', 'PhysHlth', 'BMI']]
fact_insert.columns = ['demog_key', 'lifestyle_key', 'clinical_key', 'genhealth_key', 'diabetes_binary', 'ment_hlth_days', 'phys_hlth_days', 'bmi_value']

fact_insert.to_sql('FACT_HEALTH_SURVEY', conn, if_exists='append', index=False)
print(f"Loaded {len(fact_insert)} fact rows into FACT_HEALTH_SURVEY.")

# --- OLAP OPERATIONS ---
olap_queries = {
    "Roll-up": """
        -- Roll-up: Diabetes Prevalence by Age Group (Higher Age Hierarchy Level)
        SELECT d.age AS Age_Bracket,
               COUNT(*) AS Total_Respondents,
               SUM(f.diabetes_binary) AS Diabetes_Cases,
               ROUND(AVG(f.diabetes_binary)*100, 2) AS Prevalence_Pct,
               ROUND(AVG(f.bmi_value), 2) AS Avg_BMI
        FROM FACT_HEALTH_SURVEY f
        JOIN DIM_DEMOGRAPHICS d ON f.demog_key = d.demog_key
        GROUP BY d.age
        ORDER BY d.age;
    """,
    "Drill-down": """
        -- Drill-down: Diabetes Prevalence by Age Bracket AND Sex
        SELECT d.age AS Age_Bracket,
               CASE WHEN d.sex = 0 THEN 'Female' ELSE 'Male' END AS Gender,
               COUNT(*) AS Total_Respondents,
               SUM(f.diabetes_binary) AS Diabetes_Cases,
               ROUND(AVG(f.diabetes_binary)*100, 2) AS Prevalence_Pct
        FROM FACT_HEALTH_SURVEY f
        JOIN DIM_DEMOGRAPHICS d ON f.demog_key = d.demog_key
        WHERE d.age IN (9, 10, 11) -- Age 60-74
        GROUP BY d.age, d.sex
        ORDER BY d.age, d.sex;
    """,
    "Slice": """
        -- Slice: Fixing Clinical Risk Dimension to High BP = 1 (Hypertension Slice)
        SELECT g.gen_hlth_rating AS General_Health,
               COUNT(*) AS Total_Respondents,
               SUM(f.diabetes_binary) AS Diabetes_Cases,
               ROUND(AVG(f.diabetes_binary)*100, 2) AS Diabetes_Prevalence_Pct
        FROM FACT_HEALTH_SURVEY f
        JOIN DIM_CLINICAL_RISK c ON f.clinical_key = c.clinical_key
        JOIN DIM_GENERAL_HEALTH g ON f.genhealth_key = g.genhealth_key
        WHERE c.high_bp = 1
        GROUP BY g.gen_hlth_rating
        ORDER BY g.gen_hlth_rating;
    """,
    "Dice": """
        -- Dice: Sub-cube filtering Age >= 9 (60+), High BP = 1, and High Cholesterol = 1
        SELECT d.income AS Income_Bracket,
               l.smoker AS Smoker_Status,
               COUNT(*) AS Respondent_Count,
               ROUND(AVG(f.diabetes_binary)*100, 2) AS Diabetes_Prevalence_Pct
        FROM FACT_HEALTH_SURVEY f
        JOIN DIM_DEMOGRAPHICS d ON f.demog_key = d.demog_key
        JOIN DIM_CLINICAL_RISK c ON f.clinical_key = c.clinical_key
        JOIN DIM_LIFESTYLE l ON f.lifestyle_key = l.lifestyle_key
        WHERE d.age >= 9 AND c.high_bp = 1 AND c.high_chol = 1
        GROUP BY d.income, l.smoker
        ORDER BY d.income, l.smoker;
    """,
    "Pivot": """
        -- Pivot: Age Bracket vs Gender matrix of Diabetes Cases
        SELECT d.age AS Age_Bracket,
               SUM(CASE WHEN d.sex = 0 THEN f.diabetes_binary ELSE 0 END) AS Female_Diabetes_Cases,
               SUM(CASE WHEN d.sex = 1 THEN f.diabetes_binary ELSE 0 END) AS Male_Diabetes_Cases,
               ROUND(AVG(f.diabetes_binary)*100, 2) AS Overall_Prevalence_Pct
        FROM FACT_HEALTH_SURVEY f
        JOIN DIM_DEMOGRAPHICS d ON f.demog_key = d.demog_key
        GROUP BY d.age
        ORDER BY d.age;
    """
}

olap_results = {}
sql_file_content = ""

for op_name, q in olap_queries.items():
    res_df = pd.read_sql_query(q, conn)
    olap_results[op_name] = res_df.to_dict(orient='records')
    sql_file_content += f"-- ==============================================\n-- {op_name} Query\n-- ==============================================\n{q.strip()}\n\n"

with open(os.path.join(sql_dir, '02_olap_queries.sql'), 'w') as f:
    f.write(sql_file_content)

with open('review1/olap_results.json', 'w') as f:
    json.dump(olap_results, f, indent=2)

print("OLAP queries executed and saved.")
conn.close()
