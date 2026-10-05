"""
Retail Promotion Intelligence & Campaign Optimization
Master Project Pipeline Orchestrator
Module: main.py

Executes the end-to-end analytics, causal inference, and machine learning pipeline:
1. ETL & Parquet Ingestion (Raw CSV -> DuckDB Star Schema)
2. Customer 360 Behavioral & Cadence Mart
3. Customer Segmentation (RFM Quintiles & K-Means Clusters)
4. Retention & Survival Analysis (Empirical Cadence & Churn Threshold)
5. Econometric Causal Inference (PSM + Difference-in-Differences ATT)
6. Predictive Campaign Response Classifier (Out-of-Time XGBoost)
7. Strategic Uplift Targeting Engine (T-Learner CATE & Financial Portfolio Simulation)
8. SQL Business Analytics Execution (12 Analytical Queries & KPI Report)
9. Publication-Grade Visualizations (7 Visual Charts)
10. Power BI Semantic Marts Export
"""

import os
import sys
import time
import argparse
import subprocess
import logging

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("PipelineRunner")

BANNER = r"""
================================================================================
  RETAIL PROMOTION INTELLIGENCE & CAMPAIGN OPTIMIZATION
  Dunnhumby Complete Journey - End-to-End Enterprise Analytics & Causal ML
================================================================================
"""

def print_banner():
    print(BANNER)

def check_environment():
    """Verify raw data files and directories exist."""
    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    required_csvs = [
        "transaction_data.csv", "product.csv", "hh_demographic.csv",
        "campaign_desc.csv", "campaign_table.csv", "coupon.csv",
        "coupon_redempt.csv", "causal_data.csv"
    ]
    missing = [f for f in required_csvs if not os.path.exists(os.path.join(raw_dir, f))]
    if missing:
        logger.error(f"Missing raw CSV datasets in {raw_dir}: {missing}")
        return False
    logger.info("Environment check passed: All 8 raw CSV source datasets verified.")
    return True

def run_step(step_num, title, func, *args, **kwargs):
    """Executes a pipeline step with timing and error isolation."""
    sep = "=" * 80
    print(f"\n{sep}\n[STEP {step_num}/10] {title}\n{sep}")
    t0 = time.time()
    try:
        res = func(*args, **kwargs)
        elapsed = time.time() - t0
        print(f"--> [SUCCESS] Step {step_num} finished in {elapsed:.2f}s.")
        return True, elapsed, res
    except Exception as e:
        elapsed = time.time() - t0
        logger.error(f"[ERROR] Step {step_num} failed after {elapsed:.2f}s: {e}", exc_info=True)
        return False, elapsed, None

def run_full_pipeline(skip_etl_if_db_exists=True, launch_web=False):
    """Executes the entire analytics and ML suite."""
    print_banner()
    if not check_environment():
        sys.exit(1)

    db_path = os.path.join(BASE_DIR, "data", "analytical", "retail_bi.duckdb")
    db_exists = os.path.exists(db_path) and os.path.getsize(db_path) > 1_000_000

    step_results = []
    overall_start = time.time()

    # Step 1: ETL Pipeline
    from src.preprocessing.etl_pipeline import run_pipeline as etl_run
    if db_exists and skip_etl_if_db_exists:
        logger.info("DuckDB warehouse 'retail_bi.duckdb' already exists (650+ MB). Skipping raw ingestion.")
        logger.info("Tip: Pass '--force-etl' if you wish to re-ingest and re-clean raw CSVs.")
        step_results.append(("ETL & Star Schema Staging", True, 0.0, "Cached"))
    else:
        success, elapsed, _ = run_step(1, "ETL Pipeline & Analytical Star Schema Construction", etl_run)
        step_results.append(("ETL & Star Schema Staging", success, elapsed, "Completed"))
        if not success:
            logger.error("ETL failed. Terminating pipeline.")
            sys.exit(1)

    # Step 2: Customer 360 Feature Mart
    from src.features.customer_360 import compute_customer_360
    success, elapsed, _ = run_step(2, "Customer 360 Behavioral Mart & Feature Engineering", compute_customer_360)
    step_results.append(("Customer 360 Features", success, elapsed, "Completed" if success else "Failed"))

    # Step 3: Customer Segmentation
    from src.models.segmentation import build_segmentation
    success, elapsed, _ = run_step(3, "Customer Segmentation (RFM Quintiles & K-Means Personas)", build_segmentation)
    step_results.append(("Customer Segmentation", success, elapsed, "Completed" if success else "Failed"))

    # Step 4: Retention & Survival Analysis
    from src.business.retention_survival import run_retention_analysis
    success, elapsed, _ = run_step(4, "Empirical Cadence Distribution & 45-Day Churn Survival", run_retention_analysis)
    step_results.append(("Retention & Survival", success, elapsed, "Completed" if success else "Failed"))

    # Step 5: Econometric Causal Inference
    from src.models.causal_analysis import run_causal_evaluation
    success, elapsed, _ = run_step(5, "Causal Attribution: PSM + Difference-in-Differences (ATT)", run_causal_evaluation)
    step_results.append(("Causal DiD & Placebo Test", success, elapsed, "Completed" if success else "Failed"))

    # Step 6: Predictive ML Response Classifier
    from src.models.predictive_response_model import build_predictive_models
    success, elapsed, _ = run_step(6, "Predictive Response ML (Out-of-Time XGBoost & Lift Deciles)", build_predictive_models)
    step_results.append(("Predictive XGBoost Response", success, elapsed, "Completed" if success else "Failed"))

    # Step 7: Strategic Uplift Targeting Engine
    from src.business.uplift_targeting import run_uplift_optimization
    success, elapsed, _ = run_step(7, "Strategic Uplift Engine (T-Learner & Unit Economics ROI)", run_uplift_optimization)
    step_results.append(("Uplift ROI Optimization", success, elapsed, "Completed" if success else "Failed"))

    # Step 8: Production SQL Analytics Queries
    from src.business.run_sql_analytics import run_all_queries
    success, elapsed, _ = run_step(8, "SQL Business Analytics Suite (12 Core Production Queries)", run_all_queries)
    step_results.append(("SQL Business Analytics", success, elapsed, "Completed" if success else "Failed"))

    # Step 9: Publication Figures & Charts
    from src.business.generate_eda_charts import generate_visualizations
    success, elapsed, _ = run_step(9, "Publication Visualization Suite (7 High-Res Charts)", generate_visualizations)
    step_results.append(("EDA Visualizations", success, elapsed, "Completed" if success else "Failed"))

    # Step 10: Power BI Export
    from powerbi.powerbi_export_data import export_powerbi_data
    success, elapsed, _ = run_step(10, "Power BI Data Export (Clean CSV Semantic Marts)", export_powerbi_data)
    step_results.append(("Power BI Marts Export", success, elapsed, "Completed" if success else "Failed"))

    total_time = time.time() - overall_start

    # Summary Table
    print("\n" + "=" * 80)
    print("                    PIPELINE EXECUTION SUMMARY MATRIX")
    print("=" * 80)
    print(f"{'Step':<35} | {'Status':<10} | {'Runtime (s)':<12} | {'Notes'}")
    print("-" * 80)
    for name, ok, t, note in step_results:
        status_str = "[PASS]" if ok else "[FAIL]"
        print(f"{name:<35} | {status_str:<10} | {t:>11.2f}s | {note}")
    print("=" * 80)
    print(f"Total Pipeline Runtime: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    print("=" * 80)

    # Verification of Key Outputs
    print("\n[VERIFIED OUTPUT ASSETS]:")
    print(f"  * Analytical DuckDB Warehouse: {db_path} ({os.path.getsize(db_path)/(1024*1024):.1f} MB)")
    print("  * Serialized ML Models:")
    models_dir = os.path.join(BASE_DIR, "models")
    if os.path.exists(models_dir):
        for mf in os.listdir(models_dir):
            if mf.endswith(".joblib"):
                print(f"      - models/{mf}")
    print("  * Generated Executive Reports:")
    rep_dir = os.path.join(BASE_DIR, "reports")
    if os.path.exists(rep_dir):
        for rf in os.listdir(rep_dir):
            if rf.endswith(".md"):
                print(f"      - reports/{rf}")
    print("  * Publication Figures:")
    fig_dir = os.path.join(BASE_DIR, "reports", "figures")
    if os.path.exists(fig_dir):
        for ff in os.listdir(fig_dir):
            if ff.endswith(".png"):
                print(f"      - reports/figures/{ff}")
    print("  * Power BI Marts:")
    pbi_dir = os.path.join(BASE_DIR, "powerbi", "data")
    if os.path.exists(pbi_dir):
        for pf in os.listdir(pbi_dir):
            if pf.endswith(".csv"):
                print(f"      - powerbi/data/{pf}")
    print("=" * 80)

    if launch_web:
        start_web_server()

def find_free_port(start_port=8505):
    import socket
    port = start_port
    while port < start_port + 50:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
        port += 1
    return start_port

def start_web_server():
    """Starts the Streamlit web dashboard."""
    app_path = os.path.join(BASE_DIR, "app.py")
    if not os.path.exists(app_path):
        logger.error(f"Streamlit app script '{app_path}' not found.")
        return
    port = find_free_port(8505)
    print(f"\nLaunching Interactive Streamlit Web Application on http://localhost:{port} ...")
    cmd = [sys.executable, "-m", "streamlit", "run", app_path, "--server.headless=true", f"--server.port={port}"]
    subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(
        description="Retail Promotion Intelligence & Campaign Optimization Master Pipeline Runner"
    )
    parser.add_argument("--all", action="store_true", help="Execute complete pipeline end-to-end")
    parser.add_argument("--force-etl", action="store_true", help="Force raw CSV re-ingestion into DuckDB")
    parser.add_argument("--web", action="store_true", help="Launch Streamlit interactive web dashboard")
    parser.add_argument("--step", type=str, choices=[
        "etl", "features", "segmentation", "retention", "causal",
        "predictive", "uplift", "analytics", "charts", "powerbi"
    ], help="Execute a single pipeline step")

    args = parser.parse_args()

    if args.web and not args.all and not args.step:
        start_web_server()
        return

    if args.step:
        print_banner()
        step_map = {
            "etl": ("ETL Pipeline", lambda: __import__("src.preprocessing.etl_pipeline", fromlist=["run_pipeline"]).run_pipeline()),
            "features": ("Customer 360 Mart", lambda: __import__("src.features.customer_360", fromlist=["compute_customer_360"]).compute_customer_360()),
            "segmentation": ("Customer Segmentation", lambda: __import__("src.models.segmentation", fromlist=["build_segmentation"]).build_segmentation()),
            "retention": ("Retention & Survival Analysis", lambda: __import__("src.business.retention_survival", fromlist=["run_retention_analysis"]).run_retention_analysis()),
            "causal": ("Causal Inference PSM+DiD", lambda: __import__("src.models.causal_analysis", fromlist=["run_causal_evaluation"]).run_causal_evaluation()),
            "predictive": ("Predictive Response ML", lambda: __import__("src.models.predictive_response_model", fromlist=["build_predictive_models"]).build_predictive_models()),
            "uplift": ("Uplift Optimization", lambda: __import__("src.business.uplift_targeting", fromlist=["run_uplift_optimization"]).run_uplift_optimization()),
            "analytics": ("SQL Business Analytics", lambda: __import__("src.business.run_sql_analytics", fromlist=["run_all_queries"]).run_all_queries()),
            "charts": ("Publication Charts", lambda: __import__("src.business.generate_eda_charts", fromlist=["generate_visualizations"]).generate_visualizations()),
            "powerbi": ("Power BI Export", lambda: __import__("powerbi.powerbi_export_data", fromlist=["export_powerbi_data"]).export_powerbi_data())
        }
        title, func = step_map[args.step]
        run_step(1, title, func)
        return

    # Default action: run full pipeline
    run_full_pipeline(skip_etl_if_db_exists=not args.force_etl, launch_web=args.web)

if __name__ == "__main__":
    main()
