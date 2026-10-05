-- ==============================================================================
-- Business Question 09: Promotion Depth vs. Basket Spend Elasticity
-- Question: Does deeper promotional discount depth correlate with larger market
--           basket sizes, or does it merely subsidize existing shopper spend?
-- ==============================================================================

WITH basket_discount_bins AS (
    SELECT 
        basket_id,
        household_key,
        SUM(sales_value) AS net_spend,
        SUM(CASE WHEN is_fuel = FALSE THEN quantity ELSE 1 END) AS total_units,
        SUM(total_disc_amt) AS total_discounts,
        SUM(gross_shelf_value) AS gross_spend,
        CASE 
            WHEN SUM(gross_shelf_value) = 0 THEN 0.0
            ELSE SUM(total_disc_amt) / SUM(gross_shelf_value)
        END AS discount_depth
    FROM fact_transactions
    GROUP BY basket_id, household_key
)
SELECT 
    CASE 
        WHEN discount_depth = 0 THEN '01. Full Price (0% Disc)'
        WHEN discount_depth < 0.10 THEN '02. Light Disc (0 - 10%)'
        WHEN discount_depth < 0.20 THEN '03. Moderate (10 - 20%)'
        WHEN discount_depth < 0.35 THEN '04. Deep Disc (20 - 35%)'
        ELSE '05. Extreme Disc (> 35%)'
    END AS discount_tier,
    COUNT(basket_id) AS total_baskets,
    ROUND(COUNT(basket_id) * 100.0 / (SELECT COUNT(*) FROM basket_discount_bins), 2) AS pct_baskets,
    ROUND(AVG(net_spend), 2) AS avg_net_basket_spend,
    ROUND(AVG(gross_spend), 2) AS avg_gross_shelf_spend,
    ROUND(AVG(total_units), 1) AS avg_units_per_basket,
    ROUND(AVG(total_discounts), 2) AS avg_discounts_given
FROM basket_discount_bins
GROUP BY 1
ORDER BY 1 ASC;
