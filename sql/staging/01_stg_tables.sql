-- ==============================================================================
-- Retail Promotion Intelligence & Campaign Optimization
-- Staging DDL Script: sql/staging/01_stg_tables.sql
-- Ingestion layer from raw CSV sources into DuckDB staging tables
-- ==============================================================================

-- 1. Staging Products
CREATE OR REPLACE TABLE stg_product AS
SELECT 
    PRODUCT_ID,
    MANUFACTURER,
    DEPARTMENT,
    BRAND,
    COMMODITY_DESC,
    SUB_COMMODITY_DESC,
    CURR_SIZE_OF_PRODUCT
FROM read_csv_auto('data/raw/product.csv');

-- 2. Staging Household Demographics
CREATE OR REPLACE TABLE stg_hh_demographic AS
SELECT 
    AGE_DESC,
    MARITAL_STATUS_CODE,
    INCOME_DESC,
    HOMEOWNER_DESC,
    HH_COMP_DESC,
    HOUSEHOLD_SIZE_DESC,
    KID_CATEGORY_DESC,
    household_key
FROM read_csv_auto('data/raw/hh_demographic.csv');

-- 3. Staging Campaign Descriptions
CREATE OR REPLACE TABLE stg_campaign_desc AS
SELECT 
    DESCRIPTION,
    CAMPAIGN,
    START_DAY,
    END_DAY
FROM read_csv_auto('data/raw/campaign_desc.csv');

-- 4. Staging Campaign Target Assignments
CREATE OR REPLACE TABLE stg_campaign_table AS
SELECT 
    DESCRIPTION,
    household_key,
    CAMPAIGN
FROM read_csv_auto('data/raw/campaign_table.csv');

-- 5. Staging Coupons (Raw with duplicates)
CREATE OR REPLACE TABLE stg_coupon AS
SELECT 
    COUPON_UPC,
    PRODUCT_ID,
    CAMPAIGN
FROM read_csv_auto('data/raw/coupon.csv');

-- 6. Staging Coupon Redemptions
CREATE OR REPLACE TABLE stg_coupon_redempt AS
SELECT 
    household_key,
    DAY,
    COUPON_UPC,
    CAMPAIGN
FROM read_csv_auto('data/raw/coupon_redempt.csv');

-- 7. Staging Store-Level Causal Marketing Stimuli
CREATE OR REPLACE TABLE stg_causal_data AS
SELECT 
    PRODUCT_ID,
    STORE_ID,
    WEEK_NO,
    display,
    mailer
FROM read_csv_auto('data/raw/causal_data.csv');

-- 8. Staging Point-of-Sale Transactions
CREATE OR REPLACE TABLE stg_transaction_data AS
SELECT 
    household_key,
    BASKET_ID,
    DAY,
    PRODUCT_ID,
    QUANTITY,
    SALES_VALUE,
    STORE_ID,
    RETAIL_DISC,
    TRANS_TIME,
    WEEK_NO,
    COUPON_DISC,
    COUPON_MATCH_DISC
FROM read_csv_auto('data/raw/transaction_data.csv');
