from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from core.config import load_settings
from core.utils import ensure_parent
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records, load_raw_records
from retrieval.index import LocalEmbeddingIndex

try:
    from evaluation.testset import build_test_set
except ImportError:
    build_test_set = None

try:
    from evaluation.metrics import evaluate_pipeline
except ImportError:
    evaluate_pipeline = None

try:
    from observability.quality import build_freshness_report, run_data_quality_checks
except ImportError:
    run_data_quality_checks = None
    build_freshness_report = None

try:
    from observability.reporting import generate_phase1_report
except ImportError:
    generate_phase1_report = None


def main() -> None:
    """Xây dựng và điều phối Baseline Pipeline End-to-End cho Pha 1 (Do TV1 - Nguyễn Văn Hưng phụ trách)."""
    print("=== [Pha 1] Bắt đầu Baseline Data Pipeline End-to-End ===")
    settings = load_settings()

    # Step 1: Raw Data Ingestion
    print("\n[1/7] Ingestion Phase...")
    if settings.refresh_source or not settings.paths.raw_records_json.exists():
        print("Fetching fresh records from Crossref API...")
        raw_records = fetch_source_records(settings)
    else:
        print(f"Loading raw records from snapshot: {settings.paths.raw_records_json}")
        raw_records = load_raw_records(settings.paths.raw_records_json)
    print(f"-> Ingestion complete. Raw records count: {len(raw_records)}")

    # Step 2: Data Cleaning & Schema Normalization
    print("\n[2/7] Cleaning & Data Modeling Phase...")
    now = datetime.now(UTC)
    df = build_clean_dataframe(raw_records, run_date=now)
    ensure_parent(settings.paths.clean_csv)
    df.to_csv(settings.paths.clean_csv, index=False)
    ensure_parent(settings.paths.clean_json)
    df.to_json(settings.paths.clean_json, orient="records", indent=2)
    print(f"-> Cleaning complete. Cleaned records count: {len(df)}")
    print(f"   Cleaned CSV saved to: {settings.paths.clean_csv}")
    print(f"   Cleaned JSON saved to: {settings.paths.clean_json}")

    # Step 3: Vector Embedding & Indexing
    print("\n[3/7] Vector Indexing & ChromaDB Phase...")
    index = LocalEmbeddingIndex.build(
        df=df,
        settings=settings,
        embeddings_output_path=settings.paths.embeddings_json,
    )
    print(f"-> Indexing complete. Collection: {settings.baseline_collection_name}")
    print(f"   Embeddings manifest saved to: {settings.paths.embeddings_json}")

    # Step 4: Evaluation Test Set Generation
    print("\n[4/7] Evaluation Test Set Phase...")
    test_set_data = None
    if build_test_set is not None:
        try:
            test_set_data = build_test_set(df, settings.paths.eval_testset)
            print(f"-> Test set generated and saved to: {settings.paths.eval_testset}")
        except NotImplementedError:
            print("   [Notice] build_test_set is not implemented yet by Evaluation Owner (TV5).")
        except Exception as e:
            print(f"   [Warning] Test set generation error: {e}")
    else:
        print("   [Notice] build_test_set module unavailable.")

    # Step 5: RAG Evaluation & Scoring Execution
    print("\n[5/7] RAG Evaluation Phase...")
    metrics_bundle = None
    if settings.paths.eval_testset.exists() and evaluate_pipeline is not None:
        try:
            metrics_bundle = evaluate_pipeline(
                settings=settings,
                index=index,
                test_set_path=settings.paths.eval_testset,
                metrics_output_path=settings.paths.baseline_metrics,
                answers_output_path=settings.paths.baseline_answers,
            )
            print("-> Evaluation metrics calculated and saved:")
            print(f"   Metrics: {settings.paths.baseline_metrics}")
            print(f"   Answers: {settings.paths.baseline_answers}")
            print(f"   Summary: {metrics_bundle.summary}")
        except NotImplementedError:
            print("   [Notice] evaluate_pipeline is not implemented yet by Evaluation Owner (TV5).")
        except Exception as e:
            print(f"   [Warning] Evaluation failed: {e}")
    else:
        print("   [Notice] Skipping Evaluation (test set file not found or evaluate_pipeline unavailable).")

    # Step 6: Data Quality & Freshness Monitoring
    print("\n[6/7] Data Quality & Freshness Monitoring Phase...")
    quality_result = None
    freshness_result = None

    if run_data_quality_checks is not None:
        try:
            quality_result = run_data_quality_checks(df, settings, "phase1_quality_report")
            print("-> Quality checks complete.")
        except NotImplementedError:
            print("   [Notice] run_data_quality_checks is not implemented yet by Observability Owner (TV6).")
        except Exception as e:
            print(f"   [Warning] Quality check error: {e}")

    if build_freshness_report is not None:
        try:
            freshness_result = build_freshness_report(df, settings, settings.paths.freshness_report)
            print(f"-> Freshness report complete: {settings.paths.freshness_report}")
        except NotImplementedError:
            print("   [Notice] build_freshness_report is not implemented yet by Observability Owner (TV6).")
        except Exception as e:
            print(f"   [Warning] Freshness report error: {e}")

    # Step 7: Markdown Reporting
    print("\n[7/7] Markdown Reporting Phase...")
    if generate_phase1_report is not None:
        try:
            source_summary = {
                "source_api": settings.source_api,
                "raw_records_count": len(raw_records),
                "clean_records_count": len(df),
            }
            generate_phase1_report(
                report_path=settings.paths.baseline_report,
                source_summary=source_summary,
                metrics=metrics_bundle.summary if metrics_bundle else {},
                quality=quality_result or {},
                freshness=freshness_result or {},
            )
            print(f"-> Phase 1 Report generated at: {settings.paths.baseline_report}")
        except NotImplementedError:
            print("   [Notice] generate_phase1_report is not implemented yet by Observability Owner (TV6).")
        except Exception as e:
            print(f"   [Warning] Phase 1 report generation error: {e}")

    print("\n=== [Pha 1] Baseline Data Pipeline hoàn thành thành công! ===")


if __name__ == "__main__":
    main()

