# Executive SQL Business Analytics & KPI Portfolio Report
**Warehouse Engine:** DuckDB Analytical OLAP Core
**Dataset:** Dunnhumby - The Complete Journey (2,500 Households, 102 Weeks)
**Verification Status:** 100% Executed & Reconciled

---

## 01 Customer Revenue Concentration
**Execution Runtime:** `0.030s` | **Output Rows:** `10`

```sql
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
```

### Query Output Summary Table

|   spend_decile |   customer_count |   min_spend |   max_spend |     decile_spend |   pct_enterprise_spend |   cumulative_pct_spend |
|---------------:|-----------------:|------------:|------------:|-----------------:|-----------------------:|-----------------------:|
|              1 |              250 |     7456.64 |    38319.8  |      2.76301e+06 |                  34.29 |                  34.29 |
|              2 |              250 |     5089.66 |     7447.28 |      1.51118e+06 |                  18.76 |                  53.05 |
|              3 |              250 |     3772.56 |     5082.41 |      1.10285e+06 |                  13.69 |                  66.73 |
|              4 |              250 |     2766.97 |     3772.03 | 804333           |                   9.98 |                  76.72 |
|              5 |              250 |     2158.85 |     2766.7  | 614383           |                   7.63 |                  84.34 |
|              6 |              250 |     1635.21 |     2156.65 | 474330           |                   5.89 |                  90.23 |
|              7 |              250 |     1166.63 |     1634.22 | 346887           |                   4.31 |                  94.53 |
|              8 |              250 |      760.89 |     1165.27 | 241269           |                   2.99 |                  97.53 |
|              9 |              250 |      390.16 |      760.45 | 142852           |                   1.77 |                  99.3  |
|             10 |              250 |        8.17 |      387.34 |  56364.7         |                   0.7  |                 100    |

---

## 02 Department Category Drivers
**Execution Runtime:** `0.187s` | **Output Rows:** `15`

```sql
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
```

### Query Output Summary Table

| department      |   active_products |   total_baskets_penetrated |   total_net_revenue |   revenue_share_pct |   total_retail_discounts |   total_coupon_discounts |   avg_discount_depth_pct |
|:----------------|------------------:|---------------------------:|--------------------:|--------------------:|-------------------------:|-------------------------:|-------------------------:|
| GROCERY         |             39019 |                     215411 |         4.09381e+06 |               50.81 |                817491    |                 29283.7  |                    17.14 |
| DRUG GM         |             31523 |                     118195 |         1.05536e+06 |               13.1  |                104771    |                  7509.87 |                     9.62 |
| PRODUCE         |              3117 |                      89026 |    557452           |                6.92 |                 68384.5  |                   520.64 |                    11    |
| MEAT            |              2544 |                      53401 |    548787           |                6.81 |                176693    |                    63.8  |                    24.36 |
| KIOSK-GAS       |                16 |                      22056 |    544222           |                6.75 |                 17225.4  |                     0    |                     3.07 |
| MEAT-PCKGD      |              2427 |                      58466 |    412437           |                5.12 |                119452    |                  1466.84 |                    22.67 |
| DELI            |              2354 |                      35639 |    260867           |                3.24 |                 22481.2  |                   176.55 |                     7.99 |
| PASTRY          |              2149 |                      30099 |    121740           |                1.51 |                 17578.4  |                    71.75 |                    12.66 |
| MISC SALES TRAN |                88 |                       5992 |    119960           |                1.49 |                  3035.69 |                     0    |                     2.47 |
| NUTRITION       |              2913 |                      16820 |     97669           |                1.21 |                 12202.4  |                   249.61 |                    11.31 |
| SEAFOOD-PCKGD   |               563 |                       8873 |     63093.6         |                0.78 |                 21385.6  |                   249.34 |                    25.53 |
| FLORAL          |               938 |                       3853 |     39653.3         |                0.49 |                  1120.14 |                    79.91 |                     2.94 |
| COSMETICS       |              3007 |                       5166 |     32360.4         |                0.4  |                  7133.86 |                   174.93 |                    18.42 |
| SALAD BAR       |                48 |                       8418 |     30953.3         |                0.38 |                   881.09 |                     0    |                     2.77 |
| SEAFOOD         |               369 |                       3495 |     29496.9         |                0.37 |                  6470.63 |                     0    |                    17.99 |

---

## 03 Top Products Sales Velocity
**Execution Runtime:** `1.243s` | **Output Rows:** `20`

```sql
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
```

### Query Output Summary Table

|   product_id | commodity_desc         | sub_commodity_desc             | department      | brand_type     |   unique_buying_households |   total_baskets |   normalized_units |   total_revenue |   avg_unit_price |   total_promotional_discount |
|-------------:|:-----------------------|:-------------------------------|:----------------|:---------------|---------------------------:|----------------:|-------------------:|----------------:|-----------------:|-----------------------------:|
|      6534178 | COUPON/MISC ITEMS      | GASOLINE-REG UNLEADED          | KIOSK-GAS       | Private Label  |                       1312 |           19820 |              19820 |        503867   |            25.42 |                     17053.9  |
|      6533889 | COUPON/MISC ITEMS      | GASOLINE-REG UNLEADED          | MISC SALES TRAN | Private Label  |                        151 |            1453 |               1453 |         46311.3 |            31.87 |                      1583.99 |
|      1029743 | FLUID MILK PRODUCTS    | FLUID MILK WHITE ONLY          | GROCERY         | Private Label  |                       1385 |           14401 |              16972 |         41072.1 |             2.43 |                      2685.42 |
|      6534166 | COUPON/MISC ITEMS      | GASOLINE-REG UNLEADED          | MISC SALES TRAN | Private Label  |                        189 |            1206 |               1206 |         33594.5 |            27.86 |                      1139.42 |
|      1082185 | TROPICAL FRUIT         | BANANAS                        | PRODUCE         | National Brand |                       2069 |           29756 |              30894 |         29482   |             0.95 |                      2318.64 |
|       916122 | CHICKEN                | CHICKEN BREAST BONELESS        | MEAT            | National Brand |                       1153 |            4404 |               6980 |         28951.9 |             4.31 |                     29928.7  |
|      6533765 | FUEL                   | GASOLINE-REG UNLEADED          | KIOSK-GAS       | Private Label  |                        333 |            1756 |               1756 |         28837.3 |            16.42 |                         0    |
|      1106523 | FLUID MILK PRODUCTS    | FLUID MILK WHITE ONLY          | GROCERY         | Private Label  |                       1037 |            9788 |              11497 |         27818.4 |             2.44 |                      1703.78 |
|       995242 | FLUID MILK PRODUCTS    | FLUID MILK WHITE ONLY          | GROCERY         | Private Label  |                       1462 |           12528 |              21758 |         26502.5 |             1.3  |                     14485.4  |
|      5569230 | SOFT DRINKS            | SOFT DRINKS 12/18&15PK CAN CAR | GROCERY         | National Brand |                        968 |            4832 |               7682 |         23651.6 |             3.27 |                     12950.9  |
|       844179 | BEEF                   | PRIMAL                         | MEAT            | National Brand |                       1131 |            3940 |               5435 |         20154.8 |             3.79 |                      5582.87 |
|      1044078 | BEEF                   | LEAN                           | MEAT            | National Brand |                       1094 |            4053 |               6040 |         18896.4 |             3.25 |                      6163.32 |
|      1127831 | BERRIES                | STRAWBERRIES                   | PRODUCE         | National Brand |                       1259 |            5240 |               7510 |         16786   |             2.37 |                      5469.2  |
|      1133018 | FLUID MILK PRODUCTS    | FLUID MILK WHITE ONLY          | GROCERY         | Private Label  |                       1077 |            7305 |              12318 |         14942.4 |             1.29 |                      8198.08 |
|       874972 | BEEF                   | SELECT BEEF                    | MEAT            | National Brand |                        532 |            1231 |               1628 |         13492.5 |             8.43 |                      2279.69 |
|      1126899 | FLUID MILK PRODUCTS    | FLUID MILK WHITE ONLY          | GROCERY         | Private Label  |                        481 |            4480 |               5495 |         13435.3 |             2.45 |                       805.18 |
|      1005186 | SALAD BAR              | SALAD BAR FRESH FRUIT          | SALAD BAR       | National Brand |                        795 |            4646 |               5260 |         12950.1 |             2.44 |                       395.99 |
|      5569471 | SOFT DRINKS            | SOFT DRINKS 12/18&15PK CAN CAR | GROCERY         | National Brand |                        527 |            2220 |               4356 |         12863.1 |             3.2  |                      7891.97 |
|      1070820 | FLUID MILK PRODUCTS    | FLUID MILK WHITE ONLY          | GROCERY         | Private Label  |                        508 |            4438 |               5163 |         12441.1 |             2.43 |                       827.87 |
|       951590 | BAKED BREAD/BUNS/ROLLS | MAINSTREAM WHITE BREAD         | GROCERY         | National Brand |                        867 |            6125 |               7648 |         12385.3 |             1.62 |                      2506.35 |

---

## 04 Shopping Frequency Interpurchase Time
**Execution Runtime:** `0.048s` | **Output Rows:** `5`

```sql
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
```

### Query Output Summary Table

| shopping_cadence_segment         |   household_count |   pct_households |   group_avg_days_between_trips |   avg_annual_trips |
|:---------------------------------|------------------:|-----------------:|-------------------------------:|-------------------:|
| High Frequency (<= 3 days)       |               184 |             7.36 |                           2.35 |              284.5 |
| Weekly Shoppers (4 - 7 days)     |               773 |            30.92 |                           4.98 |              134.9 |
| Bi-Weekly Shoppers (8 - 14 days) |               705 |            28.2  |                          10.02 |               65.4 |
| Monthly Shoppers (15 - 30 days)  |               529 |            21.16 |                          20.16 |               31.7 |
| Infrequent Shoppers (> 30 days)  |               306 |            12.24 |                          67.06 |               11.6 |

---

## 05 Average Basket Economics
**Execution Runtime:** `0.059s` | **Output Rows:** `5`

```sql
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
```

### Query Output Summary Table

| basket_tier             |   total_baskets |   pct_baskets |   avg_basket_spend |   avg_items_per_basket |   avg_discount_saved |   avg_savings_rate_pct |
|:------------------------|----------------:|--------------:|-------------------:|-----------------------:|---------------------:|-----------------------:|
| Micro Basket (< $10)    |           93450 |         33.8  |               4.72 |                    2.8 |                 0.89 |                  13.83 |
| Convenience ($10 - $25) |           80213 |         29.01 |              16.56 |                    6.8 |                 2.72 |                  12.39 |
| Fill-in ($25 - $50)     |           56751 |         20.53 |              35.13 |                   13   |                 5.86 |                  12.82 |
| Major Shop ($50 - $100) |           31710 |         11.47 |              69.42 |                   30   |                13.64 |                  15.43 |
| Stock-up ($100+)        |           14360 |          5.19 |             145.76 |                   61.6 |                26.65 |                  15.1  |

---

## 06 Campaign Reach And Exposure
**Execution Runtime:** `0.006s` | **Output Rows:** `30`

```sql
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
```

### Query Output Summary Table

|   campaign_id | campaign_type   |   start_day |   end_day |   duration_days |   households_targeted |   panel_reach_pct |   households_redeemed |   total_coupons_redeemed |   household_conversion_rate_pct |
|--------------:|:----------------|------------:|----------:|----------------:|----------------------:|------------------:|----------------------:|-------------------------:|--------------------------------:|
|            18 | TypeA           |         587 |       642 |              56 |                  1133 |             45.32 |                   214 |                      653 |                           18.89 |
|            13 | TypeA           |         504 |       551 |              48 |                  1077 |             43.08 |                   196 |                      629 |                           18.2  |
|             8 | TypeA           |         412 |       460 |              49 |                  1076 |             43.04 |                   158 |                      372 |                           14.68 |
|            30 | TypeA           |         323 |       369 |              47 |                   361 |             14.44 |                    36 |                       64 |                            9.97 |
|            26 | TypeA           |         224 |       264 |              41 |                   332 |             13.28 |                    31 |                       73 |                            9.34 |
|            22 | TypeB           |         624 |       656 |              33 |                   276 |             11.04 |                    17 |                       47 |                            6.16 |
|            20 | TypeC           |         615 |       685 |              71 |                   244 |              9.76 |                    20 |                       33 |                            8.2  |
|            14 | TypeC           |         531 |       596 |              66 |                   224 |              8.96 |                    18 |                       34 |                            8.04 |
|            11 | TypeB           |         477 |       523 |              47 |                   214 |              8.56 |                     6 |                        8 |                            2.8  |
|            17 | TypeB           |         575 |       607 |              33 |                   202 |              8.08 |                    18 |                       45 |                            8.91 |
|             7 | TypeB           |         398 |       432 |              35 |                   198 |              7.92 |                     5 |                        7 |                            2.53 |
|            16 | TypeB           |         561 |       593 |              33 |                   188 |              7.52 |                    19 |                       43 |                           10.11 |
|            25 | TypeB           |         659 |       691 |              33 |                   187 |              7.48 |                    24 |                       61 |                           12.83 |
|            23 | TypeB           |         646 |       684 |              39 |                   183 |              7.32 |                    23 |                       60 |                           12.57 |
|             9 | TypeB           |         435 |       467 |              33 |                   176 |              7.04 |                    20 |                       43 |                           11.36 |
|            12 | TypeB           |         477 |       509 |              33 |                   170 |              6.8  |                    11 |                       26 |                            6.47 |
|             5 | TypeB           |         377 |       411 |              35 |                   166 |              6.64 |                     8 |                       13 |                            4.82 |
|            19 | TypeB           |         603 |       635 |              33 |                   130 |              5.2  |                    15 |                       29 |                           11.54 |
|            10 | TypeB           |         463 |       495 |              33 |                   123 |              4.92 |                    10 |                       15 |                            8.13 |
|            29 | TypeB           |         281 |       334 |              54 |                   118 |              4.72 |                    13 |                       24 |                           11.02 |
|            24 | TypeB           |         659 |       719 |              61 |                   100 |              4    |                     7 |                       10 |                            7    |
|             4 | TypeB           |         372 |       404 |              33 |                    81 |              3.24 |                     6 |                       11 |                            7.41 |
|            21 | TypeB           |         624 |       656 |              33 |                    65 |              2.6  |                     4 |                        5 |                            6.15 |
|             6 | TypeC           |         393 |       425 |              33 |                    65 |              2.6  |                     1 |                        1 |                            1.54 |
|             2 | TypeB           |         351 |       383 |              33 |                    48 |              1.92 |                     2 |                        5 |                            4.17 |
|            15 | TypeC           |         547 |       708 |             162 |                    17 |              0.68 |                     2 |                        2 |                           11.76 |
|            28 | TypeB           |         259 |       320 |              62 |                    17 |              0.68 |                     1 |                        1 |                            5.88 |
|             1 | TypeB           |         346 |       383 |              38 |                    13 |              0.52 |                     1 |                        1 |                            7.69 |
|             3 | TypeC           |         356 |       412 |              57 |                    12 |              0.48 |                     2 |                        2 |                           16.67 |
|            27 | TypeC           |         237 |       300 |              64 |                    12 |              0.48 |                     1 |                        1 |                            8.33 |

---

## 07 Campaign Redemption Performance
**Execution Runtime:** `0.005s` | **Output Rows:** `3`

```sql
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
```

### Query Output Summary Table

| campaign_type   |   total_campaigns |   total_target_impressions |   total_coupons_redeemed |   redeeming_household_instances |   avg_flight_duration_days |   coupon_redemption_rate_pct |   household_response_rate_pct |
|:----------------|------------------:|---------------------------:|-------------------------:|--------------------------------:|---------------------------:|-----------------------------:|------------------------------:|
| TypeA           |                 5 |                       3979 |                     1791 |                             635 |                       48.2 |                        45.01 |                         15.96 |
| TypeB           |                19 |                       2655 |                      454 |                             210 |                       38.6 |                        17.1  |                          7.91 |
| TypeC           |                 6 |                        574 |                       73 |                              44 |                       75.5 |                        12.72 |                          7.67 |

---

## 08 Demographic Promotion Responsiveness
**Execution Runtime:** `0.015s` | **Output Rows:** `13`

```sql
-- ==============================================================================
-- Business Question 08: Demographic Promotion Responsiveness
-- Question: Which demographic brackets (Income, Household Size, Kids) show the
--           highest propensity to redeem coupons and capture promotional discounts?
-- ==============================================================================

WITH customer_redemptions AS (
    SELECT 
        household_key,
        COUNT(coupon_upc) AS coupons_redeemed
    FROM fact_coupon_redemption
    GROUP BY household_key
),
customer_promotions AS (
    SELECT 
        household_key,
        ROUND(SUM(sales_value), 2) AS total_spend,
        ROUND(SUM(total_disc_amt), 2) AS total_discounts,
        ROUND(SUM(total_disc_amt) * 100.0 / NULLIF(SUM(gross_shelf_value), 0), 2) AS personal_discount_pct
    FROM fact_transactions
    GROUP BY household_key
)
SELECT 
    c.income_desc,
    COUNT(c.household_key) AS customer_count,
    COUNT(r.household_key) AS redeeming_customers,
    ROUND(COUNT(r.household_key) * 100.0 / COUNT(c.household_key), 2) AS redemption_penetration_pct,
    COALESCE(SUM(r.coupons_redeemed), 0) AS total_coupons_redeemed,
    ROUND(AVG(p.personal_discount_pct), 2) AS avg_discount_reliance_pct,
    ROUND(AVG(p.total_spend), 2) AS avg_household_spend
FROM dim_customer c
LEFT JOIN customer_redemptions r ON c.household_key = r.household_key
LEFT JOIN customer_promotions p ON c.household_key = p.household_key
GROUP BY c.income_desc
ORDER BY redemption_penetration_pct DESC;
```

### Query Output Summary Table

| income_desc   |   customer_count |   redeeming_customers |   redemption_penetration_pct |   total_coupons_redeemed |   avg_discount_reliance_pct |   avg_household_spend |
|:--------------|-----------------:|----------------------:|-----------------------------:|-------------------------:|----------------------------:|----------------------:|
| 150-174K      |               30 |                    19 |                        63.33 |                      129 |                       12.89 |               8394.84 |
| 125-149K      |               38 |                    20 |                        52.63 |                      119 |                       13.79 |               7912.06 |
| 50-74K        |              192 |                    89 |                        46.35 |                      640 |                       15.34 |               5702.35 |
| 175-199K      |               11 |                     5 |                        45.45 |                       21 |                       11.86 |               8548.46 |
| 100-124K      |               34 |                    14 |                        41.18 |                       46 |                       13.85 |               5927.74 |
| 25-34K        |               77 |                    28 |                        36.36 |                      145 |                       16.58 |               4938.07 |
| Under 15K     |               61 |                    22 |                        36.07 |                      128 |                       16.46 |               5559.61 |
| 75-99K        |               96 |                    34 |                        35.42 |                      289 |                       15.11 |               5822.53 |
| 35-49K        |              172 |                    59 |                        34.3  |                      252 |                       16.3  |               4802.01 |
| 15-24K        |               74 |                    18 |                        24.32 |                       80 |                       16.13 |               4097.12 |
| 200-249K      |                5 |                     1 |                        20    |                        4 |                       10.8  |               5726.49 |
| 250K+         |               11 |                     2 |                        18.18 |                        3 |                       11.06 |              10789.9  |
| UNENROLLED    |             1699 |                   123 |                         7.24 |                      462 |                       15.75 |               2095.2  |

---

## 09 Promotion Depth Vs Basket Value
**Execution Runtime:** `0.057s` | **Output Rows:** `5`

```sql
-- ==============================================================================
-- Business Question 09: Promotion Depth vs. Basket Spend Elasticity
-- Question: Does deeper promotional discount depth correlate with larger market
--           basket sizes, or does it merely subsidize existing shopper spend?
-- ==============================================================================

WITH basket_discount_bins AS (
    SELECT 
        basket_id,
        household_key,
        SUM(sales_value) AS net_spend,
        SUM(CASE WHEN is_fuel = FALSE THEN quantity ELSE 1 END) AS total_units,
        SUM(total_disc_amt) AS total_discounts,
        SUM(gross_shelf_value) AS gross_spend,
        CASE 
            WHEN SUM(gross_shelf_value) = 0 THEN 0.0
            ELSE SUM(total_disc_amt) / SUM(gross_shelf_value)
        END AS discount_depth
    FROM fact_transactions
    GROUP BY basket_id, household_key
)
SELECT 
    CASE 
        WHEN discount_depth = 0 THEN '01. Full Price (0% Disc)'
        WHEN discount_depth < 0.10 THEN '02. Light Disc (0 - 10%)'
        WHEN discount_depth < 0.20 THEN '03. Moderate (10 - 20%)'
        WHEN discount_depth < 0.35 THEN '04. Deep Disc (20 - 35%)'
        ELSE '05. Extreme Disc (> 35%)'
    END AS discount_tier,
    COUNT(basket_id) AS total_baskets,
    ROUND(COUNT(basket_id) * 100.0 / (SELECT COUNT(*) FROM basket_discount_bins), 2) AS pct_baskets,
    ROUND(AVG(net_spend), 2) AS avg_net_basket_spend,
    ROUND(AVG(gross_spend), 2) AS avg_gross_shelf_spend,
    ROUND(AVG(total_units), 1) AS avg_units_per_basket,
    ROUND(AVG(total_discounts), 2) AS avg_discounts_given
FROM basket_discount_bins
GROUP BY 1
ORDER BY 1 ASC;
```

### Query Output Summary Table

| discount_tier            |   total_baskets |   pct_baskets |   avg_net_basket_spend |   avg_gross_shelf_spend |   avg_units_per_basket |   avg_discounts_given |
|:-------------------------|----------------:|--------------:|-----------------------:|------------------------:|-----------------------:|----------------------:|
| 01. Full Price (0% Disc) |           45445 |         16.44 |                   8.86 |                    8.86 |                    2.6 |                  0    |
| 02. Light Disc (0 - 10%) |           80792 |         29.22 |                  30.45 |                   32.28 |                    8.9 |                  1.83 |
| 03. Moderate (10 - 20%)  |           78500 |         28.39 |                  41.94 |                   49.25 |                   19.3 |                  7.31 |
| 04. Deep Disc (20 - 35%) |           55667 |         20.13 |                  30.35 |                   40.65 |                   16.2 |                 10.3  |
| 05. Extreme Disc (> 35%) |           16080 |          5.82 |                  13.23 |                   22.79 |                    7.9 |                  9.56 |

---

## 10 Market Basket Co Occurrence
**Execution Runtime:** `0.202s` | **Output Rows:** `15`

```sql
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
```

### Query Output Summary Table

| department_a   | department_b   |   co_purchase_baskets |   basket_penetration_pct |
|:---------------|:---------------|----------------------:|-------------------------:|
| DRUG GM        | GROCERY        |                 95238 |                    34.45 |
| GROCERY        | PRODUCE        |                 84148 |                    30.44 |
| GROCERY        | MEAT-PCKGD     |                 56772 |                    20.53 |
| GROCERY        | MEAT           |                 51347 |                    18.57 |
| DRUG GM        | PRODUCE        |                 45860 |                    16.59 |
| MEAT           | PRODUCE        |                 35640 |                    12.89 |
| MEAT-PCKGD     | PRODUCE        |                 35073 |                    12.69 |
| DELI           | GROCERY        |                 32049 |                    11.59 |
| DRUG GM        | MEAT-PCKGD     |                 30948 |                    11.19 |
| DRUG GM        | MEAT           |                 27554 |                     9.97 |
| GROCERY        | PASTRY         |                 26903 |                     9.73 |
| MEAT           | MEAT-PCKGD     |                 26093 |                     9.44 |
| DELI           | PRODUCE        |                 20612 |                     7.46 |
| DELI           | DRUG GM        |                 17984 |                     6.5  |
| PASTRY         | PRODUCE        |                 16279 |                     5.89 |

---

## 11 Brand Cannibalization Private Label
**Execution Runtime:** `0.257s` | **Output Rows:** `2`

```sql
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
```

### Query Output Summary Table

| brand_type     |   active_sku_count |   buying_households |   household_penetration_pct |   basket_count |   total_units_sold |   total_revenue |   revenue_share_pct |   total_discount_given |   discount_depth_pct |   avg_realized_unit_price |
|:---------------|-------------------:|--------------------:|----------------------------:|---------------:|-------------------:|----------------:|--------------------:|-----------------------:|---------------------:|--------------------------:|
| National Brand |              78525 |                2500 |                      100    |         238309 |        2.40179e+06 |     5.8202e+06  |               72.23 |            1.10803e+06 |                15.99 |                      2.42 |
| Private Label  |              13814 |                2496 |                       99.84 |         195721 |   976195           |     2.23726e+06 |               27.77 |       340501           |                13.21 |                      2.29 |

---

## 12 Store Causal Stimuli Impact
**Execution Runtime:** `0.925s` | **Output Rows:** `4`

```sql
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
```

### Query Output Summary Table

| marketing_stimuli_tier         |   observed_store_product_weeks |   avg_weekly_spend_per_sku |   avg_weekly_units_per_sku |   total_realized_revenue |
|:-------------------------------|-------------------------------:|---------------------------:|---------------------------:|-------------------------:|
| Base Shelf (No Stimuli)        |                        1850955 |                       3.45 |                        1.4 |              6.37769e+06 |
| Print Mailer Only              |                         246268 |                       3.38 |                        1.7 |         833296           |
| Feature Display + Print Mailer |                         103920 |                       3.07 |                        1.8 |         319384           |
| Feature Display Only           |                         133132 |                       3.04 |                        1.5 |         405071           |

---

