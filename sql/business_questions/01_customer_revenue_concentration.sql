-- ==============================================================================
-- Business Question 01: Customer Revenue Concentration & Pareto Analysis
-- Question: Which customers generate the most revenue, and what percentage
--           of total enterprise revenue is driven by the top 10% of customers?
-- ==============================================================================

WITH customer_spend AS (
    SELECT 
        household_key,
        ROUND(SUM(sales_value), 2) AS total_spend,
        COUNT(DISTINCT basket_id) AS total_baskets,
        ROUND(SUM(sales_value) / NULLIF(COUNT(DISTINCT basket_id), 0), 2) AS avg_basket_value
    FROM fact_transactions
    GROUP BY household_key
),
ranked_customers AS (
    SELECT 
        household_key,
        total_spend,
        total_baskets,
        avg_basket_value,
        NTILE(10) OVER (ORDER BY total_spend DESC) AS spend_decile,
        SUM(total_spend) OVER (ORDER BY total_spend DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_spend,
        SUM(total_spend) OVER () AS enterprise_spend
    FROM customer_spend
)
SELECT 
    spend_decile,
    COUNT(household_key) AS customer_count,
    ROUND(MIN(total_spend), 2) AS min_spend,
    ROUND(MAX(total_spend), 2) AS max_spend,
    ROUND(SUM(total_spend), 2) AS decile_spend,
    ROUND(SUM(total_spend) * 100.0 / enterprise_spend, 2) AS pct_enterprise_spend,
    ROUND(MAX(cumulative_spend) * 100.0 / enterprise_spend, 2) AS cumulative_pct_spend
FROM ranked_customers
GROUP BY spend_decile, enterprise_spend
ORDER BY spend_decile ASC;
