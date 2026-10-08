
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
