-- ==============================================================================
-- Business Question 07: Campaign Redemption Efficiency by Campaign Type
-- Question: How do the three campaign types (Type A, Type B, Type C) compare in
--           terms of conversion rate, coupon intensity, and redemption velocity?
-- ==============================================================================

WITH camp_targets AS (
    SELECT 
        campaign_id,
        COUNT(DISTINCT household_key) AS unique_households_targeted,
        COUNT(*) AS total_assignments
    FROM fact_campaign_assignment
    GROUP BY campaign_id
),
camp_redempts AS (
    SELECT 
        campaign_id,
        COUNT(DISTINCT household_key) AS unique_redeeming_households,
        COUNT(coupon_upc) AS total_coupons_redeemed
    FROM fact_coupon_redemption
    GROUP BY campaign_id
),
campaign_stats AS (
    SELECT 
        c.campaign_type,
        COUNT(DISTINCT c.campaign_id) AS total_campaigns,
        SUM(COALESCE(t.total_assignments, 0)) AS total_target_impressions,
        SUM(COALESCE(r.total_coupons_redeemed, 0)) AS total_coupons_redeemed,
        SUM(COALESCE(r.unique_redeeming_households, 0)) AS redeeming_household_instances,
        ROUND(AVG(c.duration_days), 1) AS avg_flight_duration_days
    FROM dim_campaign c
    LEFT JOIN camp_targets t ON c.campaign_id = t.campaign_id
    LEFT JOIN camp_redempts r ON c.campaign_id = r.campaign_id
    GROUP BY c.campaign_type
)
SELECT 
    campaign_type,
    total_campaigns,
    total_target_impressions,
    total_coupons_redeemed,
    redeeming_household_instances,
    avg_flight_duration_days,
    ROUND(total_coupons_redeemed * 100.0 / NULLIF(total_target_impressions, 0), 2) AS coupon_redemption_rate_pct,
    ROUND(redeeming_household_instances * 100.0 / NULLIF(total_target_impressions, 0), 2) AS household_response_rate_pct
FROM campaign_stats
ORDER BY coupon_redemption_rate_pct DESC;
