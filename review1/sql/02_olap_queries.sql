-- ==============================================
-- Roll-up Query
-- ==============================================
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

-- ==============================================
-- Drill-down Query
-- ==============================================
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

-- ==============================================
-- Slice Query
-- ==============================================
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

-- ==============================================
-- Dice Query
-- ==============================================
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

-- ==============================================
-- Pivot Query
-- ==============================================
-- Pivot: Age Bracket vs Gender matrix of Diabetes Cases
        SELECT d.age AS Age_Bracket,
               SUM(CASE WHEN d.sex = 0 THEN f.diabetes_binary ELSE 0 END) AS Female_Diabetes_Cases,
               SUM(CASE WHEN d.sex = 1 THEN f.diabetes_binary ELSE 0 END) AS Male_Diabetes_Cases,
               ROUND(AVG(f.diabetes_binary)*100, 2) AS Overall_Prevalence_Pct
        FROM FACT_HEALTH_SURVEY f
        JOIN DIM_DEMOGRAPHICS d ON f.demog_key = d.demog_key
        GROUP BY d.age
        ORDER BY d.age;

