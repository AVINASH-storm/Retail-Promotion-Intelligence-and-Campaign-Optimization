-- ==============================================================================
-- Business Question 08: Demographic Promotion Responsiveness
-- Question: Which demographic brackets (Income, Household Size, Kids) show the
--           highest propensity to redeem coupons and capture promotional discounts?
-- ==============================================================================

WITH customer_redemptions AS (
    SELECT 
        household_key,
        COUNT(coupon_upc) AS coupons_redeemed
    FROM fact_coupon_redemption
    GROUP BY household_key
),
customer_promotions AS (
    SELECT 
        household_key,
        ROUND(SUM(sales_value), 2) AS total_spend,
        ROUND(SUM(total_disc_amt), 2) AS total_discounts,
        ROUND(SUM(total_disc_amt) * 100.0 / NULLIF(SUM(gross_shelf_value), 0), 2) AS personal_discount_pct
    FROM fact_transactions
    GROUP BY household_key
)
SELECT 
    c.income_desc,
    COUNT(c.household_key) AS customer_count,
    COUNT(r.household_key) AS redeeming_customers,
    ROUND(COUNT(r.household_key) * 100.0 / COUNT(c.household_key), 2) AS redemption_penetration_pct,
    COALESCE(SUM(r.coupons_redeemed), 0) AS total_coupons_redeemed,
    ROUND(AVG(p.personal_discount_pct), 2) AS avg_discount_reliance_pct,
    ROUND(AVG(p.total_spend), 2) AS avg_household_spend
FROM dim_customer c
LEFT JOIN customer_redemptions r ON c.household_key = r.household_key
LEFT JOIN customer_promotions p ON c.household_key = p.household_key
GROUP BY c.income_desc
ORDER BY redemption_penetration_pct DESC;
