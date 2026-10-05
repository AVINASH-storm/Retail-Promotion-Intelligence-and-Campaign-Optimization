-- ==============================================================================
-- Business Question 06: Campaign Reach & Target Saturation
-- Question: Which campaigns reached the highest number of households, how long did
--           they run, and what is the distribution of campaign exposure per household?
-- ==============================================================================

SELECT 
    c.campaign_id,
    c.campaign_type,
    c.start_day,
    c.end_day,
    c.duration_days,
    c.households_targeted,
    ROUND(c.households_targeted * 100.0 / 2500, 2) AS panel_reach_pct,
    COUNT(DISTINCT r.household_key) AS households_redeemed,
    COUNT(r.coupon_upc) AS total_coupons_redeemed,
    ROUND(COUNT(DISTINCT r.household_key) * 100.0 / NULLIF(c.households_targeted, 0), 2) AS household_conversion_rate_pct
FROM dim_campaign c
LEFT JOIN fact_coupon_redemption r ON c.campaign_id = r.campaign_id
GROUP BY c.campaign_id, c.campaign_type, c.start_day, c.end_day, c.duration_days, c.households_targeted
ORDER BY c.households_targeted DESC;
