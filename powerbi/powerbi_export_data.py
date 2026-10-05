"""
Retail Promotion Intelligence & Campaign Optimization
Power BI Analytical Export Pipeline
Module: powerbi/powerbi_export_data.py

Exports production Star Schema tables and model predictions into powerbi/data/
ready for direct import into Power BI Desktop or Service.
"""

import os
import sys
import logging
import duckdb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("PowerBIExport")

BASE_DIR = r"c:\Users\Avinash\Desktop\dunnhumpy"
DB_PATH = os.path.join(BASE_DIR, "data", "analytical", "retail_bi.duckdb").replace("\\", "/")
PBI_DATA_DIR = os.path.join(BASE_DIR, "powerbi", "data").replace("\\", "/")

def export_powerbi_data():
    os.makedirs(PBI_DATA_DIR, exist_ok=True)
    con = duckdb.connect(DB_PATH, read_only=True)
    
    logger.info("Exporting Star Schema and Analytical marts for Power BI...")
    
    # 1. Dim_Customer with RFM Segments and Uplift Archetypes enriched
    logger.info("Exporting Dim_Customer...")
    con.execute(f"""
        COPY (
            SELECT 
                c.household_key,
                c.has_survey_demographics,
                c.age_desc,
                c.marital_status,
                c.income_desc,
                c.homeowner_desc,
                c.household_size,
                c.kid_category,
                c.total_net_spend,
                c.total_baskets,
                c.avg_basket_value,
                c.recency_days,
                s.rfm_segment,
                s.rfm_score_str,
                s.cluster_persona,
                u.uplift_archetype,
                u.predicted_uplift,
                u.expected_net_value,
                u.targeting_roi_pct,
                ret.is_lapsed
            FROM customer_360 c
            LEFT JOIN customer_segments s ON c.household_key = s.household_key
            LEFT JOIN customer_uplift_decisions u ON c.household_key = u.household_key
            LEFT JOIN customer_retention_status ret ON c.household_key = ret.household_key
        ) TO '{PBI_DATA_DIR}/Dim_Customer.csv' (HEADER, DELIMITER ',');
    """)
    
    # 2. Dim_Product
    logger.info("Exporting Dim_Product...")
    con.execute(f"""
        COPY (
            SELECT product_id, manufacturer, department, brand_type, commodity_desc, sub_commodity_desc
            FROM dim_product
        ) TO '{PBI_DATA_DIR}/Dim_Product.csv' (HEADER, DELIMITER ',');
    """)
    
    # 3. Dim_Campaign
    logger.info("Exporting Dim_Campaign...")
    con.execute(f"""
        COPY (
            SELECT campaign_id, campaign_type, start_day, end_day, duration_days, households_targeted
            FROM dim_campaign
        ) TO '{PBI_DATA_DIR}/Dim_Campaign.csv' (HEADER, DELIMITER ',');
    """)
    
    # 4. Fact_Campaign_Assignment
    logger.info("Exporting Fact_Campaign_Assignment...")
    con.execute(f"""
        COPY (
            SELECT campaign_id, household_key, campaign_type, start_day, end_day, duration_days
            FROM fact_campaign_assignment
        ) TO '{PBI_DATA_DIR}/Fact_Campaign_Assignment.csv' (HEADER, DELIMITER ',');
    """)
    
    # 5. Fact_Coupon_Redemption
    logger.info("Exporting Fact_Coupon_Redemption...")
    con.execute(f"""
        COPY (
            SELECT household_key, day, coupon_upc, campaign_id
            FROM fact_coupon_redemption
        ) TO '{PBI_DATA_DIR}/Fact_Coupon_Redemption.csv' (HEADER, DELIMITER ',');
    """)

    # 6. Aggregated Fact_Basket_Summary (Optimized for Power BI fast rendering)
    logger.info("Exporting Fact_Basket_Summary...")
    con.execute(f"""
        COPY (
            SELECT 
                basket_id,
                household_key,
                day,
                week_no,
                store_id,
                COUNT(DISTINCT product_id) AS distinct_items,
                SUM(CASE WHEN is_fuel = FALSE THEN quantity ELSE 1 END) AS basket_units,
                ROUND(SUM(sales_value), 2) AS basket_spend,
                ROUND(SUM(retail_disc_amt), 2) AS retail_discount_amt,
                ROUND(SUM(coupon_disc_amt + coupon_match_disc_amt), 2) AS coupon_discount_amt,
                ROUND(SUM(total_disc_amt), 2) AS total_discount_amt,
                ROUND(SUM(gross_shelf_value), 2) AS gross_shelf_spend,
                MAX(CASE WHEN is_fuel = TRUE THEN 1 ELSE 0 END) AS has_fuel_purchase
            FROM fact_transactions
            GROUP BY basket_id, household_key, day, week_no, store_id
        ) TO '{PBI_DATA_DIR}/Fact_Basket_Summary.csv' (HEADER, DELIMITER ',');
    """)

    # 7. Department-Level Weekly Transaction Mart (For Category & Time Visuals)
    logger.info("Exporting Fact_Weekly_Department_Sales...")
    con.execute(f"""
        COPY (
            SELECT 
                t.week_no,
                p.department,
                p.brand_type,
                COUNT(DISTINCT t.household_key) AS active_shoppers,
                COUNT(DISTINCT t.basket_id) AS basket_penetration,
                ROUND(SUM(t.sales_value), 2) AS net_revenue,
                ROUND(SUM(t.total_disc_amt), 2) AS total_discounts,
                SUM(CASE WHEN t.is_fuel = FALSE THEN t.quantity ELSE 1 END) AS total_units
            FROM fact_transactions t
            JOIN dim_product p ON t.product_id = p.product_id
            GROUP BY t.week_no, p.department, p.brand_type
        ) TO '{PBI_DATA_DIR}/Fact_Weekly_Department_Sales.csv' (HEADER, DELIMITER ',');
    """)

    con.close()
    logger.info(f"Power BI data tables successfully exported to {PBI_DATA_DIR}")

if __name__ == "__main__":
    export_powerbi_data()
