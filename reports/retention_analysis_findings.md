# Customer Retention & Survival Analysis Report
**Dataset:** Dunnhumby - The Complete Journey (2,500 Households, 711 Days)
**Focus:** Empirical Inter-Purchase Timing, Defensible Churn Thresholds, and Survival Dynamics

---

## 1. Empirical Inter-Purchase Time Distribution

In grocery retail, defining churn arbitrarily (e.g. "no purchase in 30 days") is methodologically flawed because shopping cadence varies widely across households. 
We extracted all **276,484 shopping trips** and computed the exact consecutive day intervals between visits:

| Metric | Empirical Value | Business Interpretation |
| :--- | :--- | :--- |
| **Mean Interval** | **6.94 days** | Average duration between store visits |
| **Median Interval (p50)** | **3.0 days** | 50% of shopping trips happen within 3.0 days |
| **75th Percentile (p75)** | **7.0 days** | Weekly / Bi-weekly replenishment threshold |
| **90th Percentile (p90)** | **14.0 days** | 90% of repeat store visits occur within 14.0 days |
| **95th Percentile (p95)** | **22.0 days** | Statistical boundary of normal shopping behavior |
| **99th Percentile (p99)** | **61.0 days** | Extreme replenishment boundary |

### Defensible Churn / Lapse Definition:
> A customer is classified as **Lapsed / Inactive** if their recency at the end of the evaluation window exceeds **45 days** (>= 97th percentile of normal return cadence). At 45 days, the empirical probability that an active customer has not returned purely by chance is under **3%**.

---

## 2. Retention & Lapse Rates by Customer Persona

| Customer Persona | Total Households | Lapsed Households | Lapse Rate (%) | Avg Recency (Days) | Avg Lifetime Spend ($) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Bulk & Deal Seekers (High Basket Value & Disc)** | 637 | 134 | **21.04%** | 32.3 | $1,984.84 |
| **Casual Mainstream (Moderate Frequency)** | 641 | 4 | **0.62%** | 5.6 | $1,846.27 |
| **Lapsed & Low Engagement (High Recency, Low Spend)** | 416 | 201 | **48.32%** | 87.9 | $368.93 |
| **Power Core VIPs (High Spend & Frequency)** | 806 | 6 | **0.74%** | 4.0 | $6,769.46 |

---

## 3. Targeted Campaign vs. Non-Targeted Holdout Lapse Dynamics

| Cohort Group | Total Households | Lapsed Households | Lapse Rate (%) | Avg Recency (Days) | Avg Total Spend ($) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Non-Targeted (Control Pool)** | 916 | 247 | **26.97%** | 48.8 | $1,028.54 |
| **Campaign Targeted** | 1,584 | 98 | **6.19%** | 12.2 | $4,491.99 |

---

## 4. Key Strategic Insights
1. **Targeted vs Non-Targeted Disparity:**
   Targeted customers show dramatically lower lapse rates than non-targeted customers. However, as demonstrated in our causal analysis, this is heavily influenced by **targeting selection bias**—the retailer prioritized active, frequent shoppers for campaign mailers.
2. **At-Risk Interventions:**
   Customers exceeding **25–35 days without a trip** enter the danger zone where return probability drops sharply. Retention re-engagement coupons should be triggered at Day 28, not Day 60, before shopping habits are permanently lost to competitors.
