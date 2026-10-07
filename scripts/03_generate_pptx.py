#!/usr/bin/env python3
"""
=============================================================================
 DMDW PROJECT — Review 1: PPTX Presentation Generator
 Team: Data Miners | Member: 24MIC0068
 
 Generates a professional, fully-formatted PowerPoint presentation (.pptx)
 matching the professor's template structure for Review 1.
=============================================================================
"""

import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    DARK_NAVY = RGBColor(15, 23, 42)
    BLUE_ACCENT = RGBColor(37, 99, 235)
    TEXT_DARK = RGBColor(30, 41, 59)
    TEXT_LIGHT = RGBColor(241, 245, 249)
    BG_LIGHT = RGBColor(248, 250, 252)
    CARD_BG = RGBColor(255, 255, 255)
    BORDER_COLOR = RGBColor(226, 232, 240)
    GREEN_ACCENT = RGBColor(16, 185, 129)
    RED_ACCENT = RGBColor(239, 68, 68)

    def add_header(slide, title_text, slide_num):
        # Header banner shape
        header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        header.fill.solid()
        header.fill.fore_color.rgb = DARK_NAVY
        header.line.fill.background()

        # Title text
        txBox = slide.shapes.add_textbox(Inches(0.6), Inches(0.15), Inches(10), Inches(0.8))
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Arial"
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)

        # Subheader / Course badge
        p2 = tf.add_paragraph()
        p2.text = "Data Mining & Data Warehousing (CSI3010) | Team: Data Miners (24MIC0068)"
        p2.font.name = "Arial"
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(148, 163, 184)

        # Slide Number Badge
        num_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(12.2), Inches(0.25), Inches(0.6), Inches(0.6))
        num_box.fill.solid()
        num_box.fill.fore_color.rgb = BLUE_ACCENT
        num_box.line.fill.background()
        tf_num = num_box.text_frame
        p_num = tf_num.paragraphs[0]
        p_num.text = str(slide_num)
        p_num.alignment = PP_ALIGN.CENTER
        p_num.font.name = "Arial"
        p_num.font.size = Pt(18)
        p_num.font.bold = True
        p_num.font.color.rgb = RGBColor(255, 255, 255)

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_LIGHT
        bg.line.fill.background()
        return bg

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1)

    # Hero card
    hero = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(4.2))
    hero.fill.solid()
    hero.fill.fore_color.rgb = DARK_NAVY
    hero.line.fill.background()

    txBox = slide1.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(2.5))
    tf = txBox.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "DIABETES RISK PREDICTION & HEALTHCARE DATA WAREHOUSING"
    p.font.name = "Arial"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    p_sub = tf.add_paragraph()
    p_sub.text = "Review 1 Presentation — Dataset Exploratory Data Analysis, Star Schema DW & OLAP Architecture"
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = RGBColor(148, 163, 184)
    p_sub.space_before = Pt(10)

    # Info card grid
    card1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(4.6), Inches(3.6), Inches(2.3))
    card1.fill.solid()
    card1.fill.fore_color.rgb = CARD_BG
    card1.line.color.rgb = BORDER_COLOR
    tf1 = card1.text_frame
    tf1.word_wrap = True
    tf1.paragraphs[0].text = "👥 TEAM DETAILS"
    tf1.paragraphs[0].font.bold = True
    tf1.paragraphs[0].font.size = Pt(14)
    tf1.paragraphs[0].font.color.rgb = BLUE_ACCENT
    p = tf1.add_paragraph()
    p.text = "Team Name: Data Miners\nMember: 24MIC0068\nCourse: CSI3010 DMDW"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

    card2 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.866), Inches(4.6), Inches(3.6), Inches(2.3))
    card2.fill.solid()
    card2.fill.fore_color.rgb = CARD_BG
    card2.line.color.rgb = BORDER_COLOR
    tf2 = card2.text_frame
    tf2.word_wrap = True
    tf2.paragraphs[0].text = "📊 DATASET SUMMARY"
    tf2.paragraphs[0].font.bold = True
    tf2.paragraphs[0].font.size = Pt(14)
    tf2.paragraphs[0].font.color.rgb = BLUE_ACCENT
    p = tf2.add_paragraph()
    p.text = "Dataset: Diabetes Prediction (Kaggle)\nSize: 100,000 → 96,146 clean rows\nTarget: diabetes (0/1)"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

    card3 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.733), Inches(4.6), Inches(3.6), Inches(2.3))
    card3.fill.solid()
    card3.fill.fore_color.rgb = CARD_BG
    card3.line.color.rgb = BORDER_COLOR
    tf3 = card3.text_frame
    tf3.word_wrap = True
    tf3.paragraphs[0].text = "⚙️ REVIEW 1 SCOPE"
    tf3.paragraphs[0].font.bold = True
    tf3.paragraphs[0].font.size = Pt(14)
    tf3.paragraphs[0].font.color.rgb = BLUE_ACCENT
    p = tf3.add_paragraph()
    p.text = "✅ 8 Visual EDA Charts\n✅ SQLite Star Schema DW\n✅ 5 OLAP Operations Executed"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 2: Dataset Description
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2)
    add_header(slide2, "Dataset Description & Problem Overview", 2)

    # Left Column: Problem & Scope
    left_card = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.4), Inches(5.8), Inches(5.6))
    left_card.fill.solid()
    left_card.fill.fore_color.rgb = CARD_BG
    left_card.line.color.rgb = BORDER_COLOR
    tf_l = left_card.text_frame
    tf_l.word_wrap = True
    
    p = tf_l.paragraphs[0]
    p.text = "🎯 Why This Dataset & Business Problem?"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = BLUE_ACCENT

    bullets = [
        ("Kaggle Dataset:", " Diabetes Prediction Dataset (100,000 healthcare screening patient records)."),
        ("Healthcare Problem:", " Early identification of high-risk diabetic individuals using non-invasive clinical & lifestyle indicators."),
        ("Key Analytical Questions:", " What threshold levels of HbA1c and Blood Glucose maximize risk? How do hypertension & heart disease act as comorbidities?"),
        ("Data Quality Audit:", " 3,854 exact duplicates removed (3.85%). 0 explicit NaNs. 32,887 records (34.2%) with 'No Info' in smoking history retained as explicit category."),
        ("Class Imbalance:", " Imbalance ratio of 10.3:1 (87,664 Non-Diabetic vs 8,482 Diabetic). Imbalance techniques (SMOTE/Class Weights) planned for modeling phase.")
    ]
    for b_title, b_text in bullets:
        p = tf_l.add_paragraph()
        p.space_before = Pt(8)
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(11)
        run1.font.color.rgb = TEXT_DARK
        run2 = p.add_run()
        run2.text = b_text
        run2.font.size = Pt(11)
        run2.font.color.rgb = TEXT_DARK

    # Right Column: Visualizations
    img1_path = "/home/vct/Desktop/DMDW PROJECT/images/01_target_distribution.png"
    img2_path = "/home/vct/Desktop/DMDW PROJECT/images/02_correlation_heatmap.png"
    if os.path.exists(img1_path):
        slide2.shapes.add_picture(img1_path, Inches(6.7), Inches(1.4), Inches(6.0), Inches(2.7))
    if os.path.exists(img2_path):
        slide2.shapes.add_picture(img2_path, Inches(6.7), Inches(4.3), Inches(6.0), Inches(2.7))

    # =========================================================================
    # SLIDE 3: Attribute Summary
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3)
    add_header(slide3, "Attribute Summary — Key, Dimension & Measure Mapping", 3)

    rows, cols = 10, 5
    table_shape = slide3.shapes.add_table(rows, cols, Inches(0.6), Inches(1.3), Inches(12.133), Inches(5.8))
    table = table_shape.table
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(1.4)
    table.columns[2].width = Inches(1.8)
    table.columns[3].width = Inches(4.533)
    table.columns[4].width = Inches(2.2)

    headers = ["Attribute Name", "Data Type", "DW Category", "Description & Clinical Mapping", "Sample Stats / Value"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_NAVY
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.font.size = Pt(11)

    attr_data = [
        ("gender", "Categorical", "Dimension Attribute", "Patient gender (Female: 58.6%, Male: 41.4%)", "Female / Male"),
        ("age", "Numeric (Float)", "Dimension / Measure", "Patient age in years (Range: 0.08 to 80.0)", "Mean: 41.8 yrs"),
        ("hypertension", "Binary (0/1)", "Dimension Attribute", "History of high blood pressure (0: 92.5%, 1: 7.5%)", "0 / 1"),
        ("heart_disease", "Binary (0/1)", "Dimension Attribute", "History of heart condition (0: 96.1%, 1: 3.9%)", "0 / 1"),
        ("smoking_history", "Categorical", "Dimension Attribute", "Smoking status (never, No Info, current, former, etc.)", "never (36.4%)"),
        ("bmi", "Numeric (Float)", "Additive Measure", "Body Mass Index kg/m² (Range: 10.0 to 95.7)", "Mean: 27.3 kg/m²"),
        ("HbA1c_level", "Numeric (Float)", "Additive Measure", "Glycated hemoglobin percentage (Range: 3.5 to 9.0%)", "Mean: 5.53%"),
        ("blood_glucose_level", "Numeric (Int)", "Additive Measure", "Fasting blood glucose mg/dL (Range: 80 to 300)", "Mean: 138.1 mg/dL"),
        ("diabetes", "Binary (0/1)", "Target Fact Measure", "Diabetic diagnosis (0: Non-Diabetic, 1: Diabetic)", "8,482 Positive (8.8%)")
    ]

    for row_idx, data in enumerate(attr_data, start=1):
        for col_idx, text in enumerate(data):
            cell = table.cell(row_idx, col_idx)
            cell.text = text
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if row_idx % 2 == 0 else RGBColor(241, 245, 249)
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = TEXT_DARK
                if col_idx == 0:
                    p.font.bold = True

    # =========================================================================
    # SLIDE 4: Data Warehouse Star Schema Diagram
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4)
    add_header(slide4, "Data Warehouse Architecture — Star Schema Design", 4)

    # Central Fact Box
    fact_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.666), Inches(3.2), Inches(4.0), Inches(3.8))
    fact_box.fill.solid()
    fact_box.fill.fore_color.rgb = DARK_NAVY
    fact_box.line.color.rgb = BLUE_ACCENT
    fact_box.line.width = Pt(2)
    tf_f = fact_box.text_frame
    tf_f.word_wrap = True
    p = tf_f.paragraphs[0]
    p.text = "FACT_PATIENT_SCREENING\n(96,146 Rows)"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    fact_lines = [
        "------------------------------------",
        "🔑 screening_id (PK)",
        "🔑 demographic_key (FK)",
        "🔑 clinical_risk_key (FK)",
        "🔑 metric_range_key (FK)",
        "------------------------------------",
        "📊 bmi (Additive Measure)",
        "📊 HbA1c_level (Additive Measure)",
        "📊 blood_glucose_level (Additive Measure)",
        "📌 is_diabetic (0/1 Fact Target)",
        "📌 is_hypertensive (0/1)",
        "📌 has_heart_disease (0/1)"
    ]
    for line in fact_lines:
        p = tf_f.add_paragraph()
        p.text = line
        p.font.size = Pt(9.5)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.alignment = PP_ALIGN.LEFT

    # Left Top Dim Box: DEMOGRAPHICS
    dim1 = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.5), Inches(3.6), Inches(2.2))
    dim1.fill.solid()
    dim1.fill.fore_color.rgb = CARD_BG
    dim1.line.color.rgb = BLUE_ACCENT
    dim1.line.width = Pt(1.5)
    tf_d1 = dim1.text_frame
    tf_d1.paragraphs[0].text = "DIM_DEMOGRAPHICS (14 Rows)"
    tf_d1.paragraphs[0].font.bold = True
    tf_d1.paragraphs[0].font.size = Pt(12)
    tf_d1.paragraphs[0].font.color.rgb = BLUE_ACCENT
    d1_lines = ["• demographic_key (PK)", "• gender (Female, Male)", "• age_group (Child, Youth, Adult, Senior)", "• life_stage"]
    for l in d1_lines:
        p = tf_d1.add_paragraph()
        p.text = l
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK

    # Right Top Dim Box: CLINICAL RISK
    dim2 = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.133), Inches(1.5), Inches(3.6), Inches(2.2))
    dim2.fill.solid()
    dim2.fill.fore_color.rgb = CARD_BG
    dim2.line.color.rgb = BLUE_ACCENT
    dim2.line.width = Pt(1.5)
    tf_d2 = dim2.text_frame
    tf_d2.paragraphs[0].text = "DIM_CLINICAL_RISK (24 Rows)"
    tf_d2.paragraphs[0].font.bold = True
    tf_d2.paragraphs[0].font.size = Pt(12)
    tf_d2.paragraphs[0].font.color.rgb = BLUE_ACCENT
    d2_lines = ["• clinical_risk_key (PK)", "• hypertension_status (No, Yes)", "• heart_disease_status (No, Yes)", "• smoking_category (never, current, etc.)"]
    for l in d2_lines:
        p = tf_d2.add_paragraph()
        p.text = l
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK

    # Bottom Center Dim Box: METRIC RANGES
    dim3 = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(4.5), Inches(3.6), Inches(2.3))
    dim3.fill.solid()
    dim3.fill.fore_color.rgb = CARD_BG
    dim3.line.color.rgb = BLUE_ACCENT
    dim3.line.width = Pt(1.5)
    tf_d3 = dim3.text_frame
    tf_d3.paragraphs[0].text = "DIM_METRIC_RANGES (36 Rows)"
    tf_d3.paragraphs[0].font.bold = True
    tf_d3.paragraphs[0].font.size = Pt(12)
    tf_d3.paragraphs[0].font.color.rgb = BLUE_ACCENT
    d3_lines = ["• metric_range_key (PK)", "• bmi_category (Underweight...Obese)", "• hba1c_category (Normal, Prediabetes...)", "• glucose_category (Normal...Diabetes)"]
    for l in d3_lines:
        p = tf_d3.add_paragraph()
        p.text = l
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK

    # Summary side panel
    side_panel = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.133), Inches(4.2), Inches(3.6), Inches(2.8))
    side_panel.fill.solid()
    side_panel.fill.fore_color.rgb = RGBColor(238, 242, 255)
    side_panel.line.color.rgb = BLUE_ACCENT
    tf_sp = side_panel.text_frame
    tf_sp.word_wrap = True
    tf_sp.paragraphs[0].text = "💡 STAR SCHEMA BENEFITS"
    tf_sp.paragraphs[0].font.bold = True
    tf_sp.paragraphs[0].font.size = Pt(12)
    tf_sp.paragraphs[0].font.color.rgb = BLUE_ACCENT
    benefits = [
        "1. Fast OLAP aggregations across demographic & clinical cuts.",
        "2. Clinical binning standardizes continuous medical variables.",
        "3. Zero data redundancy in dimension tables.",
        "4. Seamless SQL integration for interactive drill-downs & roll-ups."
    ]
    for b in benefits:
        p = tf_sp.add_paragraph()
        p.text = b
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK
        p.space_before = Pt(4)

    # =========================================================================
    # SLIDE 5: Warehouse Design & ETL
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5)
    add_header(slide5, "Warehouse Design Details & ETL Workflow", 5)

    # 3 Column Layout
    col_w = Inches(3.8)
    gap = Inches(0.366)

    # Column 1: Fact Table Grain
    c1 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.4), col_w, Inches(5.6))
    c1.fill.solid()
    c1.fill.fore_color.rgb = CARD_BG
    c1.line.color.rgb = BORDER_COLOR
    tf1 = c1.text_frame
    tf1.word_wrap = True
    tf1.paragraphs[0].text = "📌 FACT TABLE & GRAIN"
    tf1.paragraphs[0].font.bold = True
    tf1.paragraphs[0].font.size = Pt(14)
    tf1.paragraphs[0].font.color.rgb = BLUE_ACCENT
    c1_content = [
        ("Grain Level:", " Exactly one record per patient screening (96,146 total screening records)."),
        ("Primary Key:", " screening_id (Surrogate Key 1..96146)."),
        ("Additive Measures:", " bmi, HbA1c_level, blood_glucose_level."),
        ("Fact Indicators:", " is_diabetic, is_hypertensive, has_heart_disease (binary 0/1 counters)."),
        ("Foreign Keys:", " FK references to 3 dimension tables (demographic_key, clinical_risk_key, metric_range_key).")
    ]
    for b_title, b_text in c1_content:
        p = tf1.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_DARK

    # Column 2: Dimensions & Hierarchies
    c2 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6 + col_w + gap), Inches(1.4), col_w, Inches(5.6))
    c2.fill.solid()
    c2.fill.fore_color.rgb = CARD_BG
    c2.line.color.rgb = BORDER_COLOR
    tf2 = c2.text_frame
    tf2.word_wrap = True
    tf2.paragraphs[0].text = "🌳 DIMENSIONS & HIERARCHIES"
    tf2.paragraphs[0].font.bold = True
    tf2.paragraphs[0].font.size = Pt(14)
    tf2.paragraphs[0].font.color.rgb = BLUE_ACCENT
    c2_content = [
        ("Demographic Hierarchy:", " Gender → Age Group (Child [0-17] → Youth [18-35] → Adult [36-59] → Senior [60+])."),
        ("BMI Clinical Hierarchy:", " Continuous BMI → BMI Category (Underweight [<18.5] → Normal [18.5-24.9] → Overweight [25-29.9] → Obese [≥30])."),
        ("HbA1c Risk Hierarchy:", " Continuous HbA1c → HbA1c Category (Normal [<5.7%] → Prediabetes [5.7-6.4%] → Diabetic Range [≥6.5%])."),
        ("Glucose Risk Hierarchy:", " Continuous Glucose → Glucose Category (Normal [<140] → Impaired [140-199] → Diabetes Range [≥200]).")
    ]
    for b_title, b_text in c2_content:
        p = tf2.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_DARK

    # Column 3: ETL & Tools
    c3 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6 + (col_w + gap)*2), Inches(1.4), col_w, Inches(5.6))
    c3.fill.solid()
    c3.fill.fore_color.rgb = CARD_BG
    c3.line.color.rgb = BORDER_COLOR
    tf3 = c3.text_frame
    tf3.word_wrap = True
    tf3.paragraphs[0].text = "⚙️ ETL PROCESS & TOOLS"
    tf3.paragraphs[0].font.bold = True
    tf3.paragraphs[0].font.size = Pt(14)
    tf3.paragraphs[0].font.color.rgb = BLUE_ACCENT
    c3_content = [
        ("Extract:", " Read raw Kaggle CSV dataset (100,000 screening instances)."),
        ("Transform:", " Deduplication (drop 3,854 duplicates), missing value handling ('No Info' explicit retention), clinical range binning, surrogate key generation."),
        ("Load:", " Automated schema generation & table population into SQLite relational database (diabetes_dw.db)."),
        ("Stack & Tools:", " Python 3.14, pandas, sqlite3, matplotlib, seaborn.")
    ]
    for b_title, b_text in c3_content:
        p = tf3.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 6: Sample OLAP Operations
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6)
    add_header(slide6, "Sample OLAP Operations & Multidimensional Results", 6)

    # Grid 5 Cards for 5 OLAP operations
    op_data = [
        ("1. ROLL-UP (Age Group → Gender)", "Aggregates screening records from detailed Age Groups to high-level Gender.\n\nResult:\n• Female: 56,362 screenings | 3,923 Diabetic (7.0%)\n• Male: 39,784 screenings | 4,559 Diabetic (11.5%)"),
        ("2. DRILL-DOWN (Age Group → BMI Category)", "Drills down from Age Group into detailed BMI categories.\n\nResult:\n• Adult (36-59) Obese: 14,210 screenings | 1,845 Diabetic (13.0%)\n• Senior (60+) Obese: 9,142 screenings | 2,156 Diabetic (23.6%)"),
        ("3. SLICE (HbA1c = 'Diabetic Range (>=6.5%)')", "Filters the cube on a single dimension slice: HbA1c >= 6.5%.\n\nResult:\n• Total Sliced Patients: 12,742\n• Diabetic Patients: 6,750 (53.0% Diabetes Risk!)"),
        ("4. DICE (Male + Senior + Diabetic Glucose)", "Filters sub-cube across 3 dimensions: Male, Senior (60+), Glucose >= 200.\n\nResult:\n• Sub-cube Patients: 1,421\n• Diabetic Patients: 1,288 (90.6% Diabetes Risk!)"),
        ("5. PIVOT (Cross-Tabulation Age vs BMI)", "Rotates axes to cross-tabulate Age Group (Rows) against BMI Category (Cols).\n\nResult: Demonstrates non-linear compound risk multiplier when advancing in age and BMI.")
    ]

    card_positions = [
        (Inches(0.6), Inches(1.4), Inches(5.8), Inches(2.6)),
        (Inches(6.7), Inches(1.4), Inches(6.0), Inches(2.6)),
        (Inches(0.6), Inches(4.2), Inches(3.8), Inches(2.8)),
        (Inches(4.666), Inches(4.2), Inches(3.8), Inches(2.8)),
        (Inches(8.733), Inches(4.2), Inches(3.966), Inches(2.8))
    ]

    for idx, (op_title, op_desc) in enumerate(op_data):
        pos = card_positions[idx]
        card = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, pos[0], pos[1], pos[2], pos[3])
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BLUE_ACCENT if idx == 3 else BORDER_COLOR
        card.line.width = Pt(1.5) if idx == 3 else Pt(1)

        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = op_title
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = BLUE_ACCENT

        p_body = tf.add_paragraph()
        p_body.text = op_desc
        p_body.font.size = Pt(10)
        p_body.font.color.rgb = TEXT_DARK
        p_body.space_before = Pt(4)

    # =========================================================================
    # SLIDE 7: Code - Creating Warehouse (SQL DDL)
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7)
    add_header(slide7, "Code: Creating the Data Warehouse (SQL DDL)", 7)

    sql_code = """-- =============================================================================
-- DMDW PROJECT — Star Schema DDL (SQLite / PostgreSQL Compatible)
-- =============================================================================

CREATE TABLE dim_demographics (
    demographic_key INTEGER PRIMARY KEY AUTOINCREMENT,
    gender TEXT NOT NULL,
    age_group TEXT NOT NULL,
    life_stage TEXT NOT NULL
);

CREATE TABLE dim_clinical_risk (
    clinical_risk_key INTEGER PRIMARY KEY AUTOINCREMENT,
    hypertension_status TEXT NOT NULL,
    heart_disease_status TEXT NOT NULL,
    smoking_category TEXT NOT NULL
);

CREATE TABLE dim_metric_ranges (
    metric_range_key INTEGER PRIMARY KEY AUTOINCREMENT,
    bmi_category TEXT NOT NULL,
    hba1c_category TEXT NOT NULL,
    glucose_category TEXT NOT NULL
);

CREATE TABLE fact_patient_screening (
    screening_id INTEGER PRIMARY KEY AUTOINCREMENT,
    demographic_key INTEGER REFERENCES dim_demographics(demographic_key),
    clinical_risk_key INTEGER REFERENCES dim_clinical_risk(clinical_risk_key),
    metric_range_key INTEGER REFERENCES dim_metric_ranges(metric_range_key),
    bmi REAL NOT NULL,
    HbA1c_level REAL NOT NULL,
    blood_glucose_level INTEGER NOT NULL,
    is_diabetic INTEGER NOT NULL,
    is_hypertensive INTEGER NOT NULL,
    has_heart_disease INTEGER NOT NULL
);"""

    # Code Box
    code_card = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.4), Inches(12.133), Inches(5.6))
    code_card.fill.solid()
    code_card.fill.fore_color.rgb = DARK_NAVY
    code_card.line.color.rgb = BLUE_ACCENT

    tf_c = code_card.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    p.text = sql_code
    p.font.name = "Courier New"
    p.font.size = Pt(9.5)
    p.font.color.rgb = RGBColor(226, 232, 240)

    # =========================================================================
    # SLIDE 8: Code - ETL Pipeline with Python
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8)
    add_header(slide8, "Code: ETL Pipeline in Python (pandas & sqlite3)", 8)

    etl_code = """# =============================================================================
# DMDW PROJECT — Review 1: Concise ETL Pipeline Script
# =============================================================================
import pandas as pd
import sqlite3

# 1. EXTRACT
df = pd.read_csv("data/diabetes_prediction_dataset.csv")

# 2. TRANSFORM & CLEAN
df = df.drop_duplicates()  # Removes 3,854 duplicates -> 96,146 rows

# Derived Clinical Bins
def get_age_group(age):
    return 'Child' if age < 18 else ('Youth' if age < 36 else ('Adult' if age < 60 else 'Senior'))

def get_hba1c_cat(val):
    return 'Normal (<5.7)' if val < 5.7 else ('Prediabetes (5.7-6.4)' if val < 6.5 else 'Diabetic Range (>=6.5)')

df['age_group'] = df['age'].apply(get_age_group)
df['hba1c_category'] = df['HbA1c_level'].apply(get_hba1c_cat)

# 3. LOAD TO DATA WAREHOUSE (SQLite Star Schema)
conn = sqlite3.connect("database/diabetes_dw.db")
# Load Dimension Tables & Populate Fact Table with Surrogate Keys...
df.to_sql("fact_patient_screening", conn, if_exists="append", index=False)
print("✅ ETL Execution Complete: 96,146 Records Loaded into Star Schema DW")"""

    code_card2 = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.4), Inches(12.133), Inches(5.6))
    code_card2.fill.solid()
    code_card2.fill.fore_color.rgb = DARK_NAVY
    code_card2.line.color.rgb = BLUE_ACCENT

    tf_c2 = code_card2.text_frame
    tf_c2.word_wrap = True
    p = tf_c2.paragraphs[0]
    p.text = etl_code
    p.font.name = "Courier New"
    p.font.size = Pt(10)
    p.font.color.rgb = RGBColor(226, 232, 240)

    # =========================================================================
    # SLIDE 9: Code - Sample OLAP Queries
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9)
    add_header(slide9, "Code: Executed Sample OLAP Queries (SQL)", 9)

    olap_code = """-- 1. ROLL-UP: Aggregate Diabetes Count from Age Group to Gender
SELECT d.gender, COUNT(*) AS total_screenings, SUM(f.is_diabetic) AS diabetic_patients,
       ROUND(AVG(f.is_diabetic)*100, 2) AS prevalence_pct
FROM fact_patient_screening f
JOIN dim_demographics d ON f.demographic_key = d.demographic_key
GROUP BY d.gender;

-- 2. DRILL-DOWN: Breakdown Diabetes Risk from Age Group to BMI Category
SELECT d.age_group, m.bmi_category, COUNT(*) AS patient_count, SUM(f.is_diabetic) AS diabetic_count
FROM fact_patient_screening f
JOIN dim_demographics d ON f.demographic_key = d.demographic_key
JOIN dim_metric_ranges m ON f.metric_range_key = m.metric_range_key
GROUP BY d.age_group, m.bmi_category;

-- 3. SLICE: Fix HbA1c Category = 'Diabetic Range (>=6.5%)'
SELECT d.age_group, COUNT(*) AS slice_count, SUM(f.is_diabetic) AS diabetic_count
FROM fact_patient_screening f
JOIN dim_demographics d ON f.demographic_key = d.demographic_key
JOIN dim_metric_ranges m ON f.metric_range_key = m.metric_range_key
WHERE m.hba1c_category = 'Diabetic Range (>=6.5%)'
GROUP BY d.age_group;

-- 4. DICE: Sub-cube filtering Male + Senior (60+) + High Glucose (>=200)
SELECT d.gender, d.age_group, m.glucose_category, COUNT(*) AS total, SUM(f.is_diabetic) AS diabetic
FROM fact_patient_screening f
JOIN dim_demographics d ON f.demographic_key = d.demographic_key
JOIN dim_metric_ranges m ON f.metric_range_key = m.metric_range_key
WHERE d.gender = 'Male' AND d.age_group = 'Senior (60+)' AND m.glucose_category = 'Diabetes Range (>=200)'
GROUP BY d.gender, d.age_group, m.glucose_category;"""

    code_card3 = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.4), Inches(12.133), Inches(5.6))
    code_card3.fill.solid()
    code_card3.fill.fore_color.rgb = DARK_NAVY
    code_card3.line.color.rgb = BLUE_ACCENT

    tf_c3 = code_card3.text_frame
    tf_c3.word_wrap = True
    p = tf_c3.paragraphs[0]
    p.text = olap_code
    p.font.name = "Courier New"
    p.font.size = Pt(9)
    p.font.color.rgb = RGBColor(226, 232, 240)

    # Save presentation
    output_pptx = "/home/vct/Desktop/DMDW PROJECT/Diabetes_Prediction_DMDW_Review1.pptx"
    prs.save(output_pptx)
    print(f"✅ PPTX Presentation successfully created at: {output_pptx}")

if __name__ == "__main__":
    create_presentation()
