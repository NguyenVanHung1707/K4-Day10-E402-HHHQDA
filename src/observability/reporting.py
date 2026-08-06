from __future__ import annotations

import json
from typing import Any

from core.utils import write_text


def _format_dict(d: dict[str, Any] | list[Any]) -> str:
    return json.dumps(d, indent=2)


def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """Viet markdown report cho baseline phase."""
    
    report_content = f"""# Phase 1: Baseline Data Report

## 1. Source Summary
```json
{_format_dict(source_summary)}
```

## 2. Evaluation Metrics
```json
{_format_dict(metrics)}
```

## 3. Data Quality Checks
- Total Checks: {quality.get('total_checks', 0)}
- Passed Checks: {quality.get('passed_checks', 0)}

```json
{_format_dict(quality.get('checks', []))}
```

## 4. Data Freshness
- Total Rows: {freshness.get('total_rows', 0)}
- Stale Rows: {freshness.get('stale_rows', 0)}
- Is Fresh: {freshness.get('is_fresh', False)}

```json
{_format_dict(freshness)}
```
"""
    write_text(report_path, report_content)


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    """Viet markdown report so sanh baseline/corrupted/repaired."""
    
    report_content = f"""# Phase 2: Corruption & Repair Comparison Report

## 1. Metrics Comparison

| Metric | Baseline | Corrupted | Repaired |
|---|---|---|---|
"""
    
    all_keys = set(baseline_metrics.keys()) | set(corrupted_metrics.keys()) | set(repaired_metrics.keys())
    for k in sorted(all_keys):
        b_val = baseline_metrics.get(k, "N/A")
        c_val = corrupted_metrics.get(k, "N/A")
        r_val = repaired_metrics.get(k, "N/A")
        report_content += f"| {k} | {b_val} | {c_val} | {r_val} |\n"

    report_content += f"""
## 2. Data Quality Comparison

| State | Total Checks | Passed Checks |
|---|---|---|
| Baseline (from Phase 1) | N/A | N/A |
| Corrupted | {corrupted_quality.get('total_checks', 0)} | {corrupted_quality.get('passed_checks', 0)} |
| Repaired | {repaired_quality.get('total_checks', 0)} | {repaired_quality.get('passed_checks', 0)} |

### Corrupted Checks Details
```json
{_format_dict(corrupted_quality.get('checks', []))}
```

### Repaired Checks Details
```json
{_format_dict(repaired_quality.get('checks', []))}
```

## 3. Freshness Comparison

| State | Total Rows | Stale Rows | Is Fresh |
|---|---|---|---|
| Corrupted | {corrupted_freshness.get('total_rows', 0)} | {corrupted_freshness.get('stale_rows', 0)} | {corrupted_freshness.get('is_fresh', False)} |
| Repaired | {repaired_freshness.get('total_rows', 0)} | {repaired_freshness.get('stale_rows', 0)} | {repaired_freshness.get('is_fresh', False)} |

"""
    write_text(report_path, report_content)
