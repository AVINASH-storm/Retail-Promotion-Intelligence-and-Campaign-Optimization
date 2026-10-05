# Incremental Uplift Modeling & Campaign Business Value Optimization
**Dataset:** Dunnhumby - The Complete Journey (2,500 Households)
**Methodology:** T-Learner Quasi-Experimental Uplift Engine & Financial Net Value Optimization
**Key Distinction:** Propensity Modeling vs. Incremental Uplift Targeting

---

## 1. Propensity Model vs. Uplift Model: The Core Differentiator

| Analytical Dimension | Traditional Propensity Model | Incremental Uplift Model |
| :--- | :--- | :--- |
| **Fundamental Question** | *"Who is most likely to buy with a promotion?"* | *"Who will buy BECAUSE we give them a promotion?"* |
| **Mathematical Target** | $P(Y = 1 \mid X, T = 1)$ | $\tau(X) = P(Y = 1 \mid X, T = 1) - P(Y = 1 \mid X, T = 0)$ |
| **Targeting Flaw** | Directs massive discounts to **Sure Things** (VIP customers who would buy full-price anyway). | Isolates **Persuadables**, eliminating pure margin cannibalization. |
| **Financial Outcome** | High gross response, low incremental net ROI. | Maximized Net Incremental Profit and capital efficiency. |

---

## 2. Customer Breakdown into the 4 Strategic Uplift Archetypes

| Strategic Archetype | Customer Count | Share (%) | Avg Baseline Prob | Avg Uplift ($\\hat{\\tau}$) | Recommended Strategic Action |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Lost Causes (Unresponsive)** | 223 | 8.92% | 5.4% | **-3.38%** | Target only if net value is strictly positive |
| **Marginal / Low Impact** | 7 | 0.28% | 46.3% | **+2.77%** | Target only if net value is strictly positive |
| **Persuadables (Incremental Responders)** | 25 | 1.00% | 74.0% | **+9.58%** | Target only if net value is strictly positive |
| **Sleeping Dogs (Negative Lift)** | 75 | 3.00% | 38.2% | **-19.24%** | Target only if net value is strictly positive |
| **Sure Things (Buy Regardless)** | 2,170 | 86.80% | 97.0% | **-1.33%** | Target only if net value is strictly positive |

---

## 3. Financial Portfolio Strategy Comparison

Using realistic retail economics (Gross Margin: **28%**, Mailer Cost: **$0.75**, Avg Coupon Subsidy: **$2.50**):

| Targeting Strategy | Target Households | Total Cost ($) | Incremental Revenue ($) | Gross Profit ($) | Net Profit ($) | Campaign ROI (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Mass Campaign (Target All)** | 2,500 | $2,504.24 | $11,252.42 | $3,150.68 | **$646.44** | **25.8%** |
| **2. Propensity Targeting (Top 35%)** | 875 | $994.49 | $296.49 | $83.02 | **$-911.47** | **-91.7%** |
| **3. Uplift Optimization (ENV > 0)** | 334 | $312.72 | $10,366.32 | $2,902.57 | **$2,589.85** | **828.2%** |
| **4. Budget-Constrained Optimal ($2,000 Cap)** | 334 | $312.72 | $10,366.32 | $2,902.57 | **$2,589.85** | **828.2%** |

---

## 4. Key Strategic Recommendations
1. **Stop Subsidizing 'Sure Things':**
   Traditional marketing teams frequently celebrate high response rates on VIP shoppers. Our uplift analysis proves that targeting Sure Things cannibalizes base margin with near-zero incremental trip volume.
2. **Prioritize High-Margin Persuadables:**
   Uplift targeting delivers **over 3x higher marketing ROI** compared to blanket mass marketing by eliminating mailer waste and coupon leakage on unresponsive households.
