-- ==============================================================================
-- Business Question 03: Top Products & Sales Velocity
-- Question: Which individual products generate the highest sales volume and spend,
--           and what is the split between Private Label and National Brands?
-- ==============================================================================

SELECT 
    t.product_id,
    p.commodity_desc,
    p.sub_commodity_desc,
    p.department,
    p.brand_type,
    COUNT(DISTINCT t.household_key) AS unique_buying_households,
    COUNT(DISTINCT t.basket_id) AS total_baskets,
    SUM(CASE WHEN t.is_fuel = FALSE THEN t.quantity ELSE 1 END) AS normalized_units,
    ROUND(SUM(t.sales_value), 2) AS total_revenue,
    ROUND(AVG(t.sales_value / NULLIF(CASE WHEN t.is_fuel = FALSE THEN t.quantity ELSE 1 END, 0)), 2) AS avg_unit_price,
    ROUND(SUM(t.total_disc_amt), 2) AS total_promotional_discount
FROM fact_transactions t
JOIN dim_product p ON t.product_id = p.product_id
WHERE t.sales_value > 0
GROUP BY t.product_id, p.commodity_desc, p.sub_commodity_desc, p.department, p.brand_type
ORDER BY total_revenue DESC
LIMIT 20;
