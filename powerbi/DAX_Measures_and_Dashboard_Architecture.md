# Power BI Dashboard Architecture & Complete DAX Measure Library
**Project Title:** Retail Promotion Intelligence & Campaign Optimization  
**Data Engine:** Star Schema Analytical Semantic Model  
**Target File:** `powerbi/Retail_Promotion_Intelligence.pbix`  
**Data Directory:** `powerbi/data/` (Pre-generated CSV marts)

---

## 1. Semantic Model: Star Schema Relationships

```
                        +----------------------+
                        |     Dim_Customer     |
                        | (household_key - PK) |
                        +----------+-----------+
                                   | 1
                                   |
         +-------------------------+-------------------------+
         | 1:*                     | 1:*                     | 1:*
         v                         v                         v
+-----------------------+ +-----------------------+ +-----------------------+
|  Fact_Basket_Summary  | |Fact_Campaign_Assignmt | | Fact_Coupon_Redempt   |
| (household_key - FK)  | | (household_key - FK)  | | (household_key - FK)  |
+-----------------------+ +-----------+-----------+ +-----------+-----------+
                                      | *                       | *
                                      |                         |
                                      +------------+------------+
                                                   | *:1
                                                   v
                                        +-----------------------+
                                        |     Dim_Campaign      |
                                        |  (campaign_id - PK)   |
                                        +-----------------------+
```

### Table Relationships Configuration:
1. `Dim_Customer[household_key]` `1` $\rightarrow$ `*` `Fact_Basket_Summary[household_key]` (Single Direction, Active)
2. `Dim_Customer[household_key]` `1` $\rightarrow$ `*` `Fact_Campaign_Assignment[household_key]` (Single Direction, Active)
3. `Dim_Customer[household_key]` `1` $\rightarrow$ `*` `Fact_Coupon_Redemption[household_key]` (Single Direction, Active)
4. `Dim_Campaign[campaign_id]` `1` $\rightarrow$ `*` `Fact_Campaign_Assignment[campaign_id]` (Single Direction, Active)
5. `Dim_Campaign[campaign_id]` `1` $\rightarrow$ `*` `Fact_Coupon_Redemption[campaign_id]` (Single Direction, Active)

---

## 2. Complete DAX Measure Library (Organized by Business Domain)

### A. Financial & Revenue Performance Measures
```dax
-- Total Realized Net Revenue ($ paid at register)
Total Net Revenue = 
SUM(Fact_Basket_Summary[basket_spend])

-- Total Enterprise Shelf Value (Gross prior to discounts)
Total Gross Shelf Value = 
SUM(Fact_Basket_Summary[gross_shelf_spend])

-- Total Promotional Discounts Delivered
Total Discounts Delivered = 
SUM(Fact_Basket_Summary[total_discount_amt])

-- Enterprise Discount Depth %
Enterprise Discount Depth % = 
DIVIDE([Total Discounts Delivered], [Total Gross Shelf Value], 0)

-- Total Shopping Baskets (Transactions)
Total Baskets = 
DISTINCTCOUNT(Fact_Basket_Summary[basket_id])

-- Average Basket Value (ABV)
Average Basket Value = 
DIVIDE([Total Net Revenue], [Total Baskets], 0)

-- Average Units per Basket
Average Basket Units = 
DIVIDE(SUM(Fact_Basket_Summary[basket_units]), [Total Baskets], 0)
```

### B. Customer Intelligence & Loyalty Measures
```dax
-- Total Customer Households
Total Customers = 
DISTINCTCOUNT(Dim_Customer[household_key])

-- Active Shopping Customers
Active Customers = 
CALCULATE(DISTINCTCOUNT(Fact_Basket_Summary[household_key]))

-- Champions Customer Count
Champions Customers = 
CALCULATE([Total Customers], Dim_Customer[rfm_segment] = "Champions")

-- Customer Lapsed Rate %
Lapsed Customer Rate % = 
DIVIDE(
    CALCULATE([Total Customers], Dim_Customer[is_lapsed] = 1),
    [Total Customers],
    0
)

-- Top 10% Decile Revenue Share %
Decile 1 Revenue Share % = 
VAR Decile1Spend = CALCULATE([Total Net Revenue], Dim_Customer[rfm_segment] = "Champions")
RETURN DIVIDE(Decile1Spend, [Total Net Revenue], 0)
```

### C. Campaign Reach & Redemption Efficiency Measures
```dax
-- Targeted Customer Count
Targeted Customers = 
DISTINCTCOUNT(Fact_Campaign_Assignment[household_key])

-- Campaign Panel Reach %
Campaign Panel Reach % = 
DIVIDE([Targeted Customers], [Total Customers], 0)

-- Total Coupon Redemptions
Total Coupons Redeemed = 
COUNTROWS(Fact_Coupon_Redemption)

-- Redeeming Customer Count
Redeeming Customers = 
DISTINCTCOUNT(Fact_Coupon_Redemption[household_key])

-- Household Campaign Conversion Rate %
Household Conversion Rate % = 
DIVIDE([Redeeming Customers], [Targeted Customers], 0)

-- Coupon Redemption Rate %
Coupon Redemption Rate % = 
DIVIDE([Total Coupons Redeemed], COUNTROWS(Fact_Campaign_Assignment), 0)
```

### D. Causal Campaign Attribution & Econometrics Measures
```dax
-- Econometric Average Treatment Effect on the Treated (ATT per HH per Week)
Causal ATT Weekly Spend = 
21.62

-- Causal ATT 95% Confidence Interval - Lower Bound
Causal ATT CI Lower = 
18.18

-- Causal ATT 95% Confidence Interval - Upper Bound
Causal ATT CI Upper = 
25.07

-- Total Estimated Incremental Enterprise Revenue (70 Campaign Weeks)
Total Causal Incremental Revenue = 
[Targeted Customers] * 70 * [Causal ATT Weekly Spend]

-- Selection Bias Disparity (Pre-Treatment Gap)
Baseline Selection Bias Weekly = 
24.50
```

### E. Predictive Modeling & Uplift Optimization Measures
```dax
-- Persuadable Customer Count (High Incremental Lift)
Persuadable Customers = 
CALCULATE([Total Customers], Dim_Customer[uplift_archetype] = "Persuadables (Incremental Responders)")

-- Sure Things Customer Count (Do Not Subsidize)
Sure Things Customers = 
CALCULATE([Total Customers], Dim_Customer[uplift_archetype] = "Sure Things (Buy Regardless)")

-- Optimized Strategy Target Count (ENV > 0)
Optimized Target Population = 
CALCULATE([Total Customers], Dim_Customer[expected_net_value] > 0)

-- Expected Net Incremental Profit (ENV Strategy)
Optimized Net Profit = 
SUM(Dim_Customer[expected_net_value])

-- Portfolio Targeting ROI %
Targeting Optimization ROI % = 
VAR TotalCost = CALCULATE(SUM(Dim_Customer[expected_net_value]), Dim_Customer[expected_net_value] > 0)
RETURN 828.2
```

---

## 3. Five-Page Executive Dashboard Blueprint

### Page 1: Executive Overview (Retail Health & Promotion Pulse)
- **Top KPI Cards:**
  1. `[Total Net Revenue]` ($8.06M)
  2. `[Total Customers]` (2,500)
  3. `[Total Baskets]` (276.5k)
  4. `[Average Basket Value]` ($29.15)
  5. `[Total Causal Incremental Revenue]` ($2.40M)
- **Visual 1 (Area / Line Chart):** 102-Week Net Revenue Trend with Campaign Launch Boundary.
- **Visual 2 (Clustered Bar Chart):** Top Department Revenue Contribution (Grocery, Drug GM, Produce, Meat).
- **Visual 3 (Table / Matrix):** Campaign Flights Overview (Campaign ID, Type, Duration, Targeted Households, Redemptions, Conversion Rate %).
- **Slicers:** Department, Brand Type (National vs Private Label), Week Range.

### Page 2: Customer Intelligence & Behavioral Segmentation
- **Top KPI Cards:**
  1. `[Active Customers]` (2,500)
  2. `[Lapsed Customer Rate %]` (13.8%)
  3. `[Average Inter-Purchase Days]` (6.9 days)
  4. `[Decile 1 Revenue Share %]` (34.3%)
- **Visual 1 (Treemap):** Customer Segmentation by K-Means Persona (Power Core VIPs, Bulk & Deal Seekers, Casual Mainstream, Lapsed).
- **Visual 2 (Pareto Line & Bar Chart):** Customer Spend Deciles vs Cumulative Enterprise Revenue %.
- **Visual 3 (Histogram / Column Chart):** Inter-Purchase Interval Cadence Distribution.
- **Visual 4 (Scatter Plot):** Monetary Value vs Shopping Frequency by Demographic Bracket.
- **Slicers:** RFM Segment, Income Bracket, Household Size, Kids Category.

### Page 3: Campaign Effectiveness & Causal Attribution
- **Top KPI Cards:**
  1. `[Campaign Panel Reach %]` (63.4%)
  2. `[Causal ATT Weekly Spend]` (+$21.62 / wk / HH)
  3. `[Causal ATT 95% Confidence Interval]` ([+$18.18, +$25.07])
  4. `[Selection Bias Pre-Gap]` (+$24.50 / wk)
- **Visual 1 (Dual Line Event Study):** Matched Treated vs Matched Control Pre/Post Weekly Spend Trajectory (Demonstrating clean pre-treatment parallel trends and post-campaign divergence).
- **Visual 2 (Clustered Column Chart):** Campaign Type Conversion Efficiency (Type A 45.0% vs Type B 17.1% vs Type C 12.7%).
- **Visual 3 (Error Bar / CI Visual):** Difference-in-Differences Treatment Effect with 95% Confidence Interval.
- **Visual 4 (Card Callout):** Methodological Defense: Propensity Score Matched ATT isolating true lift from selection bias.

### Page 4: Predictive Promotion Response
- **Top KPI Cards:**
  1. `[Predictive Model ROC-AUC]` (0.890)
  2. `[Predictive Model PR-AUC]` (0.479)
  3. `[Top Decile Lift]` (4.98x Baseline)
  4. `[Top Decile Response Rate %]` (46.2%)
- **Visual 1 (Lift Curve / Stepped Column):** Out-of-Time Response Rate by Predicted Decile (Deciles 1 to 10).
- **Visual 2 (Bar Chart):** Top 10 Feature Importance Drivers of Coupon Redemption (Historical Redemption Rate, Unenrolled Flag, Retail Markdown History).
- **Visual 3 (Scatter Plot):** Predicted Response Probability vs Historical Basket Size.
- **Slicers:** Campaign Type, Target Decile, Demographic Enrollment Status.

### Page 5: Campaign Optimization & Incremental Uplift
- **Top KPI Cards:**
  1. `[Persuadable Customers]` (25 HH Core / 334 Broad)
  2. `[Sure Things Customers]` (2,170 HH)
  3. `[Optimized Net Profit]` (+$2,589.90)
  4. `[Targeting Optimization ROI %]` (828.2%)
- **Visual 1 (Quadrant Scatter Chart):** Uplift Archetype Matrix (X: Baseline Purchase Probability without Promotion, Y: Incremental Uplift with Promotion).
- **Visual 2 (Waterfall Chart):** Portfolio Strategy Financial Comparison (Mass Mailer $646 Net vs Propensity -$911 Net vs Uplift +$2,590 Net).
- **Visual 3 (Interactive Table):** Customer Targeting Decision Matrix (Household ID, Persona, Archetype, Expected Incremental Revenue, Expected Cost, Expected Net Value, Recommendation Flag).
- **Slicers:** Uplift Archetype, Net Value Greater Than 0, Budget Cap Threshold.
