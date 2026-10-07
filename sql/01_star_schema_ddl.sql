
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
