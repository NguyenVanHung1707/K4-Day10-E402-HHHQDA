from __future__ import annotations

from datetime import UTC, datetime
import sys

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from core.config import load_settings
from core.utils import ensure_parent, read_json
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from ingestion.crossref import fetch_source_records, load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_corruption_report
from retrieval.index import LocalEmbeddingIndex


def main() -> None:
    """Điều phối toàn bộ luồng Pha 2 (Corruption -> Re-evaluate -> Repair -> Compare Flow) do TV1 (Trưởng nhóm - Nguyễn Văn Hưng) phụ trách."""
    print("=== [Pha 2] Bắt đầu Corruption, Repair và Comparison Flow End-to-End ===")
    settings = load_settings()

    # Step 0: Load Baseline Artifacts
    print("\n[0/7] Loading Baseline Artifacts...")
    if not settings.paths.clean_json.exists():
        raise RuntimeError("Cleaned baseline dataset missing! Please run Phase 1 baseline first.")

    clean_df = pd.read_json(settings.paths.clean_json)
    print(f"-> Baseline clean dataset loaded: {len(clean_df)} records.")

    # Ensure evaluation test set exists
    if not settings.paths.eval_testset.exists():
        print("-> Generating Evaluation Test Set...")
        build_test_set(clean_df, settings.paths.eval_testset)
        print(f"-> Evaluation test set generated at: {settings.paths.eval_testset}")

    baseline_metrics = {}
    if settings.paths.baseline_metrics.exists():
        baseline_metrics = read_json(settings.paths.baseline_metrics)
        print(f"-> Baseline metrics loaded: {settings.paths.baseline_metrics}")


    # Step 1: Corrupt Clean Data
    print("\n[1/7] Corrupting Clean Dataset...")
    corrupted_df = corrupt_clean_dataframe(clean_df, settings.paths.corruption_log)
    ensure_parent(settings.paths.corrupted_clean_csv)
    corrupted_df.to_csv(settings.paths.corrupted_clean_csv, index=False)
    ensure_parent(settings.paths.corrupted_clean_json)
    corrupted_df.to_json(settings.paths.corrupted_clean_json, orient="records", indent=2)
    print(f"-> Corrupted dataset created: {len(corrupted_df)} records.")
    print(f"   Corrupted CSV saved to: {settings.paths.corrupted_clean_csv}")
    print(f"   Corruption log saved to: {settings.paths.corruption_log}")

    # Step 2: Re-indexing & Evaluating Corrupted Data
    print("\n[2/7] Re-indexing Corrupted Data & Re-evaluating Agent...")
    corrupted_index = LocalEmbeddingIndex.build(
        df=corrupted_df,
        settings=settings,
        embeddings_output_path=settings.paths.corrupted_embeddings_json,
    )
    print(f"-> Corrupted vector collection created: {settings.corrupted_collection_name}")

    corrupted_eval_bundle = evaluate_pipeline(
        settings=settings,
        index=corrupted_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.corrupted_metrics,
        answers_output_path=settings.paths.corrupted_answers,
    )
    print("-> Corrupted metrics evaluated and saved:")
    print(f"   Summary: {corrupted_eval_bundle.summary}")

    # Step 3: Observability on Corrupted Data
    print("\n[3/7] Running Quality & Freshness Monitoring on Corrupted Data...")
    corrupted_quality = run_data_quality_checks(corrupted_df, settings, "corrupted_quality")
    corrupted_freshness = build_freshness_report(
        corrupted_df, settings, settings.paths.quality_dir / "corrupted_freshness.json"
    )
    print(f"-> Corrupted Quality: {corrupted_quality.get('passed_checks', 0)}/{corrupted_quality.get('total_checks', 0)} checks passed.")

    # Step 4: Repair Dataset from Raw Source
    print("\n[4/7] Repairing Dataset from Raw Source...")
    if settings.paths.raw_records_json.exists():
        raw_records = load_raw_records(settings.paths.raw_records_json)
    else:
        raw_records = fetch_source_records(settings)

    repaired_df = build_clean_dataframe(raw_records, run_date=datetime.now(UTC))
    ensure_parent(settings.paths.repaired_clean_csv)
    repaired_df.to_csv(settings.paths.repaired_clean_csv, index=False)
    ensure_parent(settings.paths.repaired_clean_json)
    repaired_df.to_json(settings.paths.repaired_clean_json, orient="records", indent=2)
    print(f"-> Repaired dataset created from raw records: {len(repaired_df)} records.")
    print(f"   Repaired CSV saved to: {settings.paths.repaired_clean_csv}")

    # Step 5: Re-indexing & Evaluating Repaired Data
    print("\n[5/7] Re-indexing Repaired Data & Re-evaluating Agent...")
    repaired_index = LocalEmbeddingIndex.build(
        df=repaired_df,
        settings=settings,
        embeddings_output_path=settings.paths.repaired_embeddings_json,
    )
    print(f"-> Repaired vector collection created: {settings.repaired_collection_name}")

    repaired_eval_bundle = evaluate_pipeline(
        settings=settings,
        index=repaired_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.repaired_metrics,
        answers_output_path=settings.paths.repaired_answers,
    )
    print("-> Repaired metrics evaluated and saved:")
    print(f"   Summary: {repaired_eval_bundle.summary}")

    # Step 6: Observability on Repaired Data
    print("\n[6/7] Running Quality & Freshness Monitoring on Repaired Data...")
    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality")
    repaired_freshness = build_freshness_report(
        repaired_df, settings, settings.paths.quality_dir / "repaired_freshness.json"
    )
    print(f"-> Repaired Quality: {repaired_quality.get('passed_checks', 0)}/{repaired_quality.get('total_checks', 0)} checks passed.")

    # Step 7: Generating Comparison Report
    print("\n[7/7] Generating Comparison Report (Baseline vs Corrupted vs Repaired)...")
    generate_corruption_report(
        report_path=settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_eval_bundle.summary,
        repaired_metrics=repaired_eval_bundle.summary,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness,
    )
    print(f"-> Comparison report generated at: {settings.paths.comparison_report}")

    print("\n=== [Pha 2] Corruption Flow & Project Acceptance hoàn thành xuất sắc! ===")


if __name__ == "__main__":
    main()

