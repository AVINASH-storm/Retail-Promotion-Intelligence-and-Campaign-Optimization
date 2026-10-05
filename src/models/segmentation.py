"""
Retail Promotion Intelligence & Campaign Optimization
Customer Segmentation: RFM Rule-Based vs K-Means Machine Learning
Module: src/models/segmentation.py

Constructs:
1. Rule-based RFM Segment Taxonomy
2. K-Means Clustering with Elbow and Silhouette Optimization
3. Profiling and mapping clusters to actionable Business Personas
"""

import os
import sys
import logging
import joblib
import duckdb
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Segmentation")

BASE_DIR = r"c:\Users\Avinash\Desktop\dunnhumpy"
DB_PATH = os.path.join(BASE_DIR, "data", "analytical", "retail_bi.duckdb").replace("\\", "/")
ANALYTICAL_DIR = os.path.join(BASE_DIR, "data", "analytical").replace("\\", "/")
MODEL_DIR = os.path.join(BASE_DIR, "models").replace("\\", "/")

def build_segmentation():
    os.makedirs(MODEL_DIR, exist_ok=True)
    con = duckdb.connect(DB_PATH)
    
    logger.info("Extracting Customer 360 features from warehouse...")
    df = con.execute("SELECT * FROM customer_360").df()
    logger.info(f"Loaded {len(df):,} customer records.")
    
    # -------------------------------------------------------------
    # 1. RULE-BASED RFM SEGMENTATION
    # -------------------------------------------------------------
    logger.info("Computing Quintile-based RFM scores...")
    
    # Recency: Lower is better (inverted rank: 5 = most recent, 1 = least recent)
    df['r_score'] = pd.qcut(df['recency_days'], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    
    # Frequency: Higher is better (rank: 5 = highest frequency)
    df['f_score'] = pd.qcut(df['total_baskets'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    # Monetary: Higher is better (rank: 5 = highest spend)
    df['m_score'] = pd.qcut(df['total_net_spend'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    df['rfm_score_str'] = df['r_score'].astype(str) + df['f_score'].astype(str) + df['m_score'].astype(str)
    
    def assign_rfm_segment(row):
        r, f, m = row['r_score'], row['f_score'], row['m_score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 3 and m <= 3:
            return 'Potential Loyalists'
        elif r <= 2 and f >= 3 and m >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2:
            return 'Hibernating / Lapsed'
        else:
            return 'Promising / Needs Attention'

    df['rfm_segment'] = df.apply(assign_rfm_segment, axis=1)
    
    rfm_summary = df.groupby('rfm_segment').agg(
        households=('household_key', 'count'),
        avg_recency=('recency_days', 'mean'),
        avg_baskets=('total_baskets', 'mean'),
        avg_spend=('total_net_spend', 'mean'),
        total_revenue=('total_net_spend', 'sum'),
        coupon_response_rate=('is_coupon_responder', 'mean')
    ).reset_index()
    rfm_summary['pct_households'] = round(rfm_summary['households'] * 100.0 / len(df), 2)
    rfm_summary['pct_revenue'] = round(rfm_summary['total_revenue'] * 100.0 / df['total_net_spend'].sum(), 2)
    logger.info("\n=== RFM RULE-BASED SEGMENTS ===\n" + rfm_summary.to_string(index=False))

    # -------------------------------------------------------------
    # 2. MACHINE LEARNING: K-MEANS CLUSTERING
    # -------------------------------------------------------------
    logger.info("Preparing feature space for K-Means Clustering...")
    cluster_cols = [
        'recency_days', 
        'total_baskets', 
        'total_net_spend', 
        'avg_basket_value', 
        'discount_reliance_pct',
        'unique_commodities_shopped'
    ]
    
    # Log transforms for skewed monetary and frequency features
    X_raw = df[cluster_cols].copy()
    X_trans = pd.DataFrame()
    X_trans['log_recency'] = np.log1p(X_raw['recency_days'])
    X_trans['log_baskets'] = np.log1p(X_raw['total_baskets'])
    X_trans['log_spend'] = np.log1p(X_raw['total_net_spend'])
    X_trans['log_basket_val'] = np.log1p(X_raw['avg_basket_value'])
    X_trans['discount_reliance'] = X_raw['discount_reliance_pct']
    X_trans['commodities'] = X_raw['unique_commodities_shopped']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_trans)
    
    # Evaluate K from 2 to 7
    scores = {}
    for k in range(2, 8):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        sil = silhouette_score(X_scaled, km.labels_)
        scores[k] = {"inertia": km.inertia_, "silhouette": sil}
        logger.info(f"K={k}: Inertia={km.inertia_:.1f}, Silhouette={sil:.4f}")
        
    # Selected K=4 based on business interpretability and silhouette balance
    best_k = 4
    final_kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=20)
    df['kmeans_cluster'] = final_kmeans.fit_predict(X_scaled)
    
    # Profile K-Means Clusters
    cluster_profile = df.groupby('kmeans_cluster').agg(
        households=('household_key', 'count'),
        avg_recency=('recency_days', 'mean'),
        avg_baskets=('total_baskets', 'mean'),
        avg_spend=('total_net_spend', 'mean'),
        avg_basket_value=('avg_basket_value', 'mean'),
        avg_discount_pct=('discount_reliance_pct', 'mean'),
        coupon_response_rate=('is_coupon_responder', 'mean')
    ).reset_index()
    
    # Assign Business Personas based on cluster attributes
    # Sort by spend to create deterministic naming
    spend_order = cluster_profile.sort_values('avg_spend', ascending=False)['kmeans_cluster'].tolist()
    persona_mapping = {
        spend_order[0]: "Power Core VIPs (High Spend & Frequency)",
        spend_order[1]: "Bulk & Deal Seekers (High Basket Value & Disc)",
        spend_order[2]: "Casual Mainstream (Moderate Frequency)",
        spend_order[3]: "Lapsed & Low Engagement (High Recency, Low Spend)"
    }
    df['cluster_persona'] = df['kmeans_cluster'].map(persona_mapping)
    
    persona_summary = df.groupby('cluster_persona').agg(
        households=('household_key', 'count'),
        avg_recency=('recency_days', 'mean'),
        avg_baskets=('total_baskets', 'mean'),
        avg_spend=('total_net_spend', 'mean'),
        avg_basket_value=('avg_basket_value', 'mean'),
        avg_discount_pct=('discount_reliance_pct', 'mean'),
        coupon_response_rate=('is_coupon_responder', 'mean')
    ).reset_index()
    persona_summary['pct_households'] = round(persona_summary['households'] * 100.0 / len(df), 2)
    logger.info("\n=== K-MEANS BUSINESS PERSONAS ===\n" + persona_summary.to_string(index=False))

    # Save artifacts
    joblib.dump(final_kmeans, os.path.join(MODEL_DIR, "kmeans_model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "segmentation_scaler.joblib"))
    
    # Export to Parquet and DuckDB
    export_cols = [
        'household_key', 'r_score', 'f_score', 'm_score', 'rfm_score_str',
        'rfm_segment', 'kmeans_cluster', 'cluster_persona'
    ]
    seg_df = df[export_cols]
    
    con.execute("CREATE OR REPLACE TABLE customer_segments AS SELECT * FROM seg_df;")
    seg_parquet = os.path.join(ANALYTICAL_DIR, "customer_segments.parquet").replace("\\", "/")
    con.execute(f"COPY customer_segments TO '{seg_parquet}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    logger.info(f"customer_segments table updated in DuckDB and saved to {seg_parquet}")
    con.close()

if __name__ == "__main__":
    build_segmentation()
