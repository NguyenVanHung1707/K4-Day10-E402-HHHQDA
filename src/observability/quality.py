from __future__ import annotations

from typing import Any

import pandas as pd

from core.config import DataQualityCheckSchema, Settings
from core.utils import write_json


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Tao bo data quality checks."""
    checks = []
    
    row_count = len(df)
    checks.append(DataQualityCheckSchema(
        check_name="row_count",
        dimension="Completeness",
        passed=row_count > 0,
        score=1.0 if row_count > 0 else 0.0,
        details=f"Total rows: {row_count}"
    ).__dict__)
    
    if "paper_id" in df.columns:
        null_count = df["paper_id"].isnull().sum()
        unique_count = df["paper_id"].nunique()
        passed = (null_count == 0) and (unique_count == row_count)
        score = 1.0 - (null_count + (row_count - unique_count)) / row_count if row_count > 0 else 0.0
        checks.append(DataQualityCheckSchema(
            check_name="paper_id_validity",
            dimension="Validity",
            passed=bool(passed),
            score=float(score),
            details=f"Nulls: {null_count}, Uniques: {unique_count}/{row_count}"
        ).__dict__)
    
    if "title" in df.columns:
        null_title_count = df["title"].isnull().sum()
        empty_title_count = (df["title"].astype(str).str.strip() == "").sum()
        invalid_titles = null_title_count + empty_title_count
        passed = (invalid_titles == 0)
        score = 1.0 - (invalid_titles / row_count) if row_count > 0 else 0.0
        checks.append(DataQualityCheckSchema(
            check_name="title_completeness",
            dimension="Completeness",
            passed=bool(passed),
            score=float(score),
            details=f"Null or empty titles: {invalid_titles}"
        ).__dict__)
        
    if "summary" in df.columns:
        valid_summary_mask = df["summary"].notnull() & (df["summary"].astype(str).str.len() > 10)
        valid_summary_count = int(valid_summary_mask.sum())
        passed = valid_summary_count == row_count
        score = float(valid_summary_count / row_count) if row_count > 0 else 0.0
        checks.append(DataQualityCheckSchema(
            check_name="summary_validity",
            dimension="Validity",
            passed=bool(passed),
            score=score,
            details=f"Valid summaries: {valid_summary_count}/{row_count}"
        ).__dict__)

    if "age_days" in df.columns:
        fresh_mask = df["age_days"] <= settings.freshness_threshold_days
        fresh_count = int(fresh_mask.sum())
        passed = bool(fresh_count == row_count)
        score = float(fresh_count / row_count) if row_count > 0 else 0.0
        checks.append(DataQualityCheckSchema(
            check_name="freshness_check",
            dimension="Freshness",
            passed=passed,
            score=score,
            details=f"Fresh rows: {fresh_count}/{row_count}"
        ).__dict__)
        
    payload = {
        "report_name": report_name,
        "total_checks": len(checks),
        "passed_checks": sum(1 for c in checks if c["passed"]),
        "checks": checks
    }
    
    out_path = settings.paths.quality_dir / f"{report_name}.json"
    write_json(out_path, payload)
    
    return payload


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    """Tong hop freshness report."""
    if df.empty or "published" not in df.columns or "age_days" not in df.columns:
        return {}
        
    published_dt = pd.to_datetime(df["published"], errors="coerce")
    
    latest = published_dt.max()
    oldest = published_dt.min()
    
    stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum())
    total_rows = len(df)
    is_fresh = stale_rows == 0
    
    payload = {
        "latest_published": latest.isoformat() if pd.notnull(latest) else None,
        "oldest_published": oldest.isoformat() if pd.notnull(oldest) else None,
        "stale_rows": stale_rows,
        "total_rows": total_rows,
        "is_fresh": bool(is_fresh),
        "freshness_threshold_days": settings.freshness_threshold_days
    }
    
    write_json(report_path, payload)
    return payload
