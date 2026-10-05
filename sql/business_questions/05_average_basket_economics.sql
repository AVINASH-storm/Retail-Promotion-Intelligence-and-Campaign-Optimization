-- ==============================================================================
-- Business Question 05: Market Basket Economics
-- Question: What is the distribution of basket spend, item counts, and savings rate
--           across transactions, and how do they differ by store?
-- ==============================================================================

WITH basket_metrics AS (
    SELECT 
        basket_id,
        household_key,
        store_id,
        COUNT(DISTINCT product_id) AS distinct_items,
        SUM(CASE WHEN is_fuel = FALSE THEN quantity ELSE 1 END) AS total_items,
        SUM(sales_value) AS basket_spend,
        SUM(total_disc_amt) AS total_discounts,
        SUM(gross_shelf_value) AS gross_spend
    FROM fact_transactions
    GROUP BY basket_id, household_key, store_id
)
SELECT 
    CASE 
        WHEN basket_spend < 10 THEN 'Micro Basket (< $10)'
        WHEN basket_spend < 25 THEN 'Convenience ($10 - $25)'
        WHEN basket_spend < 50 THEN 'Fill-in ($25 - $50)'
        WHEN basket_spend < 100 THEN 'Major Shop ($50 - $100)'
        ELSE 'Stock-up ($100+)'
    END AS basket_tier,
    COUNT(basket_id) AS total_baskets,
    ROUND(COUNT(basket_id) * 100.0 / (SELECT COUNT(*) FROM basket_metrics), 2) AS pct_baskets,
    ROUND(AVG(basket_spend), 2) AS avg_basket_spend,
    ROUND(AVG(total_items), 1) AS avg_items_per_basket,
    ROUND(AVG(total_discounts), 2) AS avg_discount_saved,
    ROUND(AVG(total_discounts * 100.0 / NULLIF(gross_spend, 0)), 2) AS avg_savings_rate_pct
FROM basket_metrics
GROUP BY 1
ORDER BY avg_basket_spend ASC;
