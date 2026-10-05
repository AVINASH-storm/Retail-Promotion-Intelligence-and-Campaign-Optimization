"""
Retail Promotion Intelligence & Campaign Optimization
Jupyter Notebook Generator
Module: scratch/create_notebooks.py

Generates the complete 9-notebook portfolio suite matching enterprise standards:
01_data_understanding.ipynb
02_data_quality_audit.ipynb
03_data_cleaning.ipynb
04_sql_business_analysis.ipynb
05_customer_intelligence.ipynb
06_retention_analysis.ipynb
07_campaign_causal_analysis.ipynb
08_response_model.ipynb
09_uplift_targeting.ipynb
"""

import os
import json

BASE_DIR = r"c:\Users\Avinash\Desktop\dunnhumpy"
NB_DIR = os.path.join(BASE_DIR, "notebooks")

def make_cell(cell_type, source):
    return {
        "cell_type": cell_type,
        "metadata": {},
        "source": [s + "\n" for s in source.split("\n")]
    }

def make_code_cell(code):
    cell = make_cell("code", code)
    cell["execution_count"] = None
    cell["outputs"] = []
    return cell

def save_notebook(filename, cells):
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.14.8"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    filepath = os.path.join(NB_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)
    print(f"Created notebook: {filename}")

# 1. 01_data_understanding.ipynb
c1 = [
    make_cell("markdown", "# Notebook 01: Data Understanding & Inventory Exploration\n**Project:** Retail Promotion Intelligence & Campaign Optimization\n**Dataset:** Dunnhumby - The Complete Journey (8 Raw Datasets)"),
    make_code_cell("import os\nimport duckdb\nimport pandas as pd\n\ncon = duckdb.connect()\nraw_dir = '../data/raw'\nprint('Available Raw CSV Files:', os.listdir(raw_dir))"),
    make_cell("markdown", "### 1. Ingest and Profile Table Sizes"),
    make_code_cell("""tables = ['campaign_desc', 'campaign_table', 'coupon', 'coupon_redempt', 'hh_demographic', 'product', 'transaction_data', 'causal_data']
inventory = []
for t in tables:
    cnt = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{raw_dir}/{t}.csv')").fetchone()[0]
    inventory.append({'Table': t, 'Rows': cnt})
pd.DataFrame(inventory)"""),
    make_cell("markdown", "### 2. Inspect Schema & Samples for Core Tables"),
    make_code_cell("con.execute(f\"SELECT * FROM read_csv_auto('{raw_dir}/transaction_data.csv') LIMIT 5\").df()")
]
save_notebook("01_data_understanding.ipynb", c1)

# 2. 02_data_quality_audit.ipynb
c2 = [
    make_cell("markdown", "# Notebook 02: Data Quality Audit & Hygiene Diagnostic\n**Focus:** Integrity auditing, duplicate detection, orphan foreign keys, impossible quantities, and join explosions."),
    make_code_cell("import duckdb\nimport pandas as pd\ncon = duckdb.connect()\nraw_dir = '../data/raw'"),
    make_cell("markdown", "### 1. Duplicate Row Checks Across Tables"),
    make_code_cell("""# Checking coupon.csv exact duplicates
total_coups = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{raw_dir}/coupon.csv')").fetchone()[0]
distinct_coups = con.execute(f"SELECT COUNT(*) FROM (SELECT DISTINCT * FROM read_csv_auto('{raw_dir}/coupon.csv'))").fetchone()[0]
print(f'coupon.csv: Total={total_coups:,}, Distinct={distinct_coups:,}, Duplicates={total_coups - distinct_coups:,}')"""),
    make_cell("markdown", "### 2. Causal Data Multi-Display Cartesian Risk"),
    make_code_cell("""causal_dups = con.execute(f\"\"\"
    SELECT COUNT(*) FROM (
        SELECT PRODUCT_ID, STORE_ID, WEEK_NO 
        FROM read_csv_auto('{raw_dir}/causal_data.csv') 
        GROUP BY PRODUCT_ID, STORE_ID, WEEK_NO 
        HAVING COUNT(*) > 1
    )
\"\"\").fetchone()[0]
print(f'Multi-location display conflict groups in causal_data: {causal_dups:,}')"""),
    make_cell("markdown", "### 3. Numerical Value Ranges & Outliers in Transactions"),
    make_code_cell("""con.execute(f\"\"\"
    SELECT 
        MIN(SALES_VALUE) as min_sales, MAX(SALES_VALUE) as max_sales,
        MIN(QUANTITY) as min_qty, MAX(QUANTITY) as max_qty,
        COUNT(CASE WHEN SALES_VALUE = 0 THEN 1 END) as zero_sales,
        COUNT(CASE WHEN QUANTITY = 0 THEN 1 END) as zero_qty
    FROM read_csv_auto('{raw_dir}/transaction_data.csv')
\"\"\").df()""")
]
save_notebook("02_data_quality_audit.ipynb", c2)

# 3. 03_data_cleaning.ipynb
c3 = [
    make_cell("markdown", "# Notebook 03: Data Cleaning & Star Schema Engineering\n**Focus:** Deduplication, discount standardization, demographic imputation, and Parquet staging."),
    make_code_cell("import duckdb\nimport pandas as pd\ncon = duckdb.connect('../data/analytical/retail_bi.duckdb')"),
    make_cell("markdown", "### 1. Verify Star Schema Tables in Analytical DuckDB"),
    make_code_cell("con.execute('SHOW TABLES;').df()"),
    make_cell("markdown", "### 2. Validate Fact Transactions Metrics"),
    make_code_cell("""con.execute('''
    SELECT 
        COUNT(*) as total_rows,
        ROUND(SUM(sales_value), 2) as total_net_revenue,
        ROUND(SUM(retail_disc_amt), 2) as total_retail_discounts,
        ROUND(SUM(coupon_disc_amt), 2) as total_coupon_discounts,
        COUNT(CASE WHEN is_fuel = TRUE THEN 1 END) as fuel_rows,
        COUNT(CASE WHEN is_bogo_or_free = TRUE THEN 1 END) as bogo_free_rows
    FROM fact_transactions
''').df()""")
]
save_notebook("03_data_cleaning.ipynb", c3)

# 4. 04_sql_business_analysis.ipynb
c4 = [
    make_cell("markdown", "# Notebook 04: SQL Business Analytics & Strategic KPIs\n**Focus:** Pareto revenue concentration, department dynamics, shopping cadence, and market basket co-occurrence."),
    make_code_cell("import duckdb\ncon = duckdb.connect('../data/analytical/retail_bi.duckdb', read_only=True)"),
    make_cell("markdown", "### 1. Customer Revenue Concentration Deciles (Pareto Analysis)"),
    make_code_cell("""with open('../sql/business_questions/01_customer_revenue_concentration.sql') as f:
    sql = f.read()
con.execute(sql).df()"""),
    make_cell("markdown", "### 2. Department Revenue & Discount Depth"),
    make_code_cell("""with open('../sql/business_questions/02_department_category_drivers.sql') as f:
    sql = f.read()
con.execute(sql).df()"""),
    make_cell("markdown", "### 3. Shopping Cadence & Inter-Purchase Days"),
    make_code_cell("""with open('../sql/business_questions/04_shopping_frequency_interpurchase_time.sql') as f:
    sql = f.read()
con.execute(sql).df()""")
]
save_notebook("04_sql_business_analysis.ipynb", c4)

# 5. 05_customer_intelligence.ipynb
c5 = [
    make_cell("markdown", "# Notebook 05: Customer Intelligence & 360 Feature Mart\n**Focus:** Recency, frequency, monetary value, discount sensitivity, and customer segmentation."),
    make_code_cell("import duckdb\nimport pandas as pd\ncon = duckdb.connect('../data/analytical/retail_bi.duckdb', read_only=True)"),
    make_cell("markdown", "### 1. Customer 360 Feature Distribution"),
    make_code_cell("df = con.execute('SELECT * FROM customer_360').df()\ndf[['recency_days', 'total_baskets', 'total_net_spend', 'avg_basket_value', 'discount_reliance_pct']].describe()"),
    make_cell("markdown", "### 2. Rule-Based RFM vs K-Means Personas"),
    make_code_cell("""con.execute('''
    SELECT s.cluster_persona, COUNT(*) as households, ROUND(AVG(c.total_net_spend), 2) as avg_spend, ROUND(AVG(c.recency_days), 1) as avg_recency
    FROM customer_360 c
    JOIN customer_segments s ON c.household_key = s.household_key
    GROUP BY s.cluster_persona
    ORDER BY avg_spend DESC
''').df()""")
]
save_notebook("05_customer_intelligence.ipynb", c5)

# 6. 06_retention_analysis.ipynb
c6 = [
    make_cell("markdown", "# Notebook 06: Customer Retention & Survival Analysis\n**Focus:** Empirical shopping gap quantiles, defensible churn threshold, and cohort retention dynamics."),
    make_code_cell("import duckdb\nimport pandas as pd\nimport numpy as np\ncon = duckdb.connect('../data/analytical/retail_bi.duckdb', read_only=True)"),
    make_cell("markdown", "### 1. Empirical Gap Distribution & Churn Threshold"),
    make_code_cell("""gaps = con.execute('''
    SELECT day - LAG(day) OVER (PARTITION BY household_key ORDER BY day) as gap
    FROM (SELECT DISTINCT household_key, day FROM fact_transactions)
''').df()['gap'].dropna()
print('Mean Gap:', gaps.mean(), 'Median:', gaps.median(), 'p90:', gaps.quantile(0.9), 'p95:', gaps.quantile(0.95))"""),
    make_cell("markdown", "### 2. Lapsed Rates by Customer Segment"),
    make_code_cell("""con.execute('''
    SELECT s.cluster_persona, COUNT(*) as total, SUM(r.is_lapsed) as lapsed,
           ROUND(SUM(r.is_lapsed)*100.0/COUNT(*), 2) as lapse_rate_pct
    FROM customer_segments s
    JOIN customer_retention_status r ON s.household_key = r.household_key
    GROUP BY s.cluster_persona ORDER BY lapse_rate_pct DESC
''').df()""")
]
save_notebook("06_retention_analysis.ipynb", c6)

# 7. 07_campaign_causal_analysis.ipynb
c7 = [
    make_cell("markdown", "# Notebook 07: Campaign Causal Effectiveness & Econometrics\n**Focus:** Selection bias proof, Propensity Score Matching (PSM), Difference-in-Differences (DiD), and parallel trends check."),
    make_code_cell("import duckdb\nimport pandas as pd\ncon = duckdb.connect('../data/analytical/retail_bi.duckdb', read_only=True)"),
    make_cell("markdown", "### 1. Pre-Treatment Baseline Spend Comparison (Proving Selection Bias)"),
    make_code_cell("""pre_spend = con.execute('''
    WITH pre AS (
        SELECT household_key, SUM(sales_value)/32.0 as pre_wk_spend
        FROM fact_transactions WHERE day <= 223 GROUP BY household_key
    )
    SELECT 
        CASE WHEN c.total_campaigns_received > 0 THEN 'Targeted (T=1)' ELSE 'Control (T=0)' END as group_type,
        COUNT(*) as households,
        ROUND(AVG(COALESCE(p.pre_wk_spend, 0)), 2) as avg_pre_weekly_spend
    FROM customer_360 c
    LEFT JOIN pre p ON c.household_key = p.household_key
    GROUP BY 1
''').df()
pre_spend"""),
    make_cell("markdown", "### 2. Causal Econometric Results Summary"),
    make_code_cell("""with open('../reports/causal_campaign_effectiveness.md') as f:
    print(''.join(f.readlines()[15:45]))""")
]
save_notebook("07_campaign_causal_analysis.ipynb", c7)

# 8. 08_response_model.ipynb
c8 = [
    make_cell("markdown", "# Notebook 08: Predictive Campaign Response Modeling\n**Focus:** Out-of-time temporal validation, Logistic regression baseline, XGBoost, PR-AUC evaluation, and feature importance."),
    make_code_cell("import joblib\nimport pandas as pd\nimport duckdb\ncon = duckdb.connect('../data/analytical/retail_bi.duckdb', read_only=True)"),
    make_cell("markdown", "### 1. Out-of-Time Predicted Response Distribution"),
    make_code_cell("preds = con.execute('SELECT * FROM campaign_predictions').df()\npreds.head()"),
    make_code_cell("""preds['pred_decile'] = pd.qcut(preds['predicted_response_prob'].rank(method='first', ascending=False), q=10, labels=False) + 1
dec_summary = preds.groupby('pred_decile').agg(
    total=('response', 'count'),
    actual_responders=('response', 'sum'),
    response_rate=('response', 'mean')
).reset_index()
dec_summary['lift_vs_baseline'] = dec_summary['response_rate'] / preds['response'].mean()
dec_summary""")
]
save_notebook("08_response_model.ipynb", c8)

# 9. 09_uplift_targeting.ipynb
c9 = [
    make_cell("markdown", "# Notebook 09: Incremental Uplift & Financial Optimization\n**Focus:** Two-Model T-Learner, 4 Strategic Archetypes, Expected Net Value (ENV), and Portfolio Targeting Strategies."),
    make_code_cell("import duckdb\nimport pandas as pd\ncon = duckdb.connect('../data/analytical/retail_bi.duckdb', read_only=True)"),
    make_cell("markdown", "### 1. Uplift Archetype Breakdown"),
    make_code_cell("""con.execute('''
    SELECT uplift_archetype, COUNT(*) as households,
           ROUND(COUNT(*)*100.0/2500, 2) as pct_households,
           ROUND(AVG(predicted_uplift)*100, 2) as avg_uplift_pct,
           ROUND(AVG(expected_net_value), 2) as avg_env
    FROM customer_uplift_decisions
    GROUP BY uplift_archetype
    ORDER BY households DESC
''').df()"""),
    make_cell("markdown", "### 2. Portfolio Strategy Financial Comparison"),
    make_code_cell("""with open('../reports/uplift_business_value.md') as f:
    print(''.join(f.readlines()[25:60]))""")
]
save_notebook("09_uplift_targeting.ipynb", c9)

print("\nAll 9 notebooks generated successfully!")
