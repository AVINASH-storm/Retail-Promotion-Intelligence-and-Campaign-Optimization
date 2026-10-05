-- ==============================================================================
-- Business Question 02: Department & Commodity Revenue Drivers
-- Question: Which merchandise departments and commodity categories drive 
--           the bulk of revenue, unit movement, and promotional discounts?
-- ==============================================================================

SELECT 
    p.department,
    COUNT(DISTINCT t.product_id) AS active_products,
    COUNT(DISTINCT t.basket_id) AS total_baskets_penetrated,
    ROUND(SUM(t.sales_value), 2) AS total_net_revenue,
    ROUND(SUM(t.sales_value) * 100.0 / SUM(SUM(t.sales_value)) OVER (), 2) AS revenue_share_pct,
    ROUND(SUM(t.retail_disc_amt), 2) AS total_retail_discounts,
    ROUND(SUM(t.coupon_disc_amt + t.coupon_match_disc_amt), 2) AS total_coupon_discounts,
    ROUND(
        SUM(t.total_disc_amt) * 100.0 / 
        NULLIF(SUM(t.gross_shelf_value), 0), 2
    ) AS avg_discount_depth_pct
FROM fact_transactions t
JOIN dim_product p ON t.product_id = p.product_id
GROUP BY p.department
ORDER BY total_net_revenue DESC
LIMIT 15;
