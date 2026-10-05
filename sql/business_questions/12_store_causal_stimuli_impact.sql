-- ==============================================================================
-- Business Question 12: In-Store Causal Stimuli Impact (Display vs Mailer)
-- Question: In the 115 instrumented stores, what is the observable sales lift
--           when products are supported by in-store displays, print mailers, or both?
-- ==============================================================================

WITH weekly_product_sales AS (
    SELECT 
        t.store_id,
        t.product_id,
        t.week_no,
        SUM(t.sales_value) AS weekly_spend,
        SUM(CASE WHEN t.is_fuel = FALSE THEN t.quantity ELSE 1 END) AS weekly_units
    FROM fact_transactions t
    JOIN dim_store s ON t.store_id = s.store_id
    WHERE s.has_causal_tracking = TRUE
    GROUP BY t.store_id, t.product_id, t.week_no
),
stimuli_performance AS (
    SELECT 
        COALESCE(c.has_display, 0) AS has_display,
        COALESCE(c.has_mailer, 0) AS has_mailer,
        w.weekly_spend,
        w.weekly_units
    FROM weekly_product_sales w
    LEFT JOIN causal_lookup c 
      ON w.product_id = c.product_id 
     AND w.store_id = c.store_id 
     AND w.week_no = c.week_no
)
SELECT 
    CASE 
        WHEN has_display = 1 AND has_mailer = 1 THEN 'Feature Display + Print Mailer'
        WHEN has_display = 1 AND has_mailer = 0 THEN 'Feature Display Only'
        WHEN has_display = 0 AND has_mailer = 1 THEN 'Print Mailer Only'
        ELSE 'Base Shelf (No Stimuli)'
    END AS marketing_stimuli_tier,
    COUNT(*) AS observed_store_product_weeks,
    ROUND(AVG(weekly_spend), 2) AS avg_weekly_spend_per_sku,
    ROUND(AVG(weekly_units), 1) AS avg_weekly_units_per_sku,
    ROUND(SUM(weekly_spend), 2) AS total_realized_revenue
FROM stimuli_performance
GROUP BY 1
ORDER BY avg_weekly_spend_per_sku DESC;
