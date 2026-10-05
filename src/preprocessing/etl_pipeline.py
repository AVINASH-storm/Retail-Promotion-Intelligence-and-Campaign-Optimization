"""
Retail Promotion Intelligence & Campaign Optimization
ETL & Data Cleaning Pipeline
Module: src/preprocessing/etl_pipeline.py

Transforms raw CSV datasets into an optimized, validated analytical Star Schema
in Apache Parquet and persistent DuckDB database formats.
"""

import os
import sys
import time
import logging
import duckdb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ETLPipeline")

BASE_DIR = r"c:\Users\Avinash\Desktop\dunnhumpy"
RAW_DIR = os.path.join(BASE_DIR, "data", "raw").replace("\\", "/")
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned").replace("\\", "/")
ANALYTICAL_DIR = os.path.join(BASE_DIR, "data", "analytical").replace("\\", "/")
DB_PATH = os.path.join(ANALYTICAL_DIR, "retail_bi.duckdb").replace("\\", "/")

def get_connection():
    os.makedirs(CLEANED_DIR, exist_ok=True)
    os.makedirs(ANALYTICAL_DIR, exist_ok=True)
    con = duckdb.connect(DB_PATH)
    # Enable multi-threading and optimized memory usage
    con.execute("PRAGMA threads=4;")
    con.execute("PRAGMA memory_limit='8GB';")
    return con

def build_dim_product(con):
    logger.info("Transforming dim_product...")
    sql = f"""
    CREATE OR REPLACE TABLE dim_product AS
    SELECT 
        CAST(PRODUCT_ID AS BIGINT) AS product_id,
        CAST(MANUFACTURER AS BIGINT) AS manufacturer,
        COALESCE(NULLIF(TRIM(DEPARTMENT), ''), 'UNMAPPED') AS department,
        CASE 
            WHEN UPPER(TRIM(BRAND)) = 'NATIONAL' THEN 'National Brand'
            ELSE 'Private Label'
        END AS brand_type,
        COALESCE(NULLIF(TRIM(COMMODITY_DESC), ''), 'UNMAPPED') AS commodity_desc,
        COALESCE(NULLIF(TRIM(SUB_COMMODITY_DESC), ''), 'UNMAPPED') AS sub_commodity_desc,
        NULLIF(TRIM(CURR_SIZE_OF_PRODUCT), '') AS curr_size
    FROM read_csv_auto('{RAW_DIR}/product.csv');
    """
    con.execute(sql)
    parquet_path = f"{CLEANED_DIR}/dim_product.parquet"
    con.execute(f"COPY dim_product TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    cnt = con.execute("SELECT COUNT(*) FROM dim_product").fetchone()[0]
    logger.info(f"dim_product created: {cnt:,} rows -> {parquet_path}")

def build_dim_customer(con):
    logger.info("Transforming dim_customer with full 2,500 panel coverage...")
    sql = f"""
    CREATE OR REPLACE TABLE dim_customer AS
    WITH all_households AS (
        SELECT DISTINCT CAST(household_key AS BIGINT) AS household_key
        FROM read_csv_auto('{RAW_DIR}/transaction_data.csv')
    ),
    demo AS (
        SELECT 
            CAST(household_key AS BIGINT) AS household_key,
            AGE_DESC AS age_desc,
            CASE 
                WHEN MARITAL_STATUS_CODE = 'A' THEN 'Married'
                WHEN MARITAL_STATUS_CODE = 'B' THEN 'Single'
                ELSE 'Unknown'
            END AS marital_status,
            INCOME_DESC AS income_desc,
            HOMEOWNER_DESC AS homeowner_desc,
            HH_COMP_DESC AS hh_comp_desc,
            HOUSEHOLD_SIZE_DESC AS household_size,
            KID_CATEGORY_DESC AS kid_category
        FROM read_csv_auto('{RAW_DIR}/hh_demographic.csv')
    )
    SELECT 
        h.household_key,
        COALESCE(d.age_desc, 'UNENROLLED') AS age_desc,
        COALESCE(d.marital_status, 'UNENROLLED') AS marital_status,
        COALESCE(d.income_desc, 'UNENROLLED') AS income_desc,
        COALESCE(d.homeowner_desc, 'UNENROLLED') AS homeowner_desc,
        COALESCE(d.hh_comp_desc, 'UNENROLLED') AS hh_comp_desc,
        COALESCE(d.household_size, 'UNENROLLED') AS household_size,
        COALESCE(d.kid_category, 'UNENROLLED') AS kid_category,
        CASE WHEN d.household_key IS NOT NULL THEN TRUE ELSE FALSE END AS has_survey_demographics
    FROM all_households h
    LEFT JOIN demo d ON h.household_key = d.household_key
    ORDER BY h.household_key;
    """
    con.execute(sql)
    parquet_path = f"{CLEANED_DIR}/dim_customer.parquet"
    con.execute(f"COPY dim_customer TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    cnt = con.execute("SELECT COUNT(*) FROM dim_customer").fetchone()[0]
    survey_cnt = con.execute("SELECT COUNT(*) FROM dim_customer WHERE has_survey_demographics = TRUE").fetchone()[0]
    logger.info(f"dim_customer created: {cnt:,} households ({survey_cnt:,} surveyed) -> {parquet_path}")

def build_dim_campaign(con):
    logger.info("Transforming dim_campaign...")
    sql = f"""
    CREATE OR REPLACE TABLE dim_campaign AS
    WITH target_counts AS (
        SELECT 
            CAST(CAMPAIGN AS BIGINT) AS campaign_id,
            COUNT(DISTINCT household_key) AS households_targeted
        FROM read_csv_auto('{RAW_DIR}/campaign_table.csv')
        GROUP BY CAMPAIGN
    )
    SELECT 
        CAST(cd.CAMPAIGN AS BIGINT) AS campaign_id,
        TRIM(cd.DESCRIPTION) AS campaign_type,
        CAST(cd.START_DAY AS INTEGER) AS start_day,
        CAST(cd.END_DAY AS INTEGER) AS end_day,
        CAST((cd.END_DAY - cd.START_DAY + 1) AS INTEGER) AS duration_days,
        COALESCE(tc.households_targeted, 0) AS households_targeted
    FROM read_csv_auto('{RAW_DIR}/campaign_desc.csv') cd
    LEFT JOIN target_counts tc ON CAST(cd.CAMPAIGN AS BIGINT) = tc.campaign_id
    ORDER BY cd.CAMPAIGN;
    """
    con.execute(sql)
    parquet_path = f"{CLEANED_DIR}/dim_campaign.parquet"
    con.execute(f"COPY dim_campaign TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    cnt = con.execute("SELECT COUNT(*) FROM dim_campaign").fetchone()[0]
    logger.info(f"dim_campaign created: {cnt:,} campaigns -> {parquet_path}")

def build_dim_coupon(con):
    logger.info("Transforming dim_coupon (deduplicating 5,164 exact duplicate rows)...")
    sql = f"""
    CREATE OR REPLACE TABLE dim_coupon AS
    SELECT DISTINCT
        CAST(COUPON_UPC AS BIGINT) AS coupon_upc,
        CAST(PRODUCT_ID AS BIGINT) AS product_id,
        CAST(CAMPAIGN AS BIGINT) AS campaign_id
    FROM read_csv_auto('{RAW_DIR}/coupon.csv');
    """
    con.execute(sql)
    parquet_path = f"{CLEANED_DIR}/dim_coupon.parquet"
    con.execute(f"COPY dim_coupon TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    cnt = con.execute("SELECT COUNT(*) FROM dim_coupon").fetchone()[0]
    logger.info(f"dim_coupon created: {cnt:,} unique coupon-product-campaign triplets -> {parquet_path}")

def build_dim_store(con):
    logger.info("Transforming dim_store...")
    sql = f"""
    CREATE OR REPLACE TABLE dim_store AS
    WITH trans_stores AS (
        SELECT DISTINCT CAST(STORE_ID AS BIGINT) AS store_id
        FROM read_csv_auto('{RAW_DIR}/transaction_data.csv')
    ),
    causal_stores AS (
        SELECT DISTINCT CAST(STORE_ID AS BIGINT) AS store_id
        FROM read_csv_auto('{RAW_DIR}/causal_data.csv')
    )
    SELECT 
        ts.store_id,
        CASE WHEN cs.store_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_causal_tracking
    FROM trans_stores ts
    LEFT JOIN causal_stores cs ON ts.store_id = cs.store_id
    ORDER BY ts.store_id;
    """
    con.execute(sql)
    parquet_path = f"{CLEANED_DIR}/dim_store.parquet"
    con.execute(f"COPY dim_store TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    cnt = con.execute("SELECT COUNT(*) FROM dim_store").fetchone()[0]
    causal_cnt = con.execute("SELECT COUNT(*) FROM dim_store WHERE has_causal_tracking = TRUE").fetchone()[0]
    logger.info(f"dim_store created: {cnt:,} stores ({causal_cnt:,} causal tracked) -> {parquet_path}")

def build_causal_lookup(con):
    logger.info("Transforming causal_data into aggregated store-week lookup (resolving 15,245 multi-display records)...")
    sql = f"""
    CREATE OR REPLACE TABLE causal_lookup AS
    SELECT 
        CAST(PRODUCT_ID AS BIGINT) AS product_id,
        CAST(STORE_ID AS BIGINT) AS store_id,
        CAST(WEEK_NO AS INTEGER) AS week_no,
        MAX(CASE WHEN display != '0' THEN 1 ELSE 0 END) AS has_display,
        MAX(CASE WHEN mailer != '0' THEN 1 ELSE 0 END) AS has_mailer,
        MAX(display) AS display_code,
        MAX(mailer) AS mailer_code
    FROM read_csv_auto('{RAW_DIR}/causal_data.csv')
    GROUP BY PRODUCT_ID, STORE_ID, WEEK_NO;
    """
    con.execute(sql)
    parquet_path = f"{CLEANED_DIR}/causal_lookup.parquet"
    con.execute(f"COPY causal_lookup TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    cnt = con.execute("SELECT COUNT(*) FROM causal_lookup").fetchone()[0]
    logger.info(f"causal_lookup created: {cnt:,} unique product-store-week entries -> {parquet_path}")

def build_fact_campaign_assignment(con):
    logger.info("Transforming fact_campaign_assignment...")
    sql = f"""
    CREATE OR REPLACE TABLE fact_campaign_assignment AS
    SELECT 
        CAST(c.CAMPAIGN AS BIGINT) AS campaign_id,
        CAST(c.household_key AS BIGINT) AS household_key,
        TRIM(c.DESCRIPTION) AS campaign_type,
        cd.start_day,
        cd.end_day,
        cd.duration_days
    FROM read_csv_auto('{RAW_DIR}/campaign_table.csv') c
    JOIN dim_campaign cd ON CAST(c.CAMPAIGN AS BIGINT) = cd.campaign_id;
    """
    con.execute(sql)
    parquet_path = f"{CLEANED_DIR}/fact_campaign_assignment.parquet"
    con.execute(f"COPY fact_campaign_assignment TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    cnt = con.execute("SELECT COUNT(*) FROM fact_campaign_assignment").fetchone()[0]
    logger.info(f"fact_campaign_assignment created: {cnt:,} assignments -> {parquet_path}")

def build_fact_coupon_redemption(con):
    logger.info("Transforming fact_coupon_redemption...")
    sql = f"""
    CREATE OR REPLACE TABLE fact_coupon_redemption AS
    SELECT 
        CAST(household_key AS BIGINT) AS household_key,
        CAST(DAY AS INTEGER) AS day,
        CAST(COUPON_UPC AS BIGINT) AS coupon_upc,
        CAST(CAMPAIGN AS BIGINT) AS campaign_id
    FROM read_csv_auto('{RAW_DIR}/coupon_redempt.csv');
    """
    con.execute(sql)
    parquet_path = f"{CLEANED_DIR}/fact_coupon_redemption.parquet"
    con.execute(f"COPY fact_coupon_redemption TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    cnt = con.execute("SELECT COUNT(*) FROM fact_coupon_redemption").fetchone()[0]
    logger.info(f"fact_coupon_redemption created: {cnt:,} redemptions -> {parquet_path}")

def build_fact_transactions(con):
    logger.info("Transforming fact_transactions with standardized discounts and business flags...")
    sql = f"""
    CREATE OR REPLACE TABLE fact_transactions AS
    SELECT 
        CAST(t.BASKET_ID AS BIGINT) AS basket_id,
        CAST(t.household_key AS BIGINT) AS household_key,
        CAST(t.DAY AS INTEGER) AS day,
        CAST(t.WEEK_NO AS INTEGER) AS week_no,
        CAST(t.STORE_ID AS BIGINT) AS store_id,
        CAST(t.PRODUCT_ID AS BIGINT) AS product_id,
        CAST(t.QUANTITY AS INTEGER) AS quantity,
        CAST(t.SALES_VALUE AS DOUBLE) AS sales_value,
        
        -- Standardize discount conventions (positive magnitudes for intuitive business reporting)
        CASE WHEN t.RETAIL_DISC < 0 THEN ROUND(ABS(t.RETAIL_DISC), 2) ELSE 0.0 END AS retail_disc_amt,
        ROUND(ABS(t.COUPON_DISC), 2) AS coupon_disc_amt,
        ROUND(ABS(t.COUPON_MATCH_DISC), 2) AS coupon_match_disc_amt,
        
        ROUND(
            (CASE WHEN t.RETAIL_DISC < 0 THEN ABS(t.RETAIL_DISC) ELSE 0.0 END) +
            ABS(t.COUPON_DISC) +
            ABS(t.COUPON_MATCH_DISC), 2
        ) AS total_disc_amt,
        
        -- Gross shelf revenue before discounts
        ROUND(
            t.SALES_VALUE + 
            (CASE WHEN t.RETAIL_DISC < 0 THEN ABS(t.RETAIL_DISC) ELSE 0.0 END) +
            ABS(t.COUPON_DISC) +
            ABS(t.COUPON_MATCH_DISC), 2
        ) AS gross_shelf_value,
        
        -- Discount depth percentage
        CASE 
            WHEN (t.SALES_VALUE + (CASE WHEN t.RETAIL_DISC < 0 THEN ABS(t.RETAIL_DISC) ELSE 0.0 END) + ABS(t.COUPON_DISC) + ABS(t.COUPON_MATCH_DISC)) > 0
            THEN ROUND(
                ((CASE WHEN t.RETAIL_DISC < 0 THEN ABS(t.RETAIL_DISC) ELSE 0.0 END) + ABS(t.COUPON_DISC) + ABS(t.COUPON_MATCH_DISC)) / 
                (t.SALES_VALUE + (CASE WHEN t.RETAIL_DISC < 0 THEN ABS(t.RETAIL_DISC) ELSE 0.0 END) + ABS(t.COUPON_DISC) + ABS(t.COUPON_MATCH_DISC)), 4
            )
            ELSE 0.0
        END AS discount_depth_pct,
        
        t.TRANS_TIME AS trans_time,
        
        -- Operational flags
        CASE 
            WHEN p.department IN ('KIOSK-GAS', 'MISC SALES TRAN') OR p.sub_commodity_desc LIKE '%GASOLINE%' 
            THEN TRUE ELSE FALSE 
        END AS is_fuel,
        
        CASE WHEN t.SALES_VALUE = 0.0 AND t.QUANTITY > 0 THEN TRUE ELSE FALSE END AS is_bogo_or_free,
        CASE WHEN t.SALES_VALUE = 0.0 AND t.QUANTITY = 0 THEN TRUE ELSE FALSE END AS is_register_adjustment
        
    FROM read_csv_auto('{RAW_DIR}/transaction_data.csv') t
    LEFT JOIN dim_product p ON CAST(t.PRODUCT_ID AS BIGINT) = p.product_id;
    """
    con.execute(sql)
    parquet_path = f"{CLEANED_DIR}/fact_transactions.parquet"
    con.execute(f"COPY fact_transactions TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    cnt = con.execute("SELECT COUNT(*) FROM fact_transactions").fetchone()[0]
    logger.info(f"fact_transactions created: {cnt:,} rows -> {parquet_path}")

def run_pipeline():
    start_time = time.time()
    logger.info("=== STARTING FULL ETL & DATA CLEANING PIPELINE ===")
    con = get_connection()
    
    try:
        build_dim_product(con)
        build_dim_customer(con)
        build_dim_campaign(con)
        build_dim_coupon(con)
        build_dim_store(con)
        build_causal_lookup(con)
        build_fact_campaign_assignment(con)
        build_fact_coupon_redemption(con)
        build_fact_transactions(con)
        
        # DuckDB validation and indexing
        con.execute("CREATE INDEX IF NOT EXISTS idx_trans_hh ON fact_transactions(household_key);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_trans_prod ON fact_transactions(product_id);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_trans_basket ON fact_transactions(basket_id);")
        
        # Summary validation
        logger.info("\n=== ETL PIPELINE VALIDATION SUMMARY ===")
        tables = [
            "dim_product", "dim_customer", "dim_campaign", "dim_coupon", 
            "dim_store", "causal_lookup", "fact_campaign_assignment", 
            "fact_coupon_redemption", "fact_transactions"
        ]
        for t in tables:
            row_cnt = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            logger.info(f"Table: {t:<26} | Rows: {row_cnt:>12,}")
            
        elapsed = time.time() - start_time
        logger.info(f"=== PIPELINE EXECUTED SUCCESSFULLY IN {elapsed:.2f}s ===")
    finally:
        con.close()

if __name__ == "__main__":
    run_pipeline()
