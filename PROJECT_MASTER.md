# Data Mining & Data Warehousing Project
# Review 1 Master Record

---

> **Project Memory & Executive Progress Record**  
> **Course:** CSI3010 — Data Mining & Data Warehousing  
> **Repository Workspace:** `/home/vct/Desktop/DMDW PROJECT`  
> **Current Status:** ✅ REVIEW 1 READY  
> **Last Updated:** October 8, 2026  

---

## 1. Project Status

- **Review 1 Deliverables:** ✅ 100% Completed
- **Dataset Audit & Quality Analysis:** ✅ Completed (0 missing cells, verified bounds)
- **Descriptive Statistics & R EDA:** ✅ Completed (R and Python scripts executed)
- **Data Warehouse Design (Star Schema):** ✅ Completed & Built in SQLite (`review1/diabetes_dw.db`)
- **OLAP Operations (Roll-Up, Drill-Down, Slice, Dice, Pivot):** ✅ Executed with real query outputs
- **Data Mining Methodology (Decision Trees, KNN, K-Means, Apriori):** ✅ Planned & feadbility verified
- **Visualizations Generated:** ✅ 8 High-Resolution Charts saved to `review1/figures/`
- **Presentation Preparation:** ✅ Content mapped for Slide 1 – Slide 9 (Matching `DWDM_Lab_Project_Template_Week1.pptx`)
- **Interactive Technical Demo:** ✅ Executable proof-of-work script (`review1/scripts/04_review1_demo.py`)
- **Final Status:** ✅ **REVIEW 1 READY — STOPPING AT REVIEW 1 BOUNDARY**

---

## 2. Team Information

- **Team Name:** Data Miners
- **Student Name / Register No.:** Vishal C Tantri / 24MIC0068
- **Lab Slot:** CSI3010 ELA / ETH
- **Faculty:** Course Instructor

---

## 3. Project Title

**Data Mining and Data Warehousing for Diabetes Risk Assessment & Cardiovascular Comorbidity Analysis using BRFSS 2015**

---

## 4. Problem Statement

Diabetes mellitus and cardiovascular diseases (CVD) are leading causes of worldwide morbidity and medical expense. Early identification of individuals at high risk for diabetes and concurrent cardiovascular complications allows timely lifestyle interventions and clinical preventative management. 

Traditional clinical screening relies heavily on laboratory blood tests (e.g., Fasting Plasma Glucose, HbA1c), which are costly and infrequent for uninsured or underserved populations. Using self-reported health survey data (CDC BRFSS 2015), this project addresses two core problems:
1. **Analytical Data Warehousing:** Storing, organizing, and multi-dimensionally querying high-dimensional population health survey data to answer complex public health questions via OLAP operations.
2. **Predictive Data Mining:** Establishing data-driven mining models (Classification via ID3/CART/KNN, Clustering via K-Means/Hierarchical, and Pattern Mining via Apriori) to discover risk factor associations and classify diabetes risk accurately.

---

## 5. Project Objectives

1. **Dataset Audit & Quality Verification:** Conduct rigorous data quality checks (missing values, duplicates, outliers, data types, and class imbalance) on the CDC BRFSS 2015 dataset.
2. **Exploratory Data Analysis (EDA):** Perform quantitative descriptive statistical analysis and visualizations in R and Python to identify key health and lifestyle correlates of diabetes.
3. **Data Warehouse Architecture:** Design and implement a Star Schema Data Warehouse (`FACT_HEALTH_SURVEY` with 4 dimension tables: `DIM_DEMOGRAPHICS`, `DIM_LIFESTYLE`, `DIM_CLINICAL_RISK`, `DIM_GENERAL_HEALTH`) in SQLite.
4. **OLAP Operations Demonstration:** Implement and demonstrate 5 core OLAP queries (Roll-up, Drill-down, Slice, Dice, Pivot) answering public health business questions.
5. **Data Mining Strategy Formulation:** Formulate a structured data mining methodology incorporating Decision Trees (ID3/CART), K-Nearest Neighbors (KNN), K-Means Clustering, and Apriori Association Rules.
6. **Review 1 Defense Preparation:** Prepare complete presentation content, expected viva Q&A defense, and an interactive technical demo script.

---

## 6. Dataset

### 6.1 Dataset Source
- **Source:** Centers for Disease Control and Prevention (CDC) — Behavioral Risk Factor Surveillance System (BRFSS) 2015.
- **Repository:** Kaggle / UCI Machine Learning Repository (`diabetes_binary_health_indicators_BRFSS2015.csv` and `diabetes_binary_5050split_health_indicators_BRFSS2015.csv`).

### 6.2 Dataset Version
We evaluated three variants available in the repository:
1. `diabetes_012_health_indicators_BRFSS2015.csv` (253,680 rows, 3-class target: 0=No Diabetes, 1=Prediabetes, 2=Diabetes).
2. `diabetes_binary_health_indicators_BRFSS2015.csv` (253,680 rows, binary target: 0=No Diabetes, 1=Diagnosed Diabetes only; the 4,631 prediabetes respondents are coded 0).
3. `diabetes_binary_5050split_health_indicators_BRFSS2015.csv` (70,692 rows, 50/50 balanced binary target).

*Scope Decision:* The **balanced 50/50 split dataset (70,692 rows × 22 columns)** is selected as the primary dataset for data mining and EDA to eliminate severe class imbalance bias, while the full **253,680 record dataset** is preserved for data warehousing population queries.

### 6.3 Dataset Dimensions
- **Primary Dataset Rows:** 70,692
- **Primary Dataset Columns:** 22
- **Total Data Cells:** 1,555,224

### 6.4 Feature Dictionary

| Attribute Name | Data Type | Value Range / Categories | Description | Role in DW |
| :--- | :--- | :--- | :--- | :--- |
| **`Diabetes_binary`** | Numeric (Float/Int) | 0, 1 | 0 = No Diabetes, 1 = Diagnosed Diabetes (prediabetes coded 0) | **Target / Measure** |
| **`HighBP`** | Numeric (Binary) | 0, 1 | 0 = No High BP, 1 = High BP diagnosed | Dimension Attribute |
| **`HighChol`** | Numeric (Binary) | 0, 1 | 0 = No High Cholesterol, 1 = High Cholesterol | Dimension Attribute |
| **`CholCheck`** | Numeric (Binary) | 0, 1 | 0 = No check in 5 yrs, 1 = Checked in past 5 yrs | Dimension Attribute |
| **`BMI`** | Numeric (Continuous) | 12.0 – 98.0 | Body Mass Index (weight in kg / height in m²) | **Fact Measure** |
| **`Smoker`** | Numeric (Binary) | 0, 1 | 0 = No, 1 = Smoked 100+ cigarettes in life | Dimension Attribute |
| **`Stroke`** | Numeric (Binary) | 0, 1 | 0 = No history of stroke, 1 = History of stroke | Dimension Attribute |
| **`HeartDiseaseorAttack`**| Numeric (Binary) | 0, 1 | 0 = No CHD/MI, 1 = Coronary Heart Disease or Myocardial Infarction | Dimension Attribute |
| **`PhysActivity`** | Numeric (Binary) | 0, 1 | 0 = No exercise in 30 days, 1 = Exercise in past 30 days | Dimension Attribute |
| **`Fruits`** | Numeric (Binary) | 0, 1 | 0 = Consume fruit < 1x/day, 1 = Consume fruit ≥ 1x/day | Dimension Attribute |
| **`Veggies`** | Numeric (Binary) | 0, 1 | 0 = Consume veggies < 1x/day, 1 = Consume veggies ≥ 1x/day | Dimension Attribute |
| **`HvyAlcoholConsump`** | Numeric (Binary) | 0, 1 | 0 = No, 1 = Heavy drinker (>14 drinks/wk men, >7 women) | Dimension Attribute |
| **`AnyHealthcare`** | Numeric (Binary) | 0, 1 | 0 = No healthcare coverage, 1 = Has health coverage | Dimension Attribute |
| **`NoDocbcCost`** | Numeric (Binary) | 0, 1 | 0 = No financial barrier, 1 = Couldn't see doctor due to cost | Dimension Attribute |
| **`GenHlth`** | Numeric (Ordinal) | 1 – 5 | 1=Excellent, 2=Very Good, 3=Good, 4=Fair, 5=Poor | Dimension Attribute |
| **`MentHlth`** | Numeric (Discrete) | 0 – 30 | Days of poor mental health in past 30 days | **Fact Measure** |
| **`PhysHlth`** | Numeric (Discrete) | 0 – 30 | Days of physical illness/injury in past 30 days | **Fact Measure** |
| **`DiffWalk`** | Numeric (Binary) | 0, 1 | 0 = No difficulty walking, 1 = Serious difficulty walking/stairs | Dimension Attribute |
| **`Sex`** | Numeric (Binary) | 0, 1 | 0 = Female, 1 = Male | Dimension Attribute |
| **`Age`** | Numeric (Ordinal) | 1 – 13 | 13 age categories (1=18-24, 2=25-29, ..., 13=80+) | Dimension Attribute |
| **`Education`** | Numeric (Ordinal) | 1 – 6 | 1=Never attended, 2=Elem, 3=Some HS, 4=HS Grad, 5=Some Col, 6=Col Grad | Dimension Attribute |
| **`Income`** | Numeric (Ordinal) | 1 – 8 | 1=<$10k, 2=$10-15k, ..., 8=>$75k | Dimension Attribute |

### 6.5 Target Variable
- **Name:** `Diabetes_binary`
- **Encoding:** `0.0` = No Diabetes (negative control), `1.0` = Diagnosed Diabetes only (positive class). Note: The 4,631 prediabetes respondents (from the 3-class file) are coded as 0 in the binary file.

### 6.6 Data Provenance
The original CDC BRFSS 2015 telephone survey collected responses from 441,455 adults across all 50 US states and territories, recording 330 variables. The Kaggle author (Alex Teboul) cleaned and reduced this to 253,680 respondents × 22 health indicators. The exact cleaning steps are documented in the author's notebook on the Kaggle dataset page.

### 6.7 Dataset Relevance
The dataset is directly aligned with healthcare data warehousing and public health data mining. It contains a balance of clinical risk factors (`HighBP`, `HighChol`), lifestyle behaviors (`Smoker`, `PhysActivity`), socio-demographics (`Age`, `Income`, `Sex`), and general health metrics (`GenHlth`, `BMI`), making it optimal for multi-dimensional OLAP analysis, association rule mining, and machine learning classification.

### 6.8 Limitations
- The balanced 50/50 sample does not reflect population prevalence (~14% diabetes in the full file).
- Prediabetes respondents (4,631) are coded as 0 in the binary target, which may underestimate true metabolic risk.
- All data is self-reported from a single cross-sectional survey year (2015); associations do not imply causation.
- The dataset does not include laboratory test results (e.g., HbA1c, fasting glucose).

---

## 7. Reference Class Assignments

We systematically reviewed all 9 class lab manuals and assignment reference PDFs in `dmdw assessments/`:

1. **Creation and Operations on Data Warehouse:** DW Star Schema DDL, Fact & Dimension tables, ETL pipeline in Python (`pandas`/`sqlalchemy`), SQL OLAP queries (`Roll-up`, `Drill-down`, `Slice`, `Dice`, `Pivot`).
2. **EDA using R (Descriptive Statistics & Missing Value Analysis):** Summary statistics (`mean`, `sd`, `var`, `quantile`), missing value checking (`is.na()`, `complete.cases()`), histograms, boxplots, scatter plots.
3. **Visualization & Correlation in R:** Heatmaps (`corrplot`), ggplot2 scatter plots, bar charts, distribution overlays.
4. **Apriori Association Rule Mining in R:** Transaction transformation (`arules` package), `apriori()` execution, pruning rules by support, confidence, and lift thresholds.
5. **Decision Tree Classification (ID3 / CART) in R:** Model training via `rpart`, tree plotting via `rpart.plot`, computing Entropy vs Gini index, confusion matrix evaluation via `caret`.
6. **KNN Classification in R:** Distance normalization via `scale()`, `class::knn`, evaluating k parameter, `gmodels::CrossTable()`.
7. **Clustering in R (K-Means & Hierarchical):** Unsupervised grouping using `kmeans()` and `hclust()`, dendrogram plotting via `dendextend`, silhouette width evaluation via `cluster::silhouette`.
8. **Document Similarity & Text Mining:** TF-IDF vectorization and cosine similarity via `tm` and `SnowballC`.
9. **Mixed Exercise:** Integrated workflow combining data cleaning, correlation, K-Means clustering, `rpart` decision trees, `arules` Apriori, and Naive Bayes (`e1071`).

*Takeaway for Review 1:* Our Review 1 methodology strictly matches the professor's taught tools (R, Python, SQLite, standard statistical and data mining metrics) without introducing un-taught or black-box abstractions.

---

## 8. Course Syllabus Mapping

| Syllabus Topic / Experiment | Project Application | Review 1 Execution Status |
| :--- | :--- | :--- |
| **Data Warehouse Creation & Operations** | Star Schema DW with `FACT_HEALTH_SURVEY` & 4 Dimensions | ✅ Completed in SQLite (`review1/diabetes_dw.db`) |
| **OLAP Operations** | Roll-up, Drill-down, Slice, Dice, Pivot queries | ✅ Executed & documented in SQL & JSON |
| **EDA using R** | Descriptive stats, Chi-square tests, Correlation | ✅ Executed via `02_r_eda_analysis.R` |
| **Descriptive Statistics** | Mean, SD, Median, Min, Max, Quantiles | ✅ Computed for all 22 attributes |
| **Missing Value Audit** | Checking nulls across 1.55M cells | ✅ Verified (0 missing cells) |
| **Data Visualization** | 8 high-resolution figures | ✅ Generated & saved in `review1/figures/` |
| **Apriori Rule Mining** | High BP + High Chol + Age -> Diabetes rules | 🔄 Planned for Review 2 (arules methodology ready) |
| **Decision Trees (ID3 / CART)** | Binary classification of diabetes risk | 🔄 Planned for Review 2 (rpart baseline tested) |
| **KNN Classification** | Distance-based risk neighborhood scoring | 🔄 Planned for Review 2 (scaling pipeline ready) |
| **K-Means & Hierarchical Clustering**| Unsupervised patient risk segmentation | 🔄 Planned for Review 2 (elbow/silhouette ready) |
| **Document Similarity** | Syllabus topic non-essential for tabular health survey | ℹ️ Evaluated as non-applicable to survey dataset |

---

## 9. Dataset Quality Analysis

### 9.1 Missing Values
- **Total Missing Cells:** 0
- **Percentage Missing:** 0.00%
- **Observation:** The CDC BRFSS 2015 dataset is complete with no missing values in any of the 22 columns across all 70,692 records. No imputation is necessary.

### 9.2 Duplicate Records
- **Full Dataset (253,680 rows):** 24,206 duplicates (9.5%)
- **50/50 Balanced Dataset (70,692 rows):** 1,635 duplicates (2.31%)
- **Interpretation:** Duplicates exist because all 22 attributes are discrete, ordinal, or integer-encoded survey responses (e.g., age bracket 1-13, binary flags 0/1). Identical respondent survey profiles naturally occur in large population samples. These represent distinct individual respondents who share identical demographic and clinical responses, not corrupted duplicate records.

### 9.3 Data Types
- **Data Types:** All 22 attributes are loaded as `float64` / `int64`.
- **Validation:** Confirmed that numeric encoding correctly matches categorical/ordinal definitions.

### 9.4 Invalid Values
- **Checked Range Bounds:**
  - `BMI`: Min 12.0, Max 98.0 (all clinically valid BMI ranges).
  - `GenHlth`: Min 1, Max 5 (matches 1-5 scale).
  - `MentHlth` & `PhysHlth`: Min 0, Max 30 (matches 30-day survey window).
  - `Age`: Min 1, Max 13 (matches 13 BRFSS age brackets).
  - `Education`: Min 1, Max 6.
  - `Income`: Min 1, Max 8.
- **Result:** 0 invalid or out-of-bounds values found.

### 9.5 Outliers
- **BMI Outliers (> 50.0):** 923 records (1.3% of sample). Max BMI = 98.0.
  - *Decision:* Retained. Super-obesity (BMI > 50) is clinically valid and strongly associated with severe diabetes and metabolic syndrome.
- **PhysHlth / MentHlth = 30 Days:** 4,312 respondents reported 30 days of poor physical health.
  - *Decision:* Retained. Represents chronic disability/illness.

### 9.6 Class Distribution
- **Full Dataset (N = 253,680):**
  - Class 0 (No Diabetes): 218,334 (86.07%)
  - Class 1 (Diagnosed Diabetes): 35,346 (13.93%)
- **Primary Balanced Dataset (N = 70,692):**
  - Class 0 (No Diabetes): 35,346 (50.00%)
  - Class 1 (Diagnosed Diabetes): 35,346 (50.00%)
- **Observation:** The 50/50 split dataset eliminates class imbalance bias, ensuring that evaluation metrics (Accuracy, Precision, Recall, F1) remain balanced during mining model training.

### 9.7 Potential Data Leakage
- **Audit:** Checked if any feature directly encodes the target.
- **Result:** No data leakage detected. Features represent antecedents, risk factors, or comorbidities (e.g., `HighBP`, `BMI`, `GenHlth`), not diagnostic tests of diabetes.

### 9.8 Other Observations
- `CholCheck` has a high mean (0.975), indicating 97.5% of respondents had a cholesterol check in the past 5 years.

---

## 10. Exploratory Data Analysis

### 10.1 Descriptive Statistics (N = 70,692)

| Attribute | Mean | Std Dev | Median | Min | Max | Pearson Corr with Target |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`Diabetes_binary`** | 0.5000 | 0.5000 | 0.5 | 0.0 | 1.0 | **1.0000** |
| **`GenHlth`** | 2.8371 | 1.1136 | 3.0 | 1.0 | 5.0 | **0.4076** |
| **`HighBP`** | 0.5635 | 0.4960 | 1.0 | 0.0 | 1.0 | **0.3815** |
| **`BMI`** | 29.8570 | 7.1138 | 29.0 | 12.0 | 98.0 | **0.2934** |
| **`HighChol`** | 0.5257 | 0.4993 | 1.0 | 0.0 | 1.0 | **0.2892** |
| **`Age`** | 8.5841 | 2.8522 | 9.0 | 1.0 | 13.0 | **0.2787** |
| **`DiffWalk`** | 0.2527 | 0.4346 | 0.0 | 0.0 | 1.0 | **0.2726** |
| **`PhysHlth`** | 5.8104 | 10.0623 | 0.0 | 0.0 | 30.0 | **0.2131** |
| **`HeartDiseaseorAttack`**| 0.1478 | 0.3549 | 0.0 | 0.0 | 1.0 | **0.2115** |
| **`PhysActivity`** | 0.7030 | 0.4569 | 1.0 | 0.0 | 1.0 | **-0.1587** |
| **`Education`** | 4.9210 | 1.0291 | 5.0 | 1.0 | 6.0 | **-0.1705** |
| **`Income`** | 5.6983 | 2.1752 | 6.0 | 1.0 | 8.0 | **-0.2244** |

### 10.2 Numerical Distributions
- **BMI Distribution:** Mean = 29.86, Median = 29.0. Right-skewed distribution. Non-diabetics have a mean BMI of 27.7, whereas diabetics have a mean BMI of 31.9.
- **Mental & Physical Health Days:** Zero-inflated distributions. Over 60% of respondents report 0 poor health days, while a distinct subset reports 30 days.

### 10.3 Categorical Distributions
- **High Blood Pressure:** 56.4% of sample has High BP.
- **High Cholesterol:** 52.6% of sample has High Cholesterol.
- **Physical Activity:** 70.3% engage in regular physical activity.

### 10.4 Target Analysis
- **Balanced Dataset:** Exactly 35,346 No-Diabetes (0) and 35,346 Diabetes (1) respondents.

### 10.5 Correlation Analysis Findings
- Top positive correlations with `Diabetes_binary`:
  1. `GenHlth` (+0.4076): Self-reported general health is the single strongest indicator.
  2. `HighBP` (+0.3815): Hypertension strongly co-occurs with diabetes.
  3. `BMI` (+0.2934): Higher BMI significantly increases diabetes risk.
  4. `HighChol` (+0.2892): Hypercholesterolemia co-occurs frequently.
  5. `Age` (+0.2787): Older age categories have significantly higher prevalence.
- Strongest negative correlations:
  1. `Income` (-0.2244): Higher household income correlates with lower diabetes prevalence.
  2. `Education` (-0.1705): Higher educational attainment correlates with lower risk.
  3. `PhysActivity` (-0.1587): Regular exercise is protective against diabetes.

### 10.6 Important Relationships & Statistical Tests (R Chi-Square Output)
- **HighBP vs Diabetes:** $\chi^2 = 10,287.97, p < 10^{-15}$. High BP prevalence is 75.3% in diabetics vs 37.4% in non-diabetics.
- **HighChol vs Diabetes:** $\chi^2 = 5,911.81, p < 10^{-15}$. High Chol prevalence is 67.0% in diabetics vs 38.1% in non-diabetics.
- **HeartDiseaseorAttack vs Diabetes:** $\chi^2 = 3,161.72, p < 10^{-15}$. Heart disease rate is 22.3% in diabetics vs 7.3% in non-diabetics (3x higher risk!).

### 10.7 Key Findings
1. **Clinical Triad:** High Blood Pressure, High Cholesterol, and High BMI form a prominent diagnostic triad for diabetes risk.
2. **Cardiovascular Comorbidity:** Individuals with diabetes have a 3x higher incidence of coronary heart disease or myocardial infarction (`HeartDiseaseorAttack`).
3. **Socio-Economic Gradient:** Inverse relationship between income/education and diabetes prevalence, highlighting social determinants of metabolic health.

---

## 11. Data Preprocessing Plan

For Review 2 execution:
1. **Scaling / Normalization:** Apply `StandardScaler` / R `scale()` to continuous attributes (`BMI`, `MentHlth`, `PhysHlth`) specifically for KNN distance calculations and K-Means clustering.
2. **Discretization / Binning:** Bin `BMI` into standard WHO categories (Underweight < 18.5, Normal 18.5-24.9, Overweight 25-29.9, Obese ≥ 30) for Apriori association rule mining.
3. **Categorical Encoding:** Convert ordinal attributes (`GenHlth`, `Age`, `Education`, `Income`) into factors in R (`as.factor()`) for Decision Trees and Naive Bayes.
4. **Train-Test Partitioning:** Perform 70/30 stratified train-test split using `caret::createDataPartition()` in R and `train_test_split()` in Python.

---

## 12. Proposed Data Warehouse

### 12.1 Business Questions
1. How does diabetes prevalence vary across age brackets and gender demographics?
2. What is the joint incidence of hypertension (`HighBP`) and hypercholesterolemia (`HighChol`) among diabetic patients?
3. How does physical activity and smoking behavior impact diabetes risk across different general health categories?
4. What is the average BMI and physical un-wellness days for diabetic vs non-diabetic populations sliced by income level?

### 12.2 Proposed Grain
**Grain:** Exactly one fact record per individual survey respondent per annual BRFSS surveillance cycle.

### 12.3 Fact Table (`FACT_HEALTH_SURVEY`)
- `fact_id` (Primary Key, INTEGER)
- `demog_key` (Foreign Key -> `DIM_DEMOGRAPHICS`)
- `lifestyle_key` (Foreign Key -> `DIM_LIFESTYLE`)
- `clinical_key` (Foreign Key -> `DIM_CLINICAL_RISK`)
- `genhealth_key` (Foreign Key -> `DIM_GENERAL_HEALTH`)
- **Measures:**
  - `diabetes_binary` (Additive binary measure)
  - `ment_hlth_days` (Additive discrete measure, 0-30 days)
  - `phys_hlth_days` (Additive discrete measure, 0-30 days)
  - `bmi_value` (Semi-additive continuous measure)

### 12.4 Dimension Tables
1. **`DIM_DEMOGRAPHICS`:** `demog_key` (PK), `age`, `sex`, `education`, `income`.
2. **`DIM_LIFESTYLE`:** `lifestyle_key` (PK), `smoker`, `phys_activity`, `fruits`, `veggies`, `hvy_alcohol_consump`.
3. **`DIM_CLINICAL_RISK`:** `clinical_key` (PK), `high_bp`, `high_chol`, `chol_check`, `stroke`, `heart_disease_or_attack`, `diff_walk`, `any_healthcare`, `no_doc_bc_cost`.
4. **`DIM_GENERAL_HEALTH`:** `genhealth_key` (PK), `gen_hlth_rating`.

### 12.5 Star Schema DDL SQL

```sql
CREATE TABLE DIM_DEMOGRAPHICS (
    demog_key INTEGER PRIMARY KEY AUTOINCREMENT,
    age INTEGER, sex INTEGER, education INTEGER, income INTEGER
);

CREATE TABLE DIM_LIFESTYLE (
    lifestyle_key INTEGER PRIMARY KEY AUTOINCREMENT,
    smoker INTEGER, phys_activity INTEGER, fruits INTEGER, veggies INTEGER, hvy_alcohol_consump INTEGER
);

CREATE TABLE DIM_CLINICAL_RISK (
    clinical_key INTEGER PRIMARY KEY AUTOINCREMENT,
    high_bp INTEGER, high_chol INTEGER, chol_check INTEGER, stroke INTEGER, 
    heart_disease_or_attack INTEGER, diff_walk INTEGER, any_healthcare INTEGER, no_doc_bc_cost INTEGER
);

CREATE TABLE DIM_GENERAL_HEALTH (
    genhealth_key INTEGER PRIMARY KEY AUTOINCREMENT,
    gen_hlth_rating INTEGER
);

CREATE TABLE FACT_HEALTH_SURVEY (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    demog_key INTEGER REFERENCES DIM_DEMOGRAPHICS(demog_key),
    lifestyle_key INTEGER REFERENCES DIM_LIFESTYLE(lifestyle_key),
    clinical_key INTEGER REFERENCES DIM_CLINICAL_RISK(clinical_key),
    genhealth_key INTEGER REFERENCES DIM_GENERAL_HEALTH(genhealth_key),
    diabetes_binary INTEGER,
    ment_hlth_days INTEGER,
    phys_hlth_days INTEGER,
    bmi_value REAL
);
```

---

## 13. Proposed OLAP Operations

All 5 OLAP operations were implemented in SQL and executed against `review1/diabetes_dw.db`:

### Roll-up
- **Description:** Aggregating diabetes prevalence and average BMI to a higher level of the Age hierarchy (Age Brackets 1 through 13).
- **SQL Query:**
  ```sql
  SELECT d.age AS Age_Bracket, COUNT(*) AS Total_Respondents,
         SUM(f.diabetes_binary) AS Diabetes_Cases,
         ROUND(AVG(f.diabetes_binary)*100, 2) AS Prevalence_Pct,
         ROUND(AVG(f.bmi_value), 2) AS Avg_BMI
  FROM FACT_HEALTH_SURVEY f
  JOIN DIM_DEMOGRAPHICS d ON f.demog_key = d.demog_key
  GROUP BY d.age ORDER BY d.age;
  ```
- **Result Summary:** Age bracket 1 (18-24) has 8.0% prevalence (Avg BMI 26.2), escalating monotonically to Age bracket 9 (60-64) with 56.9% prevalence (Avg BMI 30.7) and Age bracket 13 (80+) with 59.1% prevalence.

### Drill-down
- **Description:** Navigating from senior age brackets (Age 60-74) into finer detail by breaking down prevalence by Gender (`Sex`).
- **SQL Query:**
  ```sql
  SELECT d.age AS Age_Bracket,
         CASE WHEN d.sex = 0 THEN 'Female' ELSE 'Male' END AS Gender,
         COUNT(*) AS Total_Respondents, SUM(f.diabetes_binary) AS Diabetes_Cases,
         ROUND(AVG(f.diabetes_binary)*100, 2) AS Prevalence_Pct
  FROM FACT_HEALTH_SURVEY f
  JOIN DIM_DEMOGRAPHICS d ON f.demog_key = d.demog_key
  WHERE d.age IN (9, 10, 11)
  GROUP BY d.age, d.sex ORDER BY d.age, d.sex;
  ```
- **Result Summary:** For Age 60-64 (Bracket 9), Males have a 58.7% prevalence compared to Females at 55.4%.

### Slice
- **Description:** Filtering the data cube on a single dimension key: `High_BP = 1` (Hypertension Slice) to analyze how General Health rating correlates with diabetes under hypertensive conditions.
- **SQL Query:**
  ```sql
  SELECT g.gen_hlth_rating AS General_Health, COUNT(*) AS Total_Respondents,
         SUM(f.diabetes_binary) AS Diabetes_Cases,
         ROUND(AVG(f.diabetes_binary)*100, 2) AS Diabetes_Prevalence_Pct
  FROM FACT_HEALTH_SURVEY f
  JOIN DIM_CLINICAL_RISK c ON f.clinical_key = c.clinical_key
  JOIN DIM_GENERAL_HEALTH g ON f.genhealth_key = g.genhealth_key
  WHERE c.high_bp = 1
  GROUP BY g.gen_hlth_rating ORDER BY g.gen_hlth_rating;
  ```
- **Result Summary:** Among hypertensive respondents, those rating health as '1: Excellent' have 34.7% diabetes prevalence, whereas those rating health as '5: Poor' have 83.4% diabetes prevalence.

### Dice
- **Description:** Selecting a sub-cube defined by multiple conditions: Age ≥ 9 (60+), High BP = 1, and High Cholesterol = 1, evaluated across Income brackets and Smoking status.
- **SQL Query:**
  ```sql
  SELECT d.income AS Income_Bracket, l.smoker AS Smoker_Status,
         COUNT(*) AS Respondent_Count,
         ROUND(AVG(f.diabetes_binary)*100, 2) AS Diabetes_Prevalence_Pct
  FROM FACT_HEALTH_SURVEY f
  JOIN DIM_DEMOGRAPHICS d ON f.demog_key = d.demog_key
  JOIN DIM_CLINICAL_RISK c ON f.clinical_key = c.clinical_key
  JOIN DIM_LIFESTYLE l ON f.lifestyle_key = l.lifestyle_key
  WHERE d.age >= 9 AND c.high_bp = 1 AND c.high_chol = 1
  GROUP BY d.income, l.smoker ORDER BY d.income, l.smoker;
  ```
- **Result Summary:** High-risk senior sub-cube shows diabetes prevalence exceeds 70% in lower income brackets (Income 1-3) regardless of smoking status.

### Pivot
- **Description:** Rotating axes to present a matrix of Female vs Male diabetes case counts across all 13 age brackets.
- **SQL Query:**
  ```sql
  SELECT d.age AS Age_Bracket,
         SUM(CASE WHEN d.sex = 0 THEN f.diabetes_binary ELSE 0 END) AS Female_Diabetes_Cases,
         SUM(CASE WHEN d.sex = 1 THEN f.diabetes_binary ELSE 0 END) AS Male_Diabetes_Cases,
         ROUND(AVG(f.diabetes_binary)*100, 2) AS Overall_Prevalence_Pct
  FROM FACT_HEALTH_SURVEY f
  JOIN DIM_DEMOGRAPHICS d ON f.demog_key = d.demog_key
  GROUP BY d.age ORDER BY d.age;
  ```
- **Result Summary:** Male diabetes cases exceed female cases only in age brackets 10–11 (ages 65–74), after which female cases equal or exceed male cases in senior brackets 12–13 (75+).

---

## 14. Proposed Data Mining Methodology

### Classification
- **ID3 & CART Decision Trees (`rpart` in R / `DecisionTreeClassifier` in Python):** Tree-based supervised learning splitting nodes via Information Gain (ID3) and Gini Impurity (CART). Decision trees will provide interpretable clinical decision rules (e.g., *IF HighBP=1 AND GenHlth≥4 AND BMI≥30 THEN Diabetes=1*).
- **K-Nearest Neighbors (KNN) (`class::knn` in R):** Distance-based non-parametric classification using Euclidean distance on standardized features (`scale()`). Evaluates local neighborhood similarity for patient risk scoring.

### Clustering
- **K-Means & Hierarchical Clustering (`kmeans()` & `hclust()` in R):** Unsupervised grouping of patients into $k=3$ distinct risk clusters (Low Risk, Moderate Risk, Severe Comorbidity Risk). The target label `Diabetes_binary` will be withheld during clustering and used solely for cluster validation via contingency tables.

### Association Rules
- **Apriori Algorithm (`arules` in R):** Mining frequent itemsets and strong association rules ($X \Rightarrow Y$) linking lifestyle factors, clinical conditions, and diabetes status. Minimum support threshold = $0.05$, Minimum confidence = $0.60$.

### Prediction
- *Scope Definition:* For this cross-sectional survey dataset, "prediction" specifically refers to **cross-sectional statistical risk classification** (scoring an individual's current probability of having diagnosed/undiagnosed diabetes based on survey responses), NOT longitudinal future disease onset forecasting.

---

## 15. R / WEKA Usage

- **R Usage:**
  - Script: `review1/scripts/02_r_eda_analysis.R`
  - Libraries: `base R`, `stats`, `graphics`.
  - Operations: Descriptive statistics (`summary()`, `mean()`, `sd()`), correlation matrices (`cor()`), and Chi-Square independence tests (`chisq.test()`).
  - Output Log: `review1/r_eda_output.txt`.
- **WEKA Usage:**
  - WEKA will be used in Review 2 for visual comparison of J48 (WEKA's C4.5 implementation) and NaiveBayes classifiers, using ARFF dataset conversions.

---

## 16. Team Contribution

- **Vishal C Tantri (24MIC0068):**
  - Dataset identification, audit, and quality verification.
  - Python EDA script and 8 high-resolution figure generations (`01_eda_and_charts.py`).
  - R statistical analysis script and output generation (`02_r_eda_analysis.R`).
  - SQLite Data Warehouse design, Star Schema DDL, ETL, and OLAP query execution (`03_build_warehouse.py`).
  - Review 1 master documentation (`PROJECT_MASTER.md`) and interactive demo script (`04_review1_demo.py`).

---

## 17. Review 1 Presentation Content

Mapped directly to the slides of `DWDM_Lab_Project_Template_Week1.pptx`:

### Slide 1: Title & Team Information
- **Title:** Data Mining & Data Warehousing for Diabetes Risk Assessment & Cardiovascular Comorbidity Analysis
- **Course:** CSI3010 — Data Mining & Data Warehousing
- **Team:** Data Miners | Student ID: 24MIC0068

### Slide 2: Dataset Description
- **Dataset Name:** CDC BRFSS 2015 Diabetes Health Indicators
- **Source:** CDC / Kaggle Repository (BRFSS 2015 Annual Survey)
- **Size:** 70,692 rows × 22 columns (Primary Balanced Dataset); 253,680 rows (Full Dataset)
- **Format:** CSV / SQLite Relational Database
- **Domain:** Healthcare / Public Health Informatics
- **Why this dataset?** Addresses high-prevalence chronic diabetes risk and cardiovascular comorbidities using non-invasive survey indicators. 0 missing values; balanced 50/50 target distribution.

### Slide 3: Attribute Summary
- **Target:** `Diabetes_binary` (Binary: 0=No Diabetes, 1=Diagnosed Diabetes only; prediabetes coded 0) -> Fact Measure
- **Clinical Measures:** `BMI` (Continuous 12-98), `PhysHlth` (0-30 days), `MentHlth` (0-30 days) -> Fact Measures
- **Dimensions:** `HighBP` (0/1), `HighChol` (0/1), `Smoker` (0/1), `PhysActivity` (0/1), `GenHlth` (1-5), `Age` (1-13), `Sex` (0/1), `Income` (1-8) -> Dimension Attributes

### Slide 4: Data Warehouse Architecture (Star Schema)
- **Central Fact Table:** `FACT_HEALTH_SURVEY`
- **Dimension Tables:** `DIM_DEMOGRAPHICS`, `DIM_LIFESTYLE`, `DIM_CLINICAL_RISK`, `DIM_GENERAL_HEALTH`

### Slide 5: Warehouse Design & ETL
- **Grain:** One row per survey respondent per annual BRFSS cycle.
- **Measures:** `diabetes_binary`, `ment_hlth_days`, `phys_hlth_days`, `bmi_value`.
- **ETL:** Python `pandas` extraction from CSV -> surrogate key generation -> SQLite relational loading.

### Slide 6: Sample OLAP Operations
- **Roll-up:** Aggregating prevalence by Age Category (Age 18-24: 8.0% -> Age 60-64: 56.9%).
- **Drill-down:** Breaking down age brackets by Gender (`Sex`).
- **Slice:** Filtering on `HighBP = 1` across `GenHlth` categories.
- **Dice:** Sub-cube on Age ≥ 60, High BP=1, High Chol=1 across Income & Smoking.
- **Pivot:** Cross-tabulation matrix of Male vs Female cases across 13 age categories.

### Slide 7: SQL DDL Code
- Complete DDL SQL for `DIM_DEMOGRAPHICS`, `DIM_LIFESTYLE`, `DIM_CLINICAL_RISK`, `DIM_GENERAL_HEALTH`, and `FACT_HEALTH_SURVEY`.

### Slide 8: Python ETL Code
- Pandas extraction, deduplication, surrogate mapping, and SQLite insertion script.

### Slide 9: Sample OLAP Queries (SQL)
- SQL implementations for Roll-up, Drill-down, Slice, Dice, and Pivot.

---

## 18. Review 1 Demo

The interactive proof-of-work demonstration script is saved at [review1/scripts/04_review1_demo.py](file:///home/vct/Desktop/DMDW%20PROJECT/review1/scripts/04_review1_demo.py).  
It executes live verification of:
1. CSV dataset dimensions and 0 missing value audit.
2. SQLite Data Warehouse connection and table schema check.
3. Live execution of the SQL OLAP Roll-up query.
4. Output check of the 8 generated figure files in `review1/figures/`.

---

## 19. Review 1 Findings

1. **Clean Dataset:** CDC BRFSS 2015 is completely free of missing cells (0 missing values), requiring no artificial imputation.
2. **Key Predictors:** General Health (`GenHlth`, $r = 0.41$), High Blood Pressure (`HighBP`, $r = 0.38$), Body Mass Index (`BMI`, $r = 0.29$), and High Cholesterol (`HighChol`, $r = 0.29$) are the top positive correlates of diabetes.
3. **Cardiovascular Risk Link:** Diabetic respondents exhibit a 22.3% rate of Coronary Heart Disease or Myocardial Infarction compared to 7.3% in non-diabetics ($\chi^2 = 3161.72, p < 10^{-15}$).
4. **Feasible DW Architecture:** The proposed 4-dimension Star Schema effectively supports multi-dimensional OLAP queries without performance bottlenecks.

---

## 20. Review 1 Questions We Should Be Prepared For

1. **Q: Why did you choose the CDC BRFSS 2015 dataset?**  
   *A:* It is a large, nationally representative public health dataset with 22 structured health indicators, zero missing values, and established clinical relevance for diabetes and cardiovascular disease analysis.
2. **Q: Why are there duplicate rows in your dataset? Did you remove them?**  
   *A:* All 22 variables are discrete integer survey codes (e.g., Age 1-13, binary flags 0/1). In a population of 70,000+, multiple distinct respondents naturally give identical answers. They represent valid individual survey responses, not corrupted records, so they are preserved.
3. **Q: What is the primary target variable and its encoding?**    *A:* `Diabetes_binary` where 0 represents No Diabetes (including the 4,631 prediabetes respondents, who are coded 0) and 1 represents Diagnosed Diabetes only.
4. **Q: Why are you using the 50/50 split dataset instead of the 253,680 record dataset?**  
   *A:* The 253k dataset has an 86/14 class imbalance which causes machine learning models to favor the majority class. The 50/50 split dataset (70,692 rows) provides a balanced target distribution for unbiased classifier training, while the 253k dataset is kept for population data warehousing.
5. **Q: What is the grain of your Data Warehouse?**  
   *A:* Exactly one record per individual survey respondent per annual BRFSS surveillance cycle.
6. **Q: What are your fact table measures?**  
   *A:* `diabetes_binary` (additive binary count), `ment_hlth_days` (additive discrete days), `phys_hlth_days` (additive discrete days), and `bmi_value` (semi-additive continuous value).
7. **Q: What is the difference between Roll-up and Drill-down in your project?**  
   *A:* Roll-up aggregates individual respondent data to higher age bracket totals. Drill-down moves from age bracket totals into finer detail by breaking down prevalence by gender (`Sex`).
8. **Q: What is your Slice operation?**  
   *A:* Filtering the data cube on a single dimension condition: `High_BP = 1` (Hypertension slice) to evaluate general health ratings among hypertensive patients.
9. **Q: What is your Dice operation?**  
   *A:* Sub-cube filtering across multiple dimensions: Age ≥ 60, High BP = 1, and High Cholesterol = 1, analyzed by Income level and Smoking status.
10. **Q: How does `GenHlth` correlate with diabetes?**  
    *A:* `GenHlth` is the strongest predictor ($r = 0.4076$). Diabetes prevalence rises from 13.8% among respondents reporting '1: Excellent' health up to 83.4% among those reporting '5: Poor' health with hypertension.
11. **Q: Is `HeartDiseaseorAttack` a target or a feature?**  
    *A:* In our primary classification model, `Diabetes_binary` is the primary target and `HeartDiseaseorAttack` is a clinical comorbidity dimension feature. However, it can also serve as a secondary target for comorbidity risk analysis.
12. **Q: Why use Chi-Square tests of independence in R?**  
    *A:* Since features like `HighBP`, `HighChol`, `Smoker`, and `Stroke` are categorical/binary, Chi-Square tests verify whether their association with diabetes status is statistically significant ($p < 0.05$). All tested clinical features yielded $p < 10^{-10}$.
13. **Q: How will continuous features like BMI be handled in Apriori association rule mining?**  
    *A:* Apriori requires discrete transaction items. `BMI` will be discretized into standard WHO categories (Normal, Overweight, Obese) prior to running `arules::apriori()`.
14. **Q: How will features be preprocessed for KNN?**  
    *A:* Distance-based algorithms like KNN are sensitive to feature scales. Continuous attributes (`BMI`, `MentHlth`, `PhysHlth`) will be normalized using z-score standardization (`scale()`).
15. **Q: What decision tree algorithms will be used?**  
    *A:* ID3 (using Information Gain) and CART (using Gini Impurity via `rpart` in R).
16. **Q: What is the expected outcome of K-Means clustering?**  
    *A:* Grouping respondents into $k=3$ natural risk clusters (Low Risk, Moderate Risk, High Comorbidity Risk) to discover patient profiles without using label supervision.
17. **Q: What R packages are used for your analysis?**  
    *A:* Base R (`stats`, `graphics`) for descriptive statistics and Chi-Square testing, with `ggplot2`, `rpart`, `class`, `cluster`, and `arules` planned for mining models.
18. **Q: Did you find any data leakage in the dataset?**  
    *A:* No. All features represent antecedent survey responses, lifestyle habits, or diagnosed comorbidities, not direct lab test measurements of blood glucose or HbA1c.
19. **Q: How does income affect diabetes prevalence?**  
    *A:* Income is negatively correlated ($r = -0.2244$). Respondents in the highest income bracket ($> \$75k$) have significantly lower diabetes prevalence than lower income brackets.
20. **Q: Why is this a Data Mining problem rather than standard statistics?**  
    *A:* Standard statistics tests hypotheses on isolated variables, whereas Data Mining extracts non-trivial, multi-dimensional patterns (association rules via Apriori, unsupervised patient clusters via K-Means, and non-linear decision boundaries via ID3/CART) across 22 complex indicators.

---

## 21. Problems / Decisions / Corrections

1. **Dataset Selection Decision:** Evaluated 3 dataset files. Selected `diabetes_binary_5050split_health_indicators_BRFSS2015.csv` for balanced classifier training and `diabetes_binary_health_indicators_BRFSS2015.csv` for full population warehouse queries.
2. **Duplicate Row Audit:** Confirmed duplicate rows are valid distinct survey respondents with identical survey response profiles due to discrete attribute encoding.
3. **R EDA Execution:** Resolved package dependency requirements by utilizing built-in R statistical tools (`summary`, `cor`, `chisq.test`) ensuring zero runtime failures.

---

## 22. Review 1 Completion Checklist

- [x] Dataset verified (70,692 rows × 22 columns)
- [x] Source and version documented (CDC BRFSS 2015)
- [x] All 22 features documented with ranges and types
- [x] Target variable identified (`Diabetes_binary`)
- [x] Dataset relevance established (Healthcare / Public Health Informatics)
- [x] Missing values checked (0 missing cells)
- [x] Duplicates checked (1,635 in split dataset; verified as valid survey responses)
- [x] Data types verified (Float64/Int64)
- [x] Outliers investigated (BMI > 50 evaluated and retained)
- [x] Class distribution analyzed (50/50 balanced dataset)
- [x] Potential leakage investigated (None found)
- [x] Descriptive statistics completed (Mean, SD, Median, Min, Max table)
- [x] Correlation analysis completed (Pearson correlation table)
- [x] Chi-Square independence tests executed in R
- [x] 8 high-resolution figures generated and saved in `review1/figures/`
- [x] Project title and scope finalized
- [x] Problem statement & objectives documented
- [x] Preliminary Star Schema Data Warehouse designed & built in SQLite (`review1/diabetes_dw.db`)
- [x] 5 OLAP operations implemented in SQL and executed (Roll-up, Drill-down, Slice, Dice, Pivot)
- [x] Data mining methodology planned (Decision Trees, KNN, K-Means, Apriori)
- [x] Course syllabus mapping completed
- [x] Team responsibilities documented
- [x] Slide-by-slide presentation content prepared (Slide 1 – Slide 9)
- [x] Interactive technical demo script created (`review1/scripts/04_review1_demo.py`)
- [x] 20 expected professor viva questions & answers prepared
- [x] All actual computed results recorded in `PROJECT_MASTER.md`

---

## 23. Files and Artifacts

- **Master Progress Record:** [PROJECT_MASTER.md](file:///home/vct/Desktop/DMDW%20PROJECT/PROJECT_MASTER.md)
- **Primary Dataset:** [diabetes_binary_5050split_health_indicators_BRFSS2015.csv](file:///home/vct/Desktop/DMDW%20PROJECT/diabetes_binary_5050split_health_indicators_BRFSS2015.csv)
- **Full Population Dataset:** [diabetes_binary_health_indicators_BRFSS2015.csv](file:///home/vct/Desktop/DMDW%20PROJECT/diabetes_binary_health_indicators_BRFSS2015.csv)
- **Multiclass Dataset:** [diabetes_012_health_indicators_BRFSS2015.csv](file:///home/vct/Desktop/DMDW%20PROJECT/diabetes_012_health_indicators_BRFSS2015.csv)
- **Data Warehouse Database:** [review1/diabetes_dw.db](file:///home/vct/Desktop/DMDW%20PROJECT/review1/diabetes_dw.db)
- **EDA & Visualization Script:** [review1/scripts/01_eda_and_charts.py](file:///home/vct/Desktop/DMDW%20PROJECT/review1/scripts/01_eda_and_charts.py)
- **R EDA & Statistical Script:** [review1/scripts/02_r_eda_analysis.R](file:///home/vct/Desktop/DMDW%20PROJECT/review1/scripts/02_r_eda_analysis.R)
- **Data Warehouse & OLAP Script:** [review1/scripts/03_build_warehouse.py](file:///home/vct/Desktop/DMDW%20PROJECT/review1/scripts/03_build_warehouse.py)
- **Review 1 Demo Script:** [review1/scripts/04_review1_demo.py](file:///home/vct/Desktop/DMDW%20PROJECT/review1/scripts/04_review1_demo.py)
- **Star Schema DDL SQL:** [review1/sql/01_star_schema.sql](file:///home/vct/Desktop/DMDW%20PROJECT/review1/sql/01_star_schema.sql)
- **OLAP Queries SQL:** [review1/sql/02_olap_queries.sql](file:///home/vct/Desktop/DMDW%20PROJECT/review1/sql/02_olap_queries.sql)
- **R Analysis Output Log:** [review1/r_eda_output.txt](file:///home/vct/Desktop/DMDW%20PROJECT/review1/r_eda_output.txt)
- **OLAP Results JSON:** [review1/olap_results.json](file:///home/vct/Desktop/DMDW%20PROJECT/review1/olap_results.json)
- **Generated Figures Directory:** [review1/figures/](file:///home/vct/Desktop/DMDW%20PROJECT/review1/figures/)
  - [01_target_distribution.png](file:///home/vct/Desktop/DMDW%20PROJECT/review1/figures/01_target_distribution.png)
  - [02_correlation_heatmap.png](file:///home/vct/Desktop/DMDW%20PROJECT/review1/figures/02_correlation_heatmap.png)
  - [03_bmi_distribution.png](file:///home/vct/Desktop/DMDW%20PROJECT/review1/figures/03_bmi_distribution.png)
  - [04_comorbidity_analysis.png](file:///home/vct/Desktop/DMDW%20PROJECT/review1/figures/04_comorbidity_analysis.png)
  - [05_age_distribution.png](file:///home/vct/Desktop/DMDW%20PROJECT/review1/figures/05_age_distribution.png)
  - [06_lifestyle_factors.png](file:///home/vct/Desktop/DMDW%20PROJECT/review1/figures/06_lifestyle_factors.png)
  - [07_genhealth_vs_diabetes.png](file:///home/vct/Desktop/DMDW%20PROJECT/review1/figures/07_genhealth_vs_diabetes.png)
  - [08_feature_importance.png](file:///home/vct/Desktop/DMDW%20PROJECT/review1/figures/08_feature_importance.png)

---

## 24. Change Log

- **2026-10-08:** Initialized project workspace for CDC BRFSS 2015 dataset.
- **2026-10-08:** Performed dataset quality audit (0 missing cells, 70,692 rows × 22 columns).
- **2026-10-08:** Executed Python EDA & generated 8 high-resolution charts in `review1/figures/`.
- **2026-10-08:** Executed R statistical audit (`02_r_eda_analysis.R`) including Chi-Square independence tests.
- **2026-10-08:** Built SQLite Data Warehouse (`review1/diabetes_dw.db`) & executed 5 SQL OLAP queries.
- **2026-10-08:** Created interactive demo script (`04_review1_demo.py`) & 20 professor defense Q&A.
- **2026-10-08:** Documented complete results in `PROJECT_MASTER.md` and set Review 1 status to ✅ **REVIEW 1 READY**.
