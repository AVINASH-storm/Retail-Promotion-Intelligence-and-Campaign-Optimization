-- ==============================================================================
-- Business Question 10: Market Basket Cross-Department Co-Occurrence
-- Question: Which merchandise departments are most frequently purchased together
--           in the same transaction basket, revealing cross-selling opportunities?
-- ==============================================================================

WITH basket_departments AS (
    SELECT DISTINCT
        t.basket_id,
        p.department
    FROM fact_transactions t
    JOIN dim_product p ON t.product_id = p.product_id
    WHERE p.department NOT IN ('UNMAPPED', 'MISC SALES TRAN', 'COUP/STR & MFG')
),
pairs AS (
    SELECT 
        b1.department AS department_a,
        b2.department AS department_b,
        COUNT(b1.basket_id) AS co_purchase_baskets
    FROM basket_departments b1
    JOIN basket_departments b2 
      ON b1.basket_id = b2.basket_id 
     AND b1.department < b2.department
    GROUP BY b1.department, b2.department
),
total_baskets AS (
    SELECT COUNT(DISTINCT basket_id) AS total_txns FROM fact_transactions
)
SELECT 
    p.department_a,
    p.department_b,
    p.co_purchase_baskets,
    ROUND(p.co_purchase_baskets * 100.0 / t.total_txns, 2) AS basket_penetration_pct
FROM pairs p, total_baskets t
ORDER BY p.co_purchase_baskets DESC
LIMIT 15;
