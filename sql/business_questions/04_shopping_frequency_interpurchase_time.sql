-- ==============================================================================
-- Business Question 04: Shopping Frequency & Inter-Purchase Time (Cadence)
-- Question: How frequently do customers visit the store, and what is the distribution
--           of inter-purchase days between consecutive shopping trips?
-- ==============================================================================

WITH trip_events AS (
    SELECT DISTINCT
        household_key,
        day
    FROM fact_transactions
),
trip_lags AS (
    SELECT 
        household_key,
        day,
        LAG(day) OVER (PARTITION BY household_key ORDER BY day) AS prev_day,
        day - LAG(day) OVER (PARTITION BY household_key ORDER BY day) AS days_between_trips
    FROM trip_events
),
customer_cadence AS (
    SELECT 
        household_key,
        COUNT(day) AS total_shopping_days,
        ROUND(AVG(days_between_trips), 2) AS avg_days_between_trips,
        MEDIAN(days_between_trips) AS median_days_between_trips,
        MIN(days_between_trips) AS min_days_between_trips,
        MAX(days_between_trips) AS max_days_between_trips
    FROM trip_lags
    WHERE days_between_trips IS NOT NULL
    GROUP BY household_key
)
SELECT 
    CASE 
        WHEN avg_days_between_trips <= 3 THEN 'High Frequency (<= 3 days)'
        WHEN avg_days_between_trips <= 7 THEN 'Weekly Shoppers (4 - 7 days)'
        WHEN avg_days_between_trips <= 14 THEN 'Bi-Weekly Shoppers (8 - 14 days)'
        WHEN avg_days_between_trips <= 30 THEN 'Monthly Shoppers (15 - 30 days)'
        ELSE 'Infrequent Shoppers (> 30 days)'
    END AS shopping_cadence_segment,
    COUNT(household_key) AS household_count,
    ROUND(COUNT(household_key) * 100.0 / 2500, 2) AS pct_households,
    ROUND(AVG(avg_days_between_trips), 2) AS group_avg_days_between_trips,
    ROUND(AVG(total_shopping_days), 1) AS avg_annual_trips
FROM customer_cadence
GROUP BY 1
ORDER BY group_avg_days_between_trips ASC;
