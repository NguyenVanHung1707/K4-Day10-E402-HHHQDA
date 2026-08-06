# Phase 1: Baseline Data Report

## 1. Source Summary
```json
{
  "source_api": "Crossref REST API",
  "raw_records_count": 24,
  "clean_records_count": 24
}
```

## 2. Evaluation Metrics
```json
{
  "samples": 24,
  "retrieval_hit_rate": 1.0,
  "mean_token_f1": 0.27048090276528997,
  "judge_accuracy": 0.041666666666666664,
  "mean_judge_score": 1.0833333333333333,
  "ragas": {
    "skipped": "Set RUN_RAGAS=1 to enable the slower Ragas pass."
  }
}
```

## 3. Data Quality Checks
- Total Checks: 5
- Passed Checks: 5

```json
[
  {
    "check_name": "row_count",
    "dimension": "Completeness",
    "passed": true,
    "score": 1.0,
    "details": "Total rows: 24"
  },
  {
    "check_name": "paper_id_validity",
    "dimension": "Validity",
    "passed": true,
    "score": 1.0,
    "details": "Nulls: 0, Uniques: 24/24"
  },
  {
    "check_name": "title_completeness",
    "dimension": "Completeness",
    "passed": true,
    "score": 1.0,
    "details": "Null or empty titles: 0"
  },
  {
    "check_name": "summary_validity",
    "dimension": "Validity",
    "passed": true,
    "score": 1.0,
    "details": "Valid summaries: 24/24"
  },
  {
    "check_name": "freshness_check",
    "dimension": "Freshness",
    "passed": true,
    "score": 1.0,
    "details": "Fresh rows: 24/24"
  }
]
```

## 4. Data Freshness
- Total Rows: 24
- Stale Rows: 0
- Is Fresh: True

```json
{
  "latest_published": "2026-08-01T00:00:00",
  "oldest_published": "2026-02-12T00:00:00",
  "stale_rows": 0,
  "total_rows": 24,
  "is_fresh": true,
  "freshness_threshold_days": 180
}
```
