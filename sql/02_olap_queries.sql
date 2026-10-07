-- ========================================================
-- DMDW PROJECT — 5 OLAP Operations
-- Team: Data Miners | Member: 24MIC0068
-- Database: diabetes_dw.db (SQLite)
-- ========================================================


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


