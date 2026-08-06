from __future__ import annotations

import numpy as np
import pandas as pd

from core.config import CorruptionLogSchema
from core.utils import write_json, now_utc


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    """Simulate nhieu dang data corruption."""
    if df.empty:
        return df

    corrupted_df = df.copy()
    logs = []
    
    if "published" in corrupted_df.columns:
        corrupted_df["published_dt"] = pd.to_datetime(corrupted_df["published"], errors="coerce")
        corrupted_df = corrupted_df.sort_values("published_dt", ascending=False)
        drop_count = int(len(corrupted_df) * 0.1)
        if drop_count > 0:
            corrupted_df = corrupted_df.iloc[drop_count:]
            logs.append(CorruptionLogSchema(
                corruption_type="drop_latest_records",
                affected_count=drop_count,
                timestamp=now_utc().isoformat(),
                description=f"Dropped top {drop_count} newest records."
            ).__dict__)
        if "published_dt" in corrupted_df.columns:
            corrupted_df = corrupted_df.drop(columns=["published_dt"])

    corrupted_df = corrupted_df.sample(frac=1, random_state=42).reset_index(drop=True)
    n_rows = len(corrupted_df)

    if "summary" in corrupted_df.columns:
        blank_count = int(n_rows * 0.05)
        if blank_count > 0:
            indices_to_blank = np.random.choice(n_rows, blank_count, replace=False)
            corrupted_df.loc[indices_to_blank, "summary"] = ""
            logs.append(CorruptionLogSchema(
                corruption_type="blank_summary",
                affected_count=blank_count,
                timestamp=now_utc().isoformat(),
                description=f"Blanked summary for {blank_count} records."
            ).__dict__)

    if "summary" in corrupted_df.columns:
        noise_count = int(n_rows * 0.05)
        if noise_count > 0:
            indices_to_noise = np.random.choice(n_rows, noise_count, replace=False)
            corrupted_df.loc[indices_to_noise, "summary"] = corrupted_df.loc[indices_to_noise, "summary"].astype(str) + " [NOISE]"
            logs.append(CorruptionLogSchema(
                corruption_type="inject_noise",
                affected_count=noise_count,
                timestamp=now_utc().isoformat(),
                description=f"Injected noise into summary for {noise_count} records."
            ).__dict__)

    if "title" in corrupted_df.columns:
        trunc_count = int(n_rows * 0.05)
        if trunc_count > 0:
            indices_to_trunc = np.random.choice(n_rows, trunc_count, replace=False)
            corrupted_df.loc[indices_to_trunc, "title"] = corrupted_df.loc[indices_to_trunc, "title"].astype(str).str[:10]
            logs.append(CorruptionLogSchema(
                corruption_type="truncate_title",
                affected_count=trunc_count,
                timestamp=now_utc().isoformat(),
                description=f"Truncated title for {trunc_count} records."
            ).__dict__)

    if "published" in corrupted_df.columns:
        stale_count = int(n_rows * 0.1)
        if stale_count > 0:
            indices_to_stale = np.random.choice(n_rows, stale_count, replace=False)
            try:
                stale_dates = pd.to_datetime(corrupted_df.loc[indices_to_stale, "published"], errors="coerce") - pd.DateOffset(years=3)
                corrupted_df.loc[indices_to_stale, "published"] = stale_dates.dt.strftime("%Y-%m-%dT%H:%M:%S").fillna("2020-01-01T00:00:00")
                if "age_days" in corrupted_df.columns:
                    corrupted_df.loc[indices_to_stale, "age_days"] = corrupted_df.loc[indices_to_stale, "age_days"] + (3 * 365)
                
                logs.append(CorruptionLogSchema(
                    corruption_type="stale_publication_date",
                    affected_count=stale_count,
                    timestamp=now_utc().isoformat(),
                    description=f"Made published date 3 years older for {stale_count} records."
                ).__dict__)
            except Exception as e:
                pass

    if n_rows > 0:
        dup_count = min(3, n_rows)
        indices_to_dup = np.random.choice(n_rows, dup_count, replace=False)
        duplicates = corrupted_df.loc[indices_to_dup].copy()
        corrupted_df = pd.concat([corrupted_df, duplicates], ignore_index=True)
        logs.append(CorruptionLogSchema(
            corruption_type="add_duplicates",
            affected_count=dup_count,
            timestamp=now_utc().isoformat(),
            description=f"Added {dup_count} duplicate rows."
        ).__dict__)

    if "text_for_embedding" in corrupted_df.columns:
        authors_col = corrupted_df.get("authors_joined", pd.Series([""]*len(corrupted_df)))
        cat_col = corrupted_df.get("categories_joined", pd.Series([""]*len(corrupted_df)))
        
        corrupted_df["text_for_embedding"] = (
            "Title: " + corrupted_df["title"].astype(str).fillna("") + "\n" +
            "Authors: " + authors_col.astype(str).fillna("") + "\n" +
            "Categories: " + cat_col.astype(str).fillna("") + "\n" +
            "Summary: " + corrupted_df["summary"].astype(str).fillna("")
        )

    write_json(output_log_path, logs)
    return corrupted_df
