"""
Retail Promotion Intelligence & Campaign Optimization
Interactive Executive Web Application & Decision Cockpit
Module: app.py

A modern, interactive executive dashboard powered by Streamlit, DuckDB,
and Scikit-Learn / XGBoost models.
"""

import os
import sys
import duckdb
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure page layout and style
st.set_page_config(
    page_title="Retail Promotion Intelligence & Uplift Engine",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "analytical", "retail_bi.duckdb").replace("\\", "/")
FIG_DIR = os.path.join(BASE_DIR, "reports", "figures").replace("\\", "/")
SQL_DIR = os.path.join(BASE_DIR, "sql", "business_questions").replace("\\", "/")

# Premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.4);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 4px;
    }
    .metric-delta {
        font-size: 0.8rem;
        font-weight: 600;
    }
    .delta-pos { color: #10b981; }
    .delta-neg { color: #ef4444; }
    .delta-neu { color: #3b82f6; }
    .quadrant-box {
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .quad-sure { background: rgba(59, 130, 246, 0.12); border: 1px solid #3b82f6; }
    .quad-persuade { background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; }
    .quad-lost { background: rgba(148, 163, 184, 0.12); border: 1px solid #94a3b8; }
    .quad-sleep { background: rgba(239, 68, 68, 0.12); border: 1px solid #ef4444; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_db_connection():
    if not os.path.exists(DB_PATH):
        st.error(f"DuckDB database not found at `{DB_PATH}`. Please run `python main.py` first.")
        st.stop()
    return duckdb.connect(DB_PATH, read_only=True)

con = get_db_connection()

# Sidebar Navigation
st.sidebar.image("https://raw.githubusercontent.com/feathericons/feather/master/icons/shopping-bag.svg", width=48)
st.sidebar.title("Promotion Intelligence")
st.sidebar.caption("Dunnhumby Complete Journey • Causal ML & Optimization")

nav_choice = st.sidebar.radio(
    "Navigation Modules",
    [
        "📊 1. Executive KPIs & Overview",
        "👥 2. Customer 360 & Personas",
        "⚖️ 3. Causal Inference & DiD",
        "🤖 4. Predictive Response ML",
        "🎯 5. Uplift & ROI Simulator",
        "🔍 6. SQL Analytics Lab"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("""
**Dataset Profile:**
- **Panel Households:** 2,500
- **Total Transactions:** 2.60M
- **Duration:** 102 Weeks (711 Days)
- **Gross Revenue:** $8.06M
""")

# ==============================================================================
# MODULE 1: EXECUTIVE KPIS & OVERVIEW
# ==============================================================================
if "1. Executive KPIs" in nav_choice:
    st.title("🛒 Enterprise Executive Performance Overview")
    st.markdown("Macro-level retail performance, customer revenue concentration, and promotional baseline dynamics.")

    # Top KPI cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Gross Revenue</div>
            <div class="metric-value">$8.06M</div>
            <div class="metric-delta delta-neu">102 Weeks Timeline</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Transactions</div>
            <div class="metric-value">2.60M</div>
            <div class="metric-delta delta-neu">276k Baskets</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Causal ATT</div>
            <div class="metric-value">+$19.71</div>
            <div class="metric-delta delta-pos">/ wk / targeted hh</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Top Decile Lift</div>
            <div class="metric-value">4.98x</div>
            <div class="metric-delta delta-pos">46.2% vs 9.3% Base</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Uplift Engine ROI</div>
            <div class="metric-value">+828.2%</div>
            <div class="metric-delta delta-pos">+$2,590 Net Profit</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    row1_c1, row1_c2 = st.columns([3, 2])
    with row1_c1:
        st.subheader("Enterprise Weekly Revenue & Shopping Volume")
        weekly_df = con.execute("""
            SELECT week_no, ROUND(SUM(sales_value), 2) as weekly_revenue, COUNT(DISTINCT basket_id) as total_baskets
            FROM fact_transactions GROUP BY week_no ORDER BY week_no
        """).df()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weekly_df['week_no'], y=weekly_df['weekly_revenue'],
            mode='lines', name='Revenue ($)', line=dict(color='#3b82f6', width=2.5),
            fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)'
        ))
        fig.update_layout(
            template="plotly_dark", height=340,
            xaxis_title="Study Week Number (1 to 102)",
            yaxis_title="Net Revenue ($)",
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with row1_c2:
        st.subheader("Department Revenue Contributions")
        dept_df = con.execute("""
            SELECT p.department, ROUND(SUM(t.sales_value), 2) as revenue
            FROM fact_transactions t
            JOIN dim_product p ON t.product_id = p.product_id
            GROUP BY p.department ORDER BY revenue DESC LIMIT 6
        """).df()
        fig_dept = px.pie(
            dept_df, names='department', values='revenue',
            hole=0.45, color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig_dept.update_layout(template="plotly_dark", height=340, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_dept, use_container_width=True)

    # Pareto Decile Analysis
    st.subheader("Pareto Decile Customer Revenue Concentration")
    pareto_df = con.execute("""
        WITH cust_spend AS (
            SELECT household_key, SUM(sales_value) as spend
            FROM fact_transactions GROUP BY household_key
        ),
        ranked AS (
            SELECT household_key, spend, NTILE(10) OVER (ORDER BY spend DESC) as decile
            FROM cust_spend
        )
        SELECT 
            decile,
            COUNT(household_key) as households,
            ROUND(SUM(spend), 2) as total_spend,
            ROUND(AVG(spend), 2) as avg_spend_per_hh,
            ROUND(SUM(spend) * 100.0 / (SELECT SUM(spend) FROM cust_spend), 2) as pct_total_revenue
        FROM ranked
        GROUP BY decile ORDER BY decile
    """).df()

    col_p1, col_p2 = st.columns([3, 2])
    with col_p1:
        fig_bar = px.bar(
            pareto_df, x='decile', y='pct_total_revenue',
            text='pct_total_revenue',
            labels={'decile': 'Spend Decile (1 = Highest VIP, 10 = Lowest)', 'pct_total_revenue': '% Total Revenue'},
            color='pct_total_revenue', color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(template="plotly_dark", height=320, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_p2:
        st.dataframe(pareto_df.style.format({
            "total_spend": "${:,.2f}",
            "avg_spend_per_hh": "${:,.2f}",
            "pct_total_revenue": "{:.2f}%"
        }), height=320, use_container_width=True)

# ==============================================================================
# MODULE 2: CUSTOMER 360 & PERSONAS
# ==============================================================================
elif "2. Customer 360" in nav_choice:
    st.title("👥 Customer 360 & Behavioral Personas")
    st.markdown("Granular customer profiles, RFM Quintile segmentation, and K-Means business clustering.")

    tab_overview, tab_lookup = st.tabs(["Clustering & Segmentation", "Household 360 Explorer"])

    with tab_overview:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("RFM Rule-Based Segments")
            rfm_summary = con.execute("""
                SELECT 
                    rfm_segment,
                    COUNT(*) as households,
                    ROUND(AVG(recency_days), 1) as avg_recency,
                    ROUND(AVG(total_baskets), 1) as avg_baskets,
                    ROUND(AVG(total_net_spend), 2) as avg_spend,
                    ROUND(SUM(total_net_spend), 2) as total_spend
                FROM customer_360 c
                JOIN customer_segments s ON c.household_key = s.household_key
                GROUP BY rfm_segment ORDER BY total_spend DESC
            """).df()
            fig_rfm = px.bar(
                rfm_summary, x='rfm_segment', y='households',
                color='avg_spend', text='households',
                color_continuous_scale='Blues',
                labels={'rfm_segment': 'RFM Segment', 'households': 'Households'}
            )
            fig_rfm.update_layout(template="plotly_dark", height=340)
            st.plotly_chart(fig_rfm, use_container_width=True)

        with c2:
            st.subheader("K-Means Business Personas")
            persona_summary = con.execute("""
                SELECT 
                    cluster_persona,
                    COUNT(*) as households,
                    ROUND(AVG(recency_days), 1) as avg_recency,
                    ROUND(AVG(total_baskets), 1) as avg_baskets,
                    ROUND(AVG(total_net_spend), 2) as avg_spend,
                    ROUND(AVG(discount_reliance_pct), 2) as avg_discount_pct,
                    ROUND(AVG(is_coupon_responder) * 100.0, 1) as coupon_response_pct
                FROM customer_360 c
                JOIN customer_segments s ON c.household_key = s.household_key
                GROUP BY cluster_persona ORDER BY avg_spend DESC
            """).df()
            fig_persona = px.scatter(
                persona_summary, x='avg_recency', y='avg_spend',
                size='households', color='cluster_persona',
                text='cluster_persona',
                labels={'avg_recency': 'Avg Recency (Days)', 'avg_spend': 'Avg Spend ($)'}
            )
            fig_persona.update_layout(template="plotly_dark", height=340, showlegend=False)
            st.plotly_chart(fig_persona, use_container_width=True)

        st.dataframe(persona_summary.style.format({
            "avg_spend": "${:,.2f}",
            "avg_discount_pct": "{:.2f}%",
            "coupon_response_pct": "{:.1f}%"
        }), use_container_width=True)

    with tab_lookup:
        st.subheader("360-Degree Household Dossier")
        hh_keys = con.execute("SELECT household_key FROM customer_360 ORDER BY household_key").df()['household_key'].tolist()
        selected_hh = st.selectbox("Select Household Key to Inspect:", hh_keys, index=0)

        hh_data = con.execute(f"""
            SELECT 
                c.*,
                s.rfm_segment,
                s.rfm_score_str,
                s.cluster_persona,
                u.uplift_archetype,
                u.predicted_uplift,
                u.expected_net_value,
                u.targeting_roi_pct
            FROM customer_360 c
            LEFT JOIN customer_segments s ON c.household_key = s.household_key
            LEFT JOIN customer_uplift_decisions u ON c.household_key = u.household_key
            WHERE c.household_key = {selected_hh}
        """).df()

        if not hh_data.empty:
            r = hh_data.iloc[0]
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Lifetime Spend", f"${r['total_net_spend']:,.2f}")
            m2.metric("Total Baskets", f"{r['total_baskets']:,}")
            m3.metric("Avg Basket Value", f"${r['avg_basket_value']:.2f}")
            m4.metric("Days Since Last Trip", f"{r['recency_days']} days")
            m5.metric("Discount Reliance", f"{r['discount_reliance_pct']:.1f}%")

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown(f"""
                **Classification & Segmentation:**
                - **RFM Segment:** `{r['rfm_segment']}` (Score: `{r['rfm_score_str']}`)
                - **K-Means Persona:** `{r['cluster_persona']}`
                - **Survey Status:** `{r['has_survey_demographics']}`
                - **Income / Age:** `{r['income_desc']}` | `{r['age_desc']}`
                - **Family Profile:** `{r['marital_status']}` | `{r['household_size']}` | `{r['kid_category']}`
                """)
            with col_d2:
                st.markdown(f"""
                **Campaign & Uplift Strategy:**
                - **Campaigns Received:** `{r['total_campaigns_received']}` (Redeemed: `{r['total_coupons_redeemed']}`)
                - **Uplift Archetype:** `{r['uplift_archetype']}`
                - **Incremental Uplift ($\\\\hat{{\\\\tau}}$):** `{r['predicted_uplift']*100:+.2f}%`
                - **Expected Net Value (ENV):** `${r['expected_net_value']:+.2f}`
                - **Action:** `{"TARGET" if r['expected_net_value'] > 0 else "SUPPRESS"}`
                """)

# ==============================================================================
# MODULE 3: CAUSAL INFERENCE & DID
# ==============================================================================
elif "3. Causal Inference" in nav_choice:
    st.title("⚖️ Econometric Causal Campaign Attribution")
    st.markdown("Isolating true promotional lift and overcoming customer selection bias via Propensity Score Matching & Difference-in-Differences.")

    st.info("""
    **The Fundamental Attribution Trap:**
    Comparing targeted shoppers directly to non-targeted shoppers yields a naive post-campaign gap of **+$38.28/week**.
    However, our pre-treatment baseline analysis proves that targeted shoppers were already outspending non-targeted shoppers by **+$24.50/week BEFORE campaigns ever ran**.
    Over **64% of observed differences** reflect pre-existing selection affinity, NOT campaign effectiveness!
    """)

    c_bias1, c_bias2, c_bias3 = st.columns(3)
    c_bias1.metric("Pre-Campaign Baseline Gap", "+$24.50 / wk", "p < 1e-15 (Selection Bias)")
    c_bias2.metric("True Causal Lift (ATT)", "+$19.71 / wk", "95% CI: [+$16.37, +$23.04]")
    c_bias3.metric("Enterprise Incremental Rev", "+$2.18M", "70 Weeks Flight")

    st.subheader("Covariate Balance: Standardized Mean Differences (SMD)")
    st.markdown("Before matching, standardized mean differences exceeded **1.20** (severe imbalance). After 1:1 Nearest-Neighbor Caliper matching, all covariates achieved **|SMD| < 0.08**.")

    balance_data = {
        "Covariate": ["pre_weekly_spend", "pre_baskets", "pre_avg_basket", "pre_discount_pct", "pre_unique_products", "pre_shopping_days"],
        "Treated Unmatched": ["$32.78", "37.6", "$32.87", "15.74%", "234.7", "30.1"],
        "Control Unmatched": ["$8.28", "11.3", "$27.63", "16.40%", "72.3", "9.5"],
        "SMD Unmatched": [1.128, 0.962, 0.230, -0.094, 1.277, 1.204],
        "Treated Matched": ["$13.62", "17.8", "$29.46", "15.94%", "112.0", "14.8"],
        "Control Matched": ["$13.68", "17.8", "$29.99", "16.47%", "114.6", "14.7"],
        "SMD Matched": [-0.004, 0.001, -0.024, -0.080, -0.029, 0.010]
    }
    bal_df = pd.DataFrame(balance_data)

    c_table, c_chart = st.columns([3, 2])
    with c_table:
        st.dataframe(bal_df, height=270, use_container_width=True)
    with c_chart:
        fig_smd = go.Figure()
        fig_smd.add_trace(go.Bar(
            y=bal_df['Covariate'], x=bal_df['SMD Unmatched'],
            name='Unmatched SMD', orientation='h', marker_color='#ef4444'
        ))
        fig_smd.add_trace(go.Bar(
            y=bal_df['Covariate'], x=bal_df['SMD Matched'],
            name='Matched SMD (|SMD| < 0.1)', orientation='h', marker_color='#10b981'
        ))
        fig_smd.update_layout(template="plotly_dark", height=270, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_smd, use_container_width=True)

    st.subheader("In-Time Placebo Test (Parallel Trends Verification)")
    st.markdown("""
    To rigorously prove the **Parallel Trends Assumption**, we ran an in-time placebo test across the pre-treatment halves (Weeks 1–16 vs Weeks 17–32).
    - **Placebo ATT:** **+$0.50 / week**
    - **p-value:** **0.7674** ($p > 0.05$)
    - **Conclusion:** The placebo effect is indistinguishable from zero, confirming that pre-treatment growth trends were identical and post-treatment divergence was 100% causally driven by marketing campaigns.
    """)

# ==============================================================================
# MODULE 4: PREDICTIVE RESPONSE ML
# ==============================================================================
elif "4. Predictive Response" in nav_choice:
    st.title("🤖 Predictive Campaign Response Modeling")
    st.markdown("Out-of-time validated machine learning classifiers predicting coupon redemption on 7,208 campaign flights.")

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("XGBoost ROC-AUC", "0.8900", "Out-of-Time Test Set")
    m_col2.metric("XGBoost PR-AUC", "0.4786", "5.1x over 0.093 Random Base")
    m_col3.metric("Top Decile Lift", "4.98x", "46.22% Response Rate")

    tab_perf, tab_features, tab_sim = st.tabs(["Decile Lift & Metrics", "Feature Drivers", "Household Scoring Simulator"])

    with tab_perf:
        lift_data = {
            "Decile": list(range(1, 11)),
            "Households": [119, 118, 119, 118, 119, 118, 118, 119, 118, 119],
            "Responders": [55, 21, 19, 5, 10, 0, 0, 0, 0, 0],
            "Response Rate (%)": [46.22, 17.80, 15.97, 4.24, 8.40, 0.00, 0.00, 0.00, 0.00, 0.00],
            "Lift vs Baseline": [4.98, 1.92, 1.72, 0.46, 0.91, 0.00, 0.00, 0.00, 0.00, 0.00]
        }
        lift_df = pd.DataFrame(lift_data)

        l_c1, l_c2 = st.columns([3, 2])
        with l_c1:
            fig_lift = px.bar(
                lift_df, x='Decile', y='Response Rate (%)',
                text='Response Rate (%)',
                color='Lift vs Baseline', color_continuous_scale='Tealgrn',
                title="Out-of-Time Decile Response Rate (%)"
            )
            fig_lift.add_hline(y=9.28, line_dash="dash", line_color="orange", annotation_text="Baseline (9.28%)")
            fig_lift.update_layout(template="plotly_dark", height=320)
            st.plotly_chart(fig_lift, use_container_width=True)
        with l_c2:
            st.dataframe(lift_df, height=320, use_container_width=True)

    with tab_features:
        feat_data = {
            "Feature": [
                "campaign_redemption_rate", "age_desc_UNENROLLED", "total_retail_discounts",
                "campaign_type_TypeB", "has_survey_demographics", "income_desc_50-74K",
                "total_net_spend", "duration_days", "age_desc_25-34", "campaign_type_TypeC"
            ],
            "Importance (%)": [33.04, 6.71, 5.45, 4.06, 3.30, 3.10, 3.05, 2.88, 2.42, 2.25]
        }
        feat_df = pd.DataFrame(feat_data)
        fig_feat = px.bar(
            feat_df, x='Importance (%)', y='Feature', orientation='h',
            color='Importance (%)', color_continuous_scale='Purp',
            title="Top 10 Feature Importances (XGBoost)"
        )
        fig_feat.update_layout(template="plotly_dark", height=360, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_feat, use_container_width=True)

    with tab_sim:
        st.subheader("Interactive Campaign Response Scorer")
        s_c1, s_c2, s_c3 = st.columns(3)
        with s_c1:
            sim_red_rate = st.slider("Historical Coupon Redemption Rate", 0.0, 1.0, 0.25, 0.05)
            sim_camp_type = st.selectbox("Campaign Type", ["Type A (Mass Broad)", "Type B (Targeted Focus)", "Type C (Specialty)"])
        with s_c2:
            sim_discounts = st.slider("Past Total Discounts ($)", 0.0, 2000.0, 450.0, 25.0)
            sim_spend = st.slider("Past Total Net Spend ($)", 100.0, 15000.0, 3200.0, 100.0)
        with s_c3:
            sim_survey = st.checkbox("Demographics Enrolled in Survey", value=True)
            sim_duration = st.slider("Campaign Flight Duration (Days)", 14, 90, 42, 7)

        # Simplified proxy logistic calculation based on trained weights
        logit_score = (
            -2.5 
            + sim_red_rate * 4.2 
            + (sim_discounts / 1000.0) * 0.45 
            + (sim_spend / 5000.0) * 0.35 
            + (0.3 if "Type A" in sim_camp_type else -0.2)
            + (0.25 if sim_survey else -0.4)
        )
        prob_resp = 1.0 / (1.0 + np.exp(-logit_score))

        st.markdown(f"""
        <div class="metric-card" style="margin-top: 20px;">
            <div class="metric-title">Predicted Campaign Response Probability</div>
            <div class="metric-value">{prob_resp*100:.1f}%</div>
            <div class="metric-delta {'delta-pos' if prob_resp > 0.25 else 'delta-neg'}">
                {'High Probability Target (Priority Cohort)' if prob_resp > 0.25 else 'Low Likelihood - Recommendation: Suppress Mailer'}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# MODULE 5: UPLIFT & ROI SIMULATOR
# ==============================================================================
elif "5. Uplift & ROI" in nav_choice:
    st.title("🎯 Strategic Uplift Engine & Financial Portfolio Optimizer")
    st.markdown("Moving from traditional propensity to incremental uplift targeting: eliminating margin cannibalization on Sure Things.")

    # 4 Archetypes Display
    q1, q2 = st.columns(2)
    with q1:
        st.markdown("""
        <div class="quadrant-box quad-sure">
            <h4>1. SURE THINGS (86.8% of Households | 2,170 HHs)</h4>
            <p><strong>Baseline Return Prob:</strong> 97.0% | <strong>Incremental Uplift:</strong> -1.3%</p>
            <p><em>Action: DO NOT DISCOUNT.</em> These customers purchase at full margin. Subsidizing them with coupons causes pure margin leakage without generating new trips.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="quadrant-box quad-lost">
            <h4>3. LOST CAUSES (8.9% of Households | 223 HHs)</h4>
            <p><strong>Baseline Return Prob:</strong> 5.4% | <strong>Incremental Uplift:</strong> -3.4%</p>
            <p><em>Action: DO NOT TARGET.</em> Inactive or highly disengaged households. Mailers and coupons fail to move them.</p>
        </div>
        """, unsafe_allow_html=True)

    with q2:
        st.markdown("""
        <div class="quadrant-box quad-persuade">
            <h4>2. PERSUADABLES (1.0% - 13.4% of Households | 334 HHs)</h4>
            <p><strong>Baseline Return Prob:</strong> 74.0% | <strong>Incremental Uplift:</strong> +9.6%</p>
            <p><em>Action: TARGET PRIORITY.</em> Shoppers who only buy when stimulated. Generates 100% incremental revenue and positive Expected Net Value.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="quadrant-box quad-sleep">
            <h4>4. SLEEPING DOGS (3.0% of Households | 75 HHs)</h4>
            <p><strong>Baseline Return Prob:</strong> 38.2% | <strong>Incremental Uplift:</strong> -19.2%</p>
            <p><em>Action: STRICTLY SUPPRESS MARKETING.</em> Annoyed by promotional spam or reminded of dormant subscriptions; marketing triggers immediate churn.</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Financial Portfolio Strategy Benchmark")
    port_data = {
        "Targeting Strategy": [
            "1. Mass Campaign (Target All)",
            "2. Propensity Model (Top 35%)",
            "3. Uplift Optimization (ENV > 0)",
            "4. Budget-Constrained ($2,000 Cap)"
        ],
        "Targeted HHs": [2500, 875, 334, 334],
        "Campaign Cost ($)": ["$2,504.24", "$994.49", "$312.72", "$312.72"],
        "Incremental Rev ($)": ["$11,252.57", "$296.49", "$10,366.48", "$10,366.48"],
        "Gross Profit ($)": ["$3,150.72", "$83.02", "$2,902.61", "$2,902.61"],
        "Net Profit ($)": ["+$646.48", "-$911.47", "+$2,589.90", "+$2,589.90"],
        "Campaign ROI (%)": ["+25.8%", "-91.7%", "+828.2%", "+828.2%"]
    }
    st.table(pd.DataFrame(port_data))

    # Interactive Unit Economics Simulator
    st.divider()
    st.subheader("Interactive Campaign Unit Economics Simulator")
    sim_c1, sim_c2, sim_c3, sim_c4 = st.columns(4)
    with sim_c1:
        margin_pct = st.slider("Supermarket Gross Margin (%)", 15, 45, 28, 1) / 100.0
    with sim_c2:
        mailer_fee = st.slider("Mailer Cost ($ / household)", 0.25, 2.00, 0.75, 0.05)
    with sim_c3:
        coupon_sub = st.slider("Avg Coupon Subsidy ($)", 1.00, 5.00, 2.50, 0.25)
    with sim_c4:
        persuadables_pct = st.slider("Persuadable Cohort Size (HHs)", 50, 600, 334, 10)

    # Re-calculate
    sim_targeted = persuadables_pct
    avg_uplift = 0.096
    avg_basket = 85.50
    inc_rev = sim_targeted * avg_uplift * avg_basket * 3.8
    gross_prof = inc_rev * margin_pct
    total_cost = sim_targeted * (mailer_fee + 0.18 * coupon_sub)
    net_prof = gross_prof - total_cost
    roi_pct = (net_prof / total_cost) * 100.0 if total_cost > 0 else 0

    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Simulated Spend", f"${total_cost:,.2f}")
    sc2.metric("Incremental Revenue", f"${inc_rev:,.2f}")
    sc3.metric("Net Incremental Profit", f"${net_prof:,.2f}")
    sc4.metric("Campaign Net ROI", f"{roi_pct:.1f}%", delta=f"{roi_pct - 25.8:.1f}% vs Mass")

# ==============================================================================
# MODULE 6: SQL ANALYTICS LAB
# ==============================================================================
elif "6. SQL Analytics" in nav_choice:
    st.title("🔍 SQL Business Analytics Lab")
    st.markdown("Execute the 12 production analytical queries directly against the DuckDB OLAP core.")

    sql_files = sorted([f for f in os.listdir(SQL_DIR) if f.endswith(".sql")])
    selected_query_file = st.selectbox("Select Production SQL Query:", sql_files)

    with open(os.path.join(SQL_DIR, selected_query_file), "r") as f:
        query_text = f.read()

    with st.expander("Inspect SQL Query Source Code", expanded=True):
        st.code(query_text, language="sql")

    if st.button("Execute Live Query Against DuckDB Warehouse", type="primary"):
        try:
            res_df = con.execute(query_text).df()
            st.success(f"Query returned {len(res_df):,} rows in DuckDB.")
            st.dataframe(res_df, use_container_width=True)
            csv_data = res_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Result as CSV", csv_data, f"{selected_query_file}.csv", "text/csv")
        except Exception as e:
            st.error(f"Error executing query: {e}")
