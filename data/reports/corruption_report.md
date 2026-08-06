# Phase 2: Corruption & Repair Comparison Report

## 1. Metrics Comparison

| Metric | Baseline | Corrupted | Repaired |
|---|---|---|---|
| judge_accuracy | 0.9 | 0.0 | 0.041666666666666664 |
| mean_judge_score | 4.5 | 1 | 1.0833333333333333 |
| mean_token_f1 | 0.842 | 0.21882245848688225 | 0.27048090276528997 |
| ragas | {'answer_relevancy': 0.88, 'context_precision': 0.91, 'context_recall': 0.89, 'faithfulness': 0.93} | {'skipped': 'Set RUN_RAGAS=1 to enable the slower Ragas pass.'} | {'skipped': 'Set RUN_RAGAS=1 to enable the slower Ragas pass.'} |
| retrieval_hit_rate | 0.9 | 0.875 | 1.0 |
| samples | 10 | 24 | 24 |

## 2. Data Quality Comparison

| State | Total Checks | Passed Checks |
|---|---|---|
| Baseline (from Phase 1) | N/A | N/A |
| Corrupted | 5 | 2 |
| Repaired | 5 | 5 |

### Corrupted Checks Details
```json
[
  {
    "check_name": "row_count",
    "dimension": "Completeness",
    "passed": true,
    "score": 1.0,
    "details": "Total rows: 25"
  },
  {
    "check_name": "paper_id_validity",
    "dimension": "Validity",
    "passed": false,
    "score": 0.88,
    "details": "Nulls: 0, Uniques: 22/25"
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
    "passed": false,
    "score": 0.96,
    "details": "Valid summaries: 24/25"
  },
  {
    "check_name": "freshness_check",
    "dimension": "Freshness",
    "passed": false,
    "score": 0.92,
    "details": "Fresh rows: 23/25"
  }
]
```

### Repaired Checks Details
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

## 3. Freshness Comparison

| State | Total Rows | Stale Rows | Is Fresh |
|---|---|---|---|
| Corrupted | 25 | 2 | False |
| Repaired | 24 | 0 | True |

