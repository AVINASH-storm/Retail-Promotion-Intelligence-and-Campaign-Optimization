-- ==============================================================================
-- Retail Promotion Intelligence & Campaign Optimization
-- Analytical Star Schema DDL: sql/analytical/02_star_schema.sql
-- Production Dimensional Model with Primary & Foreign Key Constraints and Views
-- ==============================================================================

-- 1. DIMENSION: Products
CREATE OR REPLACE TABLE dim_product (
    product_id BIGINT PRIMARY KEY,
    manufacturer BIGINT,
    department VARCHAR,
    brand_type VARCHAR,
    commodity_desc VARCHAR,
    sub_commodity_desc VARCHAR,
    curr_size VARCHAR
);

-- 2. DIMENSION: Customers (2,500 Full Universe with Imputed Demographics)
CREATE OR REPLACE TABLE dim_customer (
    household_key BIGINT PRIMARY KEY,
    age_desc VARCHAR,
    marital_status VARCHAR,
    income_desc VARCHAR,
    homeowner_desc VARCHAR,
    hh_comp_desc VARCHAR,
    household_size VARCHAR,
    kid_category VARCHAR,
    has_survey_demographics BOOLEAN
);

-- 3. DIMENSION: Campaigns (30 Campaigns)
CREATE OR REPLACE TABLE dim_campaign (
    campaign_id BIGINT PRIMARY KEY,
    campaign_type VARCHAR,
    start_day INTEGER,
    end_day INTEGER,
    duration_days INTEGER,
    households_targeted INTEGER
);

-- 4. DIMENSION: Coupons (Deduplicated UPC to Product Mapping)
CREATE OR REPLACE TABLE dim_coupon (
    coupon_upc BIGINT,
    product_id BIGINT,
    campaign_id BIGINT,
    PRIMARY KEY (coupon_upc, product_id, campaign_id)
);

-- 5. DIMENSION: Stores (582 Stores with Marketing Instrumentation Flag)
CREATE OR REPLACE TABLE dim_store (
    store_id BIGINT PRIMARY KEY,
    has_causal_tracking BOOLEAN
);

-- 6. AGGREGATED LOOKUP: Causal Marketing Stimuli (Store-Week Level)
CREATE OR REPLACE TABLE causal_lookup (
    product_id BIGINT,
    store_id BIGINT,
    week_no INTEGER,
    has_display INTEGER,
    has_mailer INTEGER,
    display_code VARCHAR,
    mailer_code VARCHAR,
    PRIMARY KEY (product_id, store_id, week_no)
);

-- 7. FACT: Campaign Target Assignments
CREATE OR REPLACE TABLE fact_campaign_assignment (
    campaign_id BIGINT,
    household_key BIGINT,
    campaign_type VARCHAR,
    start_day INTEGER,
    end_day INTEGER,
    duration_days INTEGER,
    PRIMARY KEY (campaign_id, household_key)
);

-- 8. FACT: Coupon Redemptions
CREATE OR REPLACE TABLE fact_coupon_redemption (
    household_key BIGINT,
    day INTEGER,
    coupon_upc BIGINT,
    campaign_id BIGINT,
    PRIMARY KEY (household_key, day, coupon_upc, campaign_id)
);

-- 9. FACT: Point-of-Sale Transactions
CREATE OR REPLACE TABLE fact_transactions (
    basket_id BIGINT,
    household_key BIGINT,
    day INTEGER,
    week_no INTEGER,
    store_id BIGINT,
    product_id BIGINT,
    quantity INTEGER,
    sales_value DOUBLE,
    retail_disc_amt DOUBLE,
    coupon_disc_amt DOUBLE,
    coupon_match_disc_amt DOUBLE,
    total_disc_amt DOUBLE,
    gross_shelf_value DOUBLE,
    discount_depth_pct DOUBLE,
    trans_time VARCHAR,
    is_fuel BOOLEAN,
    is_bogo_or_free BOOLEAN,
    is_register_adjustment BOOLEAN,
    PRIMARY KEY (basket_id, product_id)
);

-- Core Business Views for High-Velocity Reporting
CREATE OR REPLACE VIEW v_basket_summary AS
SELECT 
    basket_id,
    household_key,
    day,
    week_no,
    store_id,
    COUNT(DISTINCT product_id) AS distinct_items,
    SUM(CASE WHEN is_fuel = FALSE THEN quantity ELSE 1 END) AS total_units,
    ROUND(SUM(sales_value), 2) AS basket_spend,
    ROUND(SUM(retail_disc_amt), 2) AS total_retail_disc,
    ROUND(SUM(coupon_disc_amt + coupon_match_disc_amt), 2) AS total_coupon_disc,
    ROUND(SUM(total_disc_amt), 2) AS total_savings,
    CASE WHEN SUM(gross_shelf_value) > 0 
         THEN ROUND(SUM(total_disc_amt) / SUM(gross_shelf_value), 4) 
         ELSE 0.0 END AS basket_discount_rate
FROM fact_transactions
GROUP BY basket_id, household_key, day, week_no, store_id;
