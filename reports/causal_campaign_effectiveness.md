# Causal Campaign Effectiveness & Econometric Attribution Report
**Dataset:** Dunnhumby - The Complete Journey (2,500 Households, 102 Weeks)
**Methodology:** Propensity Score Matching (PSM) + Difference-in-Differences (DiD) Econometrics
**Scientific Status:** Validated Quasi-Experiment with Selection Bias Correction and Parallel Trends Check

---

## 1. Executive Summary & Causal Answers

| Question | Naive / Observational Answer | Econometric Causal Answer | Methodological Defense |
| :--- | :---: | :---: | :--- |
| **Did targeted households spend more?** | **Yes, +$38.28 / week** | **Yes, +$38.28 / week** | Descriptive correlation. |
| **Did campaigns CAUSE additional spending?** | Claimed +$38.28/wk (Biased) | **+$19.71 / week / HH** | **Difference-in-Differences on Matched Panel** |
| **Statistical Significance** | Spurious p < 0.0001 | **p = 1.8518e-28 (t = 11.62)** | 95% CI: `[+$16.38, +$23.03]` |
| **Enterprise Incremental Revenue** | $4.8M (Overstated) | **+$2,185,265.34** | True net causal lift over 70 campaign weeks |

---

## 2. Selection Bias Diagnostic (Pre-Treatment Proof)

During the **pre-treatment baseline window (Days 1 to 223 / Weeks 1 to 31)**, before any marketing campaign launched:
- **Treated Households Average Weekly Spend:** `$32.78`
- **Non-Targeted Households Average Weekly Spend:** `$8.28`
- **Pre-Existing Baseline Disparity:** **+$24.50 per week** ($p < 0.00001$)

> **Recruiter & Interviewer Defense:** 
> Marketing teams deliberately select high-frequency, high-value loyalty shoppers for campaign mailers. Comparing targeted customers directly to non-targeted customers commits **omitted variable selection bias**, confusing *selection affinity* with *campaign impact*. Over 60% of the raw spend difference was pre-existing!

---

## 3. Propensity Score Matching & Covariate Balance

To resolve confounding, we estimated propensity scores $e(X_i) = P(T_i = 1 \mid X_i)$ and executed 1:1 Nearest-Neighbor Caliper Matching across 6 pre-treatment behavioral features:

| Covariate | Unmatched Treated | Unmatched Control | SMD Before Matching | Matched Treated | Matched Control | SMD After Matching |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `pre_weekly_spend` | $32.78 | $8.28 | **+1.1281** | $13.84 | $13.68 | **`+0.0100`** |
| `pre_baskets` | $37.61 | $11.32 | **+0.9616** | $17.84 | $17.82 | **`+0.0011`** |
| `pre_avg_basket` | $32.87 | $27.63 | **+0.2300** | $29.20 | $29.99 | **`-0.0368`** |
| `pre_discount_pct` | $15.74 | $16.40 | **-0.0935** | $16.09 | $16.47 | **`-0.0578`** |
| `pre_unique_products` | $234.68 | $72.26 | **+1.2773** | $113.48 | $114.56 | **`-0.0115`** |
| `pre_shopping_days` | $30.12 | $9.51 | **+1.2043** | $14.75 | $14.69 | **`+0.0047`** |

*Note: A Standardized Mean Difference (SMD) with absolute value $< 0.10$ denotes excellent experimental balance.* All matched covariates achieve near-perfect balance!

---

## 4. Difference-in-Differences Econometric Estimation

Using the balanced matched cohorts ($N = 346$ per arm), the causal Average Treatment Effect on the Treated (ATT) is estimated:

$$\text{ATT} = (\bar{Y}_{\text{Treated, Post}} - \bar{Y}_{\text{Treated, Pre}}) - (\bar{Y}_{\text{Control, Post}} - \bar{Y}_{\text{Control, Pre}})$$

- **Change in Matched Treated Spend:** **+$20.14 / week**
- **Change in Matched Control Spend:** **+$0.44 / week**
- **Causal ATT ($\\hat{\\delta}$):** **+$19.71 per week per household**
- **95% Confidence Interval:** **`[+$16.38, +$23.03]`**
- **p-value:** `1.8518e-28` (Reject null hypothesis of zero effect at $\alpha = 0.05$)

---

## 5. Parallel Trends / In-Time Placebo Validation

We tested the parallel trends assumption by running a placebo Difference-in-Differences comparison across the two pre-treatment halves (Weeks 1–16 vs Weeks 17–32):
- **Placebo ATT:** **$1.18 / week**
- **p-value:** `0.4774`
- **Conclusion:** Because the placebo ATT is statistically zero ($p > 0.05$), the parallel trends assumption is satisfied, confirming that the post-treatment divergence was causally driven by the marketing campaigns.
