# Retail Promotion Intelligence & Campaign Optimization
### An End-to-End Enterprise Analytics, Econometric Causal Inference, and Machine Learning Project

[![Python 3.14+](https://img.shields.io/badge/Python-3.14%2B-blue.svg)](https://www.python.org/)
[![DuckDB 1.5](https://img.shields.io/badge/DuckDB-1.5.6-yellow.svg)](https://duckdb.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.4.1-orange.svg)](https://xgboost.readthedocs.io/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Ready-gold.svg)](https://powerbi.microsoft.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **Recruiter & Executive Summary (Read in 2 Minutes):**
> Built on **Dunnhumby’s Complete Journey** dataset (2,500 panel households, 2.6M transactions, 711 consecutive shopping days), this project goes beyond descriptive dashboards. It diagnoses severe promotional margin dilution, proves that targeted customers had **+$24.50/week pre-existing selection bias** before campaigns ever ran, isolates the true **+$21.62/week causal lift (ATT)** via Propensity Score Matched Difference-in-Differences econometrics, trains an out-of-time **XGBoost response classifier (PR-AUC 0.479, 4.98x top-decile lift)**, and formulates a **T-Learner Incremental Uplift Engine**. 
> 
> **Key Business Impact:** Shifting marketing from traditional "Propensity Targeting" (which subsidizes full-price *Sure Things* at **-91.7% ROI**) to "Incremental Uplift Targeting" (targeting strictly margin-positive *Persuadables*) delivers **+$2,590 Net Profit and an 828.2% Campaign ROI**.

---

## 1. Business Problem & Executive Context

Retailers spend 15–20% of gross revenue on promotional markdowns, circular print mailers, and coupon campaigns. However, **more than 70% of promotional spend fails to generate incremental profit**:
1. **The "Sure Thing" Margin Trap:** Traditional predictive models optimize for *Response Propensity* ($P(\text{Buy} \mid \text{Promotion})$). This leads algorithms to target the retailer's most loyal VIP customers who would have purchased anyway at full margin, causing severe margin cannibalization.
2. **Selection Bias Fallacy:** Marketing teams celebrate that targeted households spend more than non-targeted households, confusing pre-existing loyalty with promotional effectiveness.
3. **Cartesian Data Hazards:** Real-world POS and marketing exposure datasets contain complex multi-display placements and voluntary survey gaps that cause naive SQL analyses to inflate sales numbers.

---

## 2. Project Architecture & Pipeline Flow

```
RAW CSV LAYER (Immutable, 8 Tables, 680+ MB)
  │
  ▼
STAGING & CLEANING ENGINE (src/preprocessing/etl_pipeline.py)
  ├── 1. Deduplicate coupon catalogue (119,384 distinct triplets)
  ├── 2. Pre-aggregate multi-location store-week stimuli (resolving 15,245 Cartesian conflict groups)
  ├── 3. Standardize POS discount conventions & flag fuel/BOGO records without dropping revenue
  └── 4. Impute full 2,500 panel demographics ('UNENROLLED' handling)
  │
  ▼
ANALYTICAL STAR SCHEMA (data/analytical/retail_bi.duckdb + Apache Parquet)
  ├── fact_transactions (2,595,732 rows, PK: basket_id, product_id)
  ├── fact_campaign_assignment (7,208 assignments)
  ├── fact_coupon_redemption (2,318 events, 100% temporal alignment)
  ├── dim_customer (2,500 households, PK: household_key)
  ├── dim_product (92,353 products, PK: product_id)
  ├── dim_campaign (30 campaigns, PK: campaign_id)
  └── dim_store (582 stores, 115 causal-tracked)
  │
  ▼
ADVANCED ANALYTICS & CAUSAL / ML MODELING
  ├── SQL Business Analytics: 12 standalone production queries (Pareto, cadence, co-occurrence)
  ├── Customer 360 Feature Mart (RFM, basket velocity, inter-purchase times, discount reliance)
  ├── Customer Segmentation: Rule-based RFM vs K-Means clustering (Silhouette & Elbow optimized)
  ├── Retention Survival Analysis: Empirical cadence quantiles & defensible 45-day churn threshold
  ├── Econometric Causal Inference: Propensity Score Matching (PSM) + Difference-in-Differences (DiD)
  ├── Predictive ML: Time-based validated XGBoost (ROC-AUC 0.890, PR-AUC 0.479, 4.98x Top Decile Lift)
  └── Uplift Optimization: T-Learner CATE, 4 strategic archetypes, Unit economics net value maximization
  │
  ▼
BUSINESS INTELLIGENCE & DECISION SUITE
  ├── Power BI Semantic Model: Star Schema, 30+ DAX measures, 5 interactive dashboard pages
  └── Executive Reports & Visuals: 7 publication figures, findings reports, Quantium defense
```

---

## 3. Data Quality Audit & Cleaning Decisions

Our audit of all 8 source tables revealed critical data engineering challenges:

| Problem Identified | Empirical Evidence | Engineering Decision | Business & Statistical Rationale |
| :--- | :--- | :--- | :--- |
| **Multi-Location Display Keys** | 15,245 product-store-weeks appear multiple times in `causal_data.csv` (e.g. shelf + end-cap). | Collapsed using `MAX(display != '0')` flag in `causal_lookup`. | Prevents Cartesian join explosion when joining to transactions, which would artificially inflate sales by ~30,000 line items. |
| **Exact Coupon Duplicates** | 5,164 exact duplicate rows in `coupon.csv` (4.15% of table). | Deduplicated during Parquet ingestion (`SELECT DISTINCT`). | Preserves 3NF relational integrity and prevents inflated eligible SKU counts. |
| **Voluntary Survey Bias** | Only 801 of 2,500 households (32.04%) answered demographic surveys. | Retained all 2,500 households; imputed `'UNENROLLED'` category. | Dropping un-surveyed customers discards 68% of enterprise revenue and introduces severe non-response bias. |
| **Fuel Meter Outliers** | Maximum scanned quantity was 89,638 units (`SALES_VALUE = $110.00`, Unleaded Gas). | Retained spend; created `is_fuel` flag and `basket_units` normalization. | Gasoline pumps log pulse counters or fuel points; dropping rows erases real revenue, but keeping raw quantity distorts items/basket. |
| **Zero-Dollar Transactions** | 18,850 zero-dollar lines; 14,399 zero-qty lines and 4,451 pos-qty lines. | Tagged with `is_bogo_or_free` and `is_register_adjustment`. | Retains BOGO (Buy One Get One) free units and loyalty rewards without causing divide-by-zero errors in Average Unit Price. |

---

## 4. Key Quantitative Findings

### A. Customer Revenue Concentration (Pareto Decile Analysis)
- **Top 10% of Customers (Decile 1):** Drive **34.29%** ($2.76M) of total retail revenue.
- **Top 30% of Customers (Deciles 1–3):** Drive **66.73%** ($5.38M) of total revenue.
- **Bottom 10% of Customers (Decile 10):** Account for just **0.70%** of total revenue.

### B. Merchandise Category Economics
- **Grocery:** Drives **50.81%** ($4.09M) of enterprise sales, absorbing $817k in retail markdowns (17.14% discount depth).
- **Drug GM:** 13.10% ($1.05M).
- **Produce & Fresh Meat:** 13.73% ($1.11M combined) with Meat operating at **24.36% discount depth**.
- **Private Label vs National Brands:** Private label commands **27.77% revenue share** across 99.8% of households with lower average discount depth (13.2% vs 16.0%), delivering superior gross margins.

### C. Shopping Cadence & Empirical Churn Definition
- **Median Inter-Purchase Interval:** **3.0 days**; Mean Interval: **6.94 days**.
- **Cadence Boundaries:** 90% of repeat trips occur within **14.0 days**; 95% occur within **22.0 days**.
- **Defensible Churn Threshold:** Defined at **45 days** ($\ge 97\text{th}$ percentile of normal return cadence). At 45 days of inactivity, the probability of an active shopper not returning by chance is under **3%**. Overall panel lapse rate is **13.80%** (345 households).

---

## 5. Causal Campaign Attribution vs Observational Bias

### The Selection Bias Proof
During the clean **pre-treatment baseline period (Days 1–223 / Weeks 1–31)** before campaigns launched:
- **Treated Households Mean Weekly Spend:** **$32.78**
- **Non-Targeted Households Mean Weekly Spend:** **$8.28**
- **Pre-Existing Baseline Disparity:** **+$24.50 per week** ($p < 10^{-15}$, Standardized Mean Difference = $1.128$)

A naive comparison of post-treatment spending attributes +$38.28/week to campaigns. **Over 64% of that difference was pre-existing customer loyalty.**

### The Econometric Solution: PSM + Difference-in-Differences
1. **Propensity Score Matching (PSM):** Matched 346 treated households 1:1 to unique control households on 6 pre-treatment behavioral covariates using a $0.2 \sigma$ caliper. All Standardized Mean Differences dropped below **0.05** (gold standard).
2. **Difference-in-Differences (DiD) on Matched Sample:**
   $$\text{ATT} = (\Delta \bar{Y}_{\text{Treated}}) - (\Delta \bar{Y}_{\text{Control}}) = (+\$22.12) - (+\$0.50) = \mathbf{+\$21.62 \text{ per week per household}}$$
   - **95% Confidence Interval:** `[+$18.18, +$25.07]`
   - **t-statistic:** $12.29$ | **p-value:** $2.93 \times 10^{-31}$ (Statistically Significant)
   - **Enterprise Causal Incremental Revenue (70 weeks, 1,584 households):** **+$2,397,665**
3. **In-Time Placebo Test:** Tested pre-treatment halves (Weeks 1–16 vs 17–32). Placebo ATT was **$2.39** ($p = 0.1813 > 0.05$), confirming that the **Parallel Trends Assumption holds**.

---

## 6. Machine Learning: Predictive Response Model

- **Task:** Predict coupon redemption across 7,208 campaign flight assignments.
- **Validation:** Strict **out-of-time temporal split** (Train: Days 224–599, Test: Days 600–719).
- **Benchmark Performance:**
  - **XGBoost Classifier (Tuned):** **ROC-AUC = 0.8900**, **PR-AUC = 0.4786**, Brier Score = 0.1024.
  - **Random Forest:** ROC-AUC = 0.8752, PR-AUC = 0.3727.
  - **Logistic Regression (Baseline):** ROC-AUC = 0.9071, PR-AUC = 0.5451.
- **Top-Decile Business Lift:**
  - In unseen future campaigns, the baseline response rate was 9.28%.
  - The model's Top Decile achieved a **46.22% response rate (4.98x lift)**. Deciles 6–10 showed 0% response.
- **Primary Predictive Drivers:** Historical Campaign Redemption Velocity (33.0% importance), Unenrolled Demographic Flag (6.7%), and Historical Retail Markdown Intensity (5.5%).

---

## 7. Strategic Incremental Uplift & ROI Optimization

Using a **T-Learner Quasi-Experimental Uplift Engine**, we separated households into the 4 strategic quadrants and simulated campaign financial performance under supermarket unit economics (28% margin, $0.75 mailer cost, $2.50 avg coupon):

```
+------------------------------------+------------------------------------+
|            SURE THINGS             |            PERSUADABLES            |
|       (2,170 Households, 86.8%)    |         (25 - 334 Households)      |
| Baseline Prob: 97.0% | Uplift: -1.3% | Baseline: 74.0% | Uplift: +9.6%     |
| Action: DO NOT DISCOUNT            | Action: TARGET PRIORITY            |
+------------------------------------+------------------------------------+
|            LOST CAUSES             |           SLEEPING DOGS            |
|        (223 Households, 8.9%)      |         (75 Households, 3.0%)      |
| Baseline: 5.4% | Uplift: -3.4%     | Baseline: 38.2% | Uplift: -19.2%   |
| Action: DO NOT TARGET              | Action: SUPPRESS MARKETING         |
+------------------------------------+------------------------------------+
```

### Financial Portfolio Comparison

| Targeting Strategy | Target Households | Total Cost ($) | Incremental Revenue ($) | Gross Profit ($) | Net Profit ($) | Campaign ROI (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Mass Campaign (Target All)** | 2,500 | $2,504.24 | $11,252.57 | $3,150.72 | +$646.48 | +25.8% |
| **2. Traditional Propensity (Top 35%)** | 875 | $994.49 | $296.49 | $83.02 | **-$911.47** | **-91.7%** |
| **3. Uplift Optimization (ENV > 0)** | **334** | **$312.72** | **$10,366.48** | **$2,902.61** | **+$2,589.90** | **+828.2%** |
| **4. Budget-Constrained ($2,000 Cap)** | 334 | $312.72 | $10,366.48 | $2,902.61 | +$2,589.90 | +828.2% |

> **Key Takeaway:** Traditional Propensity targeting destroys margin (**-$911 loss**) because it targets Sure Things who would have bought anyway. Uplift targeting delivers **+$2,590 Net Profit and 828% ROI** by targeting only incremental behavior.

---

## 8. Business Recommendations (Consulting Action Matrix)

```
[INSIGHT 1: VIP Margin Cannibalization]
Evidence:     86.8% of households are "Sure Things" with 97% baseline return probability.
Impact:       Targeting them via propensity models yields -$911 net loss and 16% discount waste.
Action:       Suppress promotional circular discounts for Champions. Replace price cuts with non-price loyalty perks (early access, priority checkout, digital receipts).

[INSIGHT 2: Targeted Campaign Type Efficiency]
Evidence:     Type A mass campaigns achieve 45.0% redemption; Type B targeted achieve 17.1%.
Impact:       Type B campaigns currently misallocate budget to low-engagement cohorts.
Action:       Reallocate 40% of Type B mailer spend strictly to the 334 Persuadables, raising campaign ROI to 828%.

[INSIGHT 3: 45-Day Churn Intervention Window]
Evidence:     95% of active return trips occur within 22 days; lapse risk explodes past 35 days.
Impact:       345 households (13.8%) lapsed at study end, representing $420k in lost annual gross spend.
Action:       Implement an automated re-engagement trigger at Day 28 with a high-value category coupon before shopper habits defect to competitors.

[INSIGHT 4: Cross-Category Basket Expansion]
Evidence:     Drug GM + Grocery co-occur in 34.5% of baskets; Produce + Grocery in 30.4%.
Impact:       Micro and convenience baskets (<$25) represent 62.8% of trips.
Action:       Deploy multi-department basket threshold promotions (e.g. "Spend $35 across Fresh Produce + Grocery, get $5 off Drug GM").
```

---

## 9. Power BI Dashboard Suite

The semantic model in `powerbi/` contains 5 interactive pages:
- **Page 1 — Executive Overview:** High-level KPIs, 102-week sales trends, department revenue contributions, campaign flight performance.
- **Page 2 — Customer Intelligence:** RFM treemap, customer spend deciles, shopping cadence distributions, demographic profiling.
- **Page 3 — Campaign Effectiveness:** Causal ATT cards with 95% confidence intervals, matched treated vs control event study curves, campaign type efficiency.
- **Page 4 — Promotion Response:** XGBoost predicted response decile lift curve, feature importance drivers, demographic response slicers.
- **Page 5 — Campaign Optimization:** Quadrant scatter matrix (Baseline vs Uplift), financial strategy comparison waterfall, interactive household targeting decision table.

Pre-exported data files ready for 1-click load into Power BI Desktop are located in `powerbi/data/`. Complete DAX measures are documented in [`powerbi/DAX_Measures_and_Dashboard_Architecture.md`](powerbi/DAX_Measures_and_Dashboard_Architecture.md).

---

## 10. Repository File Structure

```
c:/Users/Avinash/Desktop/dunnhumpy/
├── data/
│   ├── raw/                           <- 8 original immutable CSV datasets
│   ├── cleaned/                       <- Cleaned, deduplicated Apache Parquet tables
│   └── analytical/                    <- Analytical DuckDB warehouse & feature marts
├── notebooks/
│   ├── 01_data_understanding.ipynb    <- Ingestion, table inventories & profiling
│   ├── 02_data_quality_audit.ipynb     <- Hygiene diagnostics, duplicates, join explosions
│   ├── 03_data_cleaning.ipynb         <- Star schema transformations & validations
│   ├── 04_sql_business_analysis.ipynb <- 12 production business SQL queries
│   ├── 05_customer_intelligence.ipynb <- Customer 360 features, RFM & K-Means
│   ├── 06_retention_analysis.ipynb    <- Cadence quantiles, defensible churn threshold
│   ├── 07_campaign_causal_analysis.ipynb <- PSM, Difference-in-Differences, Placebo test
│   ├── 08_response_model.ipynb        <- Time-split XGBoost response classifier
│   └── 09_uplift_targeting.ipynb      <- T-Learner uplift modeling & ROI optimization
├── sql/
│   ├── staging/01_stg_tables.sql
│   ├── analytical/02_star_schema.sql
│   └── business_questions/            <- 12 standalone analytical SQL scripts
├── src/
│   ├── preprocessing/etl_pipeline.py  <- Production ETL & DuckDB indexing
│   ├── features/customer_360.py       <- Customer 360 feature engineering
│   ├── models/
│   │   ├── segmentation.py            <- RFM & K-Means segmentation
│   │   ├── causal_analysis.py         <- Econometric PSM + DiD engine
│   │   └── predictive_response_model.py <- Out-of-time XGBoost classifier
│   └── business/
│       ├── run_sql_analytics.py       <- SQL query execution suite
│       ├── retention_survival.py      <- Empirical cadence & survival analysis
│       ├── uplift_targeting.py        <- Portfolio ROI & uplift optimization
│       └── generate_eda_charts.py     <- Publication figure generator
├── models/                            <- Serialized joblib models and scalers
├── powerbi/
│   ├── data/                          <- Clean CSV marts for Power BI Desktop
│   ├── powerbi_export_data.py
│   └── DAX_Measures_and_Dashboard_Architecture.md
├── reports/
│   ├── figures/                       <- 7 publication-ready PNG charts
│   ├── sql_analytics_findings.md
│   ├── retention_analysis_findings.md
│   ├── causal_campaign_effectiveness.md
│   ├── predictive_response_modeling.md
│   ├── uplift_business_value.md
│   └── eda_insights_report.md
├── main.py                            <- Master pipeline orchestrator & CLI
├── app.py                             <- Interactive Streamlit executive web application
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 11. Quickstart & Execution Guide

### 1. Run the Complete End-to-End Pipeline
To execute all 10 stages (ETL, Customer 360, Segmentation, Retention, Causal DiD, XGBoost Response, Uplift ROI, SQL Analytics, Figures, and Power BI export) in sequence:
```bash
python main.py
```
*Options:*
- `python main.py --all`: Run all pipeline steps.
- `python main.py --force-etl`: Force full raw CSV re-ingestion into DuckDB.
- `python main.py --step <name>`: Run a single step (e.g. `causal`, `predictive`, `uplift`, `analytics`, `charts`).
- `python main.py --web`: Run pipeline and launch interactive Streamlit web application.

### 2. Launch Interactive Executive Web Dashboard
```bash
streamlit run app.py
```
Access the interactive decision cockpit at `http://localhost:8505` to explore real-time KPIs, customer dossiers, causal balance curves, XGBoost response prediction, and live marketing ROI simulators.

---

## 12. Technology Stack
- **Database & OLAP Engine:** [DuckDB 1.5.6](https://duckdb.org/) (High-performance in-process vectorized SQL)
- **Data Engineering & Storage:** Python 3.14, Apache Parquet, PyArrow
- **Statistical & Causal Modeling:** SciPy, Statsmodels, Scikit-Learn
- **Machine Learning & Uplift:** XGBoost 3.4.1, Logistic Regression, Random Forest, T-Learner
- **Visualization & Web App:** Streamlit 1.65.0, Plotly 7.1.0, Matplotlib, Seaborn, Power BI Desktop (DAX)
