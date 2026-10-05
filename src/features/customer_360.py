"""
Retail Promotion Intelligence & Campaign Optimization
Customer 360 Feature Engineering Pipeline
Module: src/features/customer_360.py

Computes granular behavioral, transactional, discount sensitivity, cadence,
and promotional responsiveness features for all 2,500 panel households.
"""

import os
import sys
import logging
import duckdb
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Customer360")

BASE_DIR = r"c:\Users\Avinash\Desktop\dunnhumpy"
DB_PATH = os.path.join(BASE_DIR, "data", "analytical", "retail_bi.duckdb").replace("\\", "/")
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned").replace("\\", "/")
ANALYTICAL_DIR = os.path.join(BASE_DIR, "data", "analytical").replace("\\", "/")

def compute_customer_360():
    logger.info("Connecting to DuckDB Analytical Warehouse: %s", DB_PATH)
    con = duckdb.connect(DB_PATH)
    
    # 1. Total study duration reference: max day is 711
    max_day = con.execute("SELECT MAX(day) FROM fact_transactions;").fetchone()[0]
    logger.info("Maximum reference day in transaction history: %d", max_day)
    
    # 2. Build Customer 360 Feature Mart
    sql = f"""
    CREATE OR REPLACE TABLE customer_360 AS
    WITH trans_agg AS (
        SELECT 
            household_key,
            -- Recency: Days since last shopping trip relative to study conclusion (Day 711)
            ({max_day} - MAX(day)) AS recency_days,
            
            -- Frequency: Total distinct transaction baskets
            COUNT(DISTINCT basket_id) AS total_baskets,
            COUNT(DISTINCT day) AS total_shopping_days,
            
            -- Monetary: Total Net Revenue spent ($)
            ROUND(SUM(sales_value), 2) AS total_net_spend,
            ROUND(SUM(gross_shelf_value), 2) AS total_gross_spend,
            
            -- Basket Sizing & Velocity
            ROUND(SUM(sales_value) / NULLIF(COUNT(DISTINCT basket_id), 0), 2) AS avg_basket_value,
            ROUND(SUM(CASE WHEN is_fuel = FALSE THEN quantity ELSE 1 END) * 1.0 / NULLIF(COUNT(DISTINCT basket_id), 0), 2) AS avg_items_per_basket,
            
            -- Product & Category Variety Breadth
            COUNT(DISTINCT product_id) AS unique_products_purchased,
            
            -- Promotional & Discount Sensitivity
            ROUND(SUM(retail_disc_amt), 2) AS total_retail_discounts,
            ROUND(SUM(coupon_disc_amt + coupon_match_disc_amt), 2) AS total_coupon_discounts,
            ROUND(SUM(total_disc_amt), 2) AS total_discounts_captured,
            
            -- Discount Depth Percentage
            ROUND(
                SUM(total_disc_amt) * 100.0 / NULLIF(SUM(gross_shelf_value), 0), 2
            ) AS discount_reliance_pct,
            
            -- BOGO & Free Item Propensity
            COUNT(CASE WHEN is_bogo_or_free = TRUE THEN 1 END) AS total_free_or_bogo_items,
            
            -- First and last transaction days
            MIN(day) AS first_active_day,
            MAX(day) AS last_active_day,
            (MAX(day) - MIN(day) + 1) AS customer_tenure_days
        FROM fact_transactions
        GROUP BY household_key
    ),
    
    -- Category and Department Diversity
    dept_agg AS (
        SELECT 
            t.household_key,
            COUNT(DISTINCT p.department) AS unique_departments_shopped,
            COUNT(DISTINCT p.commodity_desc) AS unique_commodities_shopped,
            
            -- Spend in Core Grocery vs Drug GM vs Fresh Meat/Produce
            ROUND(SUM(CASE WHEN p.department = 'GROCERY' THEN t.sales_value ELSE 0 END), 2) AS grocery_spend,
            ROUND(SUM(CASE WHEN p.department IN ('MEAT', 'MEAT-PCKGD', 'SEAFOOD', 'SEAFOOD-PCKGD') THEN t.sales_value ELSE 0 END), 2) AS meat_seafood_spend,
            ROUND(SUM(CASE WHEN p.department = 'PRODUCE' THEN t.sales_value ELSE 0 END), 2) AS produce_spend,
            ROUND(SUM(CASE WHEN p.department = 'DRUG GM' THEN t.sales_value ELSE 0 END), 2) AS drug_gm_spend,
            ROUND(SUM(CASE WHEN t.is_fuel = TRUE THEN t.sales_value ELSE 0 END), 2) AS fuel_spend,
            
            -- Brand Affinity: Private Label Share of Spend
            ROUND(
                SUM(CASE WHEN p.brand_type = 'Private Label' THEN t.sales_value ELSE 0 END) * 100.0 /
                NULLIF(SUM(t.sales_value), 0), 2
            ) AS private_label_spend_pct
        FROM fact_transactions t
        JOIN dim_product p ON t.product_id = p.product_id
        GROUP BY t.household_key
    ),
    
    -- Cadence: Inter-Purchase Intervals
    cadence_calc AS (
        SELECT 
            household_key,
            ROUND(AVG(day_diff), 2) AS avg_interpurchase_days,
            ROUND(STDDEV(day_diff), 2) AS std_interpurchase_days,
            MEDIAN(day_diff) AS median_interpurchase_days,
            MAX(day_diff) AS max_gap_days
        FROM (
            SELECT 
                household_key,
                day - LAG(day) OVER (PARTITION BY household_key ORDER BY day) AS day_diff
            FROM (
                SELECT DISTINCT household_key, day 
                FROM fact_transactions
            )
        )
        WHERE day_diff IS NOT NULL
        GROUP BY household_key
    ),
    
    -- Campaign Exposure & Coupon Redemptions
    camp_exposure AS (
        SELECT 
            c.household_key,
            COUNT(DISTINCT c.campaign_id) AS total_campaigns_received,
            COUNT(DISTINCT CASE WHEN c.campaign_type = 'TypeA' THEN c.campaign_id END) AS campaigns_type_a,
            COUNT(DISTINCT CASE WHEN c.campaign_type = 'TypeB' THEN c.campaign_id END) AS campaigns_type_b,
            COUNT(DISTINCT CASE WHEN c.campaign_type = 'TypeC' THEN c.campaign_id END) AS campaigns_type_c
        FROM fact_campaign_assignment c
        GROUP BY c.household_key
    ),
    coupon_redempt_agg AS (
        SELECT 
            r.household_key,
            COUNT(r.coupon_upc) AS total_coupons_redeemed,
            COUNT(DISTINCT r.campaign_id) AS distinct_campaigns_redeemed,
            COUNT(DISTINCT r.coupon_upc) AS unique_coupon_codes_redeemed
        FROM fact_coupon_redemption r
        GROUP BY r.household_key
    )
    
    SELECT 
        -- Identification & Demographics
        cust.household_key,
        cust.has_survey_demographics,
        cust.age_desc,
        cust.marital_status,
        cust.income_desc,
        cust.homeowner_desc,
        cust.hh_comp_desc,
        cust.household_size,
        cust.kid_category,
        
        -- RFM & Core Behavioral
        t.recency_days,
        t.total_baskets,
        t.total_shopping_days,
        t.total_net_spend,
        t.total_gross_spend,
        t.avg_basket_value,
        t.avg_items_per_basket,
        t.customer_tenure_days,
        
        -- Cadence & Regularity
        COALESCE(cad.avg_interpurchase_days, t.customer_tenure_days) AS avg_interpurchase_days,
        COALESCE(cad.std_interpurchase_days, 0.0) AS std_interpurchase_days,
        COALESCE(cad.median_interpurchase_days, t.customer_tenure_days) AS median_interpurchase_days,
        COALESCE(cad.max_gap_days, t.customer_tenure_days) AS max_gap_days,
        
        -- Variety & Department Penetration
        dept.unique_departments_shopped,
        dept.unique_commodities_shopped,
        t.unique_products_purchased,
        dept.grocery_spend,
        dept.meat_seafood_spend,
        dept.produce_spend,
        dept.drug_gm_spend,
        dept.fuel_spend,
        dept.private_label_spend_pct,
        
        -- Promotional Engagement & Price Sensitivity
        t.total_retail_discounts,
        t.total_coupon_discounts,
        t.total_discounts_captured,
        t.discount_reliance_pct,
        t.total_free_or_bogo_items,
        
        -- Campaign & Coupon History
        COALESCE(camp.total_campaigns_received, 0) AS total_campaigns_received,
        COALESCE(camp.campaigns_type_a, 0) AS campaigns_type_a,
        COALESCE(camp.campaigns_type_b, 0) AS campaigns_type_b,
        COALESCE(camp.campaigns_type_c, 0) AS campaigns_type_c,
        COALESCE(red.total_coupons_redeemed, 0) AS total_coupons_redeemed,
        COALESCE(red.distinct_campaigns_redeemed, 0) AS distinct_campaigns_redeemed,
        COALESCE(red.unique_coupon_codes_redeemed, 0) AS unique_coupon_codes_redeemed,
        
        -- Campaign Response Propensity Ratio
        CASE 
            WHEN COALESCE(camp.total_campaigns_received, 0) > 0 
            THEN ROUND(COALESCE(red.distinct_campaigns_redeemed, 0) * 1.0 / camp.total_campaigns_received, 4)
            ELSE 0.0 
        END AS campaign_redemption_rate,
        
        -- Direct Binary Promotion Responder Indicator (Ever Redeemed)
        CASE WHEN COALESCE(red.total_coupons_redeemed, 0) > 0 THEN 1 ELSE 0 END AS is_coupon_responder
        
    FROM dim_customer cust
    JOIN trans_agg t ON cust.household_key = t.household_key
    JOIN dept_agg dept ON cust.household_key = dept.household_key
    LEFT JOIN cadence_calc cad ON cust.household_key = cad.household_key
    LEFT JOIN camp_exposure camp ON cust.household_key = camp.household_key
    LEFT JOIN coupon_redempt_agg red ON cust.household_key = red.household_key
    ORDER BY cust.household_key;
    """
    
    con.execute(sql)
    parquet_path = os.path.join(ANALYTICAL_DIR, "customer_360.parquet").replace("\\", "/")
    con.execute(f"COPY customer_360 TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    
    cnt = con.execute("SELECT COUNT(*) FROM customer_360;").fetchone()[0]
    responders = con.execute("SELECT COUNT(*) FROM customer_360 WHERE is_coupon_responder = 1;").fetchone()[0]
    targeted = con.execute("SELECT COUNT(*) FROM customer_360 WHERE total_campaigns_received > 0;").fetchone()[0]
    
    logger.info(f"customer_360 feature mart successfully compiled:")
    logger.info(f"  - Total Households: {cnt:,}")
    logger.info(f"  - Households Targeted by Campaigns: {targeted:,} ({targeted*100/cnt:.1f}%)")
    logger.info(f"  - Coupon Responders: {responders:,} ({responders*100/cnt:.1f}%)")
    logger.info(f"  - Parquet Mart Saved -> {parquet_path}")
    con.close()

if __name__ == "__main__":
    compute_customer_360()
