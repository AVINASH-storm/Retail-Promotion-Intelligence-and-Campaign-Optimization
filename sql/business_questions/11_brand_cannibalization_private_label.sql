-- ==============================================================================
-- Business Question 11: Brand Tier Economics (Private Label vs. National Brand)
-- Question: How do Private Label (store brand) products compare to National Brands
--           in revenue volume, basket penetration, and margin discount reliance?
-- ==============================================================================

SELECT 
    p.brand_type,
    COUNT(DISTINCT t.product_id) AS active_sku_count,
    COUNT(DISTINCT t.household_key) AS buying_households,
    ROUND(COUNT(DISTINCT t.household_key) * 100.0 / 2500, 2) AS household_penetration_pct,
    COUNT(DISTINCT t.basket_id) AS basket_count,
    SUM(CASE WHEN t.is_fuel = FALSE THEN t.quantity ELSE 1 END) AS total_units_sold,
    ROUND(SUM(t.sales_value), 2) AS total_revenue,
    ROUND(SUM(t.sales_value) * 100.0 / SUM(SUM(t.sales_value)) OVER (), 2) AS revenue_share_pct,
    ROUND(SUM(t.total_disc_amt), 2) AS total_discount_given,
    ROUND(
        SUM(t.total_disc_amt) * 100.0 / NULLIF(SUM(t.gross_shelf_value), 0), 2
    ) AS discount_depth_pct,
    ROUND(
        SUM(t.sales_value) / NULLIF(SUM(CASE WHEN t.is_fuel = FALSE THEN t.quantity ELSE 1 END), 0), 2
    ) AS avg_realized_unit_price
FROM fact_transactions t
JOIN dim_product p ON t.product_id = p.product_id
GROUP BY p.brand_type
ORDER BY total_revenue DESC;
