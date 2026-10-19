# UI Redesign Handoff — BRFSS Diabetes Analytics Dashboard

**For:** UI/UX Designer
**Project:** Interactive diabetes analytics dashboard built on CDC BRFSS 2015 survey data (academic analytics prototype).
**Scope:** Full redesign of 10 existing app pages + 1 new landing page.

---

## 1. Product summary (what you are designing)

A dark-themed, data-dense analytics web app. All numbers come from pre-computed research artifacts (CSV/JSON) — the UI is a **visualization and exploration layer**, not a form-heavy product. Recurring themes:

- Charts and tables are the heroes; text is supporting context.
- Every health-related page must display **disclaimer banners** (educational only, not medical advice).
- Data provenance matters: pages show where each number comes from.

---

## 2. Recommended stack (for easy integration)

### Primary recommendation: Next.js (App Router) + TypeScript

| Layer | Technology | Why |
|---|---|---|
| Framework | **Next.js 14/15 (App Router) + TypeScript** | SSR for the landing page (SEO), component reuse, easy Vercel/Netlify deploy |
| Styling | **Tailwind CSS v4 + design tokens** | Token-first; designer owns palette/spacing in one place |
| Component kit | **shadcn/ui** (Radix primitives) | Accessible selects/tabs/sliders/toggles that map 1:1 to current Streamlit widgets |
| Charts | **Recharts or ECharts** for standard charts; **Plotly.js** only if you need the interactive polar/radar/heatmap parity | Matches current chart inventory (bar, line, scatter, heatmap, radar/polar, histogram, imshow) |
| Tables | **TanStack Table** | Sortable, filterable; matches current styled dataframes |
| Data layer | **Server components read the CSV/JSON artifacts at build/request time** (no Python runtime needed for display); optional Route Handlers for the custom OLAP query | Artifacts live in `review2/results/*.csv`, `review1/*.json` |

**Integration note for the designer:** hand off **Figma with a token page** (colors, radii, spacing, type scale) plus **component variants** (button, card, metric card, tab, slider, select, toggle, banner/callout, table, chart frame). The dev maps tokens → Tailwind config and components → shadcn/ui.

### Alternative (lower effort): keep Streamlit, redesign via theme

If the team wants to keep the Python stack: Streamlit theming (`[theme]` in `.streamlit/config.toml`) + custom CSS components. Much cheaper, but **limited**: no landing page SEO, constrained layout control. Only pick this if timeline is very tight.

---

## 3. Current design language (starting point — improve, don't preserve blindly)

Existing dark palette:

| Token | Hex | Role |
|---|---|---|
| Navy (bg) | `#0B1220` | Page background |
| Surface | `#111C2E` / `#17233A` | Card & chart backgrounds |
| Sidebar | `#0E1728` | Nav rail |
| Teal (primary accent) | `#2DD4BF` | Primary series, success, insight accent |
| Orange (secondary) | `#FB923C` | Warnings, "your value" markers |
| Sky | `#60A5FA` | Third data series |
| Muted | `#94A3B8` | Neutral series, captions |
| Text | `#E6EDF7` primary / `#AFC0D5` secondary | Typography |
| Border | `#22304A` / `#283852` | Card & header borders |

**Fixed model colors** (used consistently across pages, keep stable in redesign):
CART=`#2DD4BF` · Info-Gain=`#FB923C` · KNN=`#60A5FA` · J48=`#94A3B8` · Naive Bayes=`#FCA5A5`

**Callout styles:** teal-left-border "insight" box; orange-left-border "warning" box.

**Ask from designer:** formalize this into a documented token system (light + dark mode optional), an 8pt spacing scale, type scale, chart palette (categorical, colorblind-safe), and empty/loading/error states.

---

## 4. Global layout & navigation

- **Left sidebar nav** (collapsible on mobile) with logo/wordmark "🩺 BRFSS Analytics", subtitle "Diabetes & cardiovascular comorbidity · 2015".
- **Page header on every page:** H1 title + one-line caption + (where relevant) disclaimer banner.
- **Top area:** optional global selector — "Dataset context: Balanced modeling sample / Full population sample".
- **Footer (every page):** "Academic analytics prototype · CDC BRFSS 2015 · Saved project results are preserved as produced; no clinical use intended."

### Navigation items (in order)
1. Executive Overview
2. Explore the Data
3. Warehouse & OLAP
4. Model Arena
5. Population Reality Check
6. Patterns & Clusters
7. My Health Profile
8. Advanced Model Analytics
9. What-If Explorer
10. Methods & Limitations

**New: 11. Landing page** (see §6) — should be the public entry; app pages sit behind it.

### Shared components to design
- **Metric card** (label, big value, delta/caption line) — used on Overview, Reality Check, Health Profile.
- **Callout banners:** `Insight` (teal), `Warning/Disclaimer` (orange), `Info` (blue).
- **Chart frame:** title, optional caption, dark plot bg, download CSV button, source footnote.
- **Tab bar**, **select/multiselect**, **slider + number input combo**, **toggle**, **form with primary submit**.
- **Data table:** styled, right-aligned numerics, % formatting, optional download.
- **Disclaimer component** (must appear on My Health Profile, What-If Explorer, and any user-input page).

---

## 5. Page-by-page specification

### 5.1 Executive Overview
**Purpose:** one-glance project summary.
- 4 metric cards: Full survey records (`236,386`-scale count), Balanced modeling sample, Missing cells (0), Full-file diabetes prevalence (~9.4% / shown as %).
- Insight callout: "balanced data helps compare classifiers, but it does not represent population prevalence."
- Two-column charts: (L) grouped horizontal bar — risk-factor comparison (% respondents with factor, Diabetes vs No diabetes) with **Sex filter** (All/Female/Male); (R) scatter — Precision vs Recall, bubble size = F1, one point per model.
- Full-width **model scorecard heatmap** (5 models × 5 metrics: Accuracy, Precision, Recall, F1, AUC).
- Data: `review2/results/model_comparison_all.csv`, `review1/eda_metrics.json`, balanced CSV.

### 5.2 Explore the Data
**Purpose:** filterable descriptive EDA on the balanced sample.
- Filter row: **age band range slider** (13 bands, 18–24 … 80+), **sex select**, **income multiselect** (8 bands).
- Live count metric: "Respondents after filters".
- 2×2 chart grid: diabetes share by age (line), by self-rated health (bar), BMI distribution by diabetes status (overlaid histogram), correlation-with-label horizontal bar.
- **Download filtered CSV** button.
- Loading/empty states needed when filters exclude everything.

### 5.3 Warehouse & OLAP
**Purpose:** star-schema OLAP demo + new custom query builder.
- Tabs: **Roll-up, Drill-down, Slice, Dice, Pivot** + new **Custom OLAP Builder** tab.
- Standard tabs: table + chart + per-tab download button (roll-up = bar; drill-down = grouped bar by sex; slice = line; dice = density heatmap; pivot = grouped bar female/male cases).
- **Custom OLAP Builder** (interactive): row-dimension multiselect, column-dimension select, measure select (Count / Diabetes prevalence % / Avg BMI / Avg MentHlth / Avg PhysHlth), **pandas-style filter text input** (e.g. `Age >= 8 and BMI > 30`), primary "Run OLAP query" button → results table + auto chart (bar or heatmap) + CSV download. Needs success/error states for invalid filters.
- Collapsible "Star schema structure" diagram (DIM_DEMOGRAPHICS, DIM_LIFESTYLE, DIM_CLINICAL_RISK, DIM_GENERAL_HEALTH → FACT_HEALTH_SURVEY).

### 5.4 Model Arena
- Comparability warning callout (R held-out vs WEKA 10-fold CV).
- Model select dropdown → 5 metric cards update live.
- Tabs: **All metrics** (grouped bar), **Metric trade-offs** (polar/radar chart, range 0.55–0.9), **Model details** (full table).
- Bottom two charts: KNN CV accuracy by k (line, dashed marker at selected k=29), CART feature importance (top-10 horizontal bar).

### 5.5 Population Reality Check
- Warning callout about full-file evaluation / leakage.
- 3 metric cards: full-file test prevalence (~14%), always-No accuracy (~86.1%), recall at 0.50 (~10.5%).
- **Threshold control (both):** range slider (0.2–0.5, step 0.1) **and** free number input (0.00–1.00, step 0.01) — keep both, they sync.
- 4 metric cards (Accuracy/Precision/Recall/F1 at chosen threshold) that update live.
- Threshold trade-off line chart (4 series) with vertical marker at selected threshold.
- Full trade-off table + interpretation insight callout (0.20 → recall 60.7%/precision 31.7%; 0.50 → recall 10.5%).

### 5.6 Patterns & Clusters
- Tabs: **Apriori association rules** / **K-Means profiles**.
- Rules tab: minimum-lift slider (1.0–2.0), formatted rules table (Support %, Confidence %, Lift), horizontal bar ranked by lift (color = confidence), CSV download. Caption explains sample-conditional confidence/lift.
- Clusters tab: scatter (mean BMI vs diabetes share, bubble = cluster size) + formatted cluster table + 2 static images (elbow plot, dendrogram) with captions. Caption: "K-Means fit with diabetes withheld; share added post-hoc."

### 5.7 My Health Profile
**Purpose:** educational survey comparison from user inputs. Requires disclaimer banner (top) and non-diagnostic caption (bottom).
- Form fields: age band slider, sex select, BMI number input (12–98), 3 toggles (high BP, high cholesterol, physically active), 2 more toggles (difficulty walking, …), general health select (Excellent→Poor), income select (8 bands).
- **NEW — "Additional factors (optional)":** two rows of (free-text factor name + your value + cohort avg %).
- Primary submit: "Compare profile with survey sample".
- After submit: insight callout (comparison cohort scope), 4 metric cards (cohort diabetes share, BMI percentile, nearest survey cluster, cohort size), grouped bar (your profile vs cohort vs all respondents, includes custom factors), BMI histogram with "Your BMI" + "Cohort median" markers, nearest-cluster context bar chart, formatted profile table.

### 5.8 Advanced Model Analytics
- Caption: "All charts use Review 2 saved results — no refitting."
- 7 tabs: **ROC curves** · **Precision–Recall** · **Confusion matrices** · **Learning curves** · **Calibration** · **Lift/Gain** · **Decision boundary**.
- Chart specs: approximate ROC lines per model with diagonal; PR lines; confusion-matrix heatmap (2×2, threshold 0.5); learning curves (train/val per model, simulated — label as descriptive); calibration curves vs perfect diagonal; lift chart vs baseline (~14% prevalence) with reference line; decision-boundary tab is currently a placeholder card pointing to R scripts — **redesign as an informative empty state**.
- Every tab needs an honest caption about approximation/simulation (research-integrity requirement).

### 5.9 What-If Explorer
- Disclaimers: descriptive only, not clinical.
- Form: age band, sex, BMI, toggles (BP, cholesterol, active, difficulty walking), general health, income → primary button "Explore cluster context".
- Results: insight callout naming nearest cluster; **radar/polar chart** (your profile vs 3 cluster centroids, normalized); bar chart of diabetes share by cluster with balanced-sample average reference line; cluster detail table.

### 5.10 Methods & Limitations
- Workflow prose + reproducibility note (seed 42).
- **Review 2 pipeline:** 7 script cards (`01_preprocess.R` … `07_final_comparison.R`) each with copyable command + description — design as a step/timeline component.
- **Limitations:** 5 warning cards (balanced data ≠ prevalence, prediabetes coded 0, self-reported 2015 cross-sectional, WEKA vs R protocols, health profile is descriptive).
- Artifact provenance list (file paths) + external link to CDC BRFSS 2015.

---

## 6. NEW: Landing page specification

**Goal:** public entry that explains the project, establishes trust, and routes into the app. Sits **before** the dashboard.

### Sections
1. **Hero:** product name + one-liner (e.g. "Interactive evidence from 236k+ CDC BRFSS 2015 responses — diabetes risk, comorbidity patterns, and model transparency"). Primary CTA: **"Open the dashboard"**; secondary: "Read the methodology". Hero visual: abstract health-data viz (pulsing ECG line / small multiples of the scorecard heatmap).
2. **Key stats strip:** records analyzed (236,386), modeling sample (~70k balanced), models compared (5), OLAP operations (5) — metric-card style.
3. **Feature cards → link into pages:** Explore the Data · Warehouse & OLAP · Model Arena · Patterns & Clusters · What-If Explorer — each card: icon, 1-line description, chart thumbnail, deep link.
4. **How it works / pipeline:** CSV → EDA → SQLite star schema → stratified preprocessing → models/rules/clusters → dashboard (mirrors Methods page).
5. **Model scorecard preview:** small heatmap teaser + "See full comparison" CTA.
6. **Trust & limitations:** prominent disclaimer (associations not causal; not medical advice; 2015 data; balanced sample ≠ prevalence) + links to Methods & Limitations and CDC source.
7. **Footer:** repo/artifact provenance, CDC BRFSS link, academic prototype note.

### Landing page requirements
- Responsive (mobile-first), fast (static/SSR), accessible (contrast, focus states, semantic HTML).
- Same token system as the app; light/dark optional but dark is the brand default.
- SEO basics: title, meta description, OG image (design one).

---

## 7. Deliverables checklist for the designer

- [ ] Figma file: **design tokens** page (color, type scale, spacing, radii, shadows, chart palette)
- [ ] **Component library** with states: default/hover/focus/disabled/loading/empty/error
- [ ] Landing page: desktop + mobile (≥2 breakpoints) + states
- [ ] All 11 screens: desktop (1440px) + mobile (390px) + tablet (768px)
- [ ] Chart style guide: palette, grid/axis rules, tooltips, legends, empty/loading states
- [ ] Table style guide: density, number/percent formatting, download affordance
- [ ] Disclaimers & microcopy review (health-compliance tone: educational, non-diagnostic)
- [ ] Icons (Lucide or similar) and any illustrations
- [ ] Handoff annotations: component names mapped to shadcn/ui equivalents where possible

## 8. Non-negotiables (research integrity)

1. Every health page keeps a visible **"not medical advice"** disclaimer.
2. Model colors stay consistent across all pages.
3. Approximate/simulated charts must keep their **descriptive captions** — no chart may imply it is a fitted clinical model.
4. Data source footnotes (artifact file paths) remain available (tooltip or footnote).
5. Balanced-sample vs population-prevalence distinction must remain visually prominent.
