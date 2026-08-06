from __future__ import annotations

from datetime import UTC, datetime
from html import unescape
import re
import unicodedata

import pandas as pd

from ingestion.crossref import PaperRecord


CLEAN_COLUMNS = [
    "paper_id", "title", "summary", "authors_joined", "categories_joined",
    "primary_category", "published", "updated", "age_days", "summary_chars",
    "text_for_embedding", "abs_url", "pdf_url",
]


def _clean_text(value: object) -> str:
    if value is None:
        return ""
    text = re.sub(r"<[^>]*>", " ", unescape(str(value)))
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.split())


def _value(record: PaperRecord | dict, field: str, default: object = "") -> object:
    if isinstance(record, dict):
        return record.get(field, default)
    return getattr(record, field, default)


def _clean_list(value: object) -> list[str]:
    values = [value] if isinstance(value, str) else (value or [])
    result: list[str] = []
    seen: set[str] = set()
    for item in values:
        cleaned = _clean_text(item)
        if cleaned and cleaned.casefold() not in seen:
            result.append(cleaned)
            seen.add(cleaned.casefold())
    return result


def _parse_date(value: object) -> datetime | None:
    try:
        parsed = pd.to_datetime(_clean_text(value), errors="raise", utc=True)
    except (TypeError, ValueError, OverflowError):
        return None
    if pd.isna(parsed):
        return None
    return parsed.to_pydatetime().astimezone(UTC)


def build_clean_dataframe(
    records: list[PaperRecord] | list[dict], run_date: datetime
) -> pd.DataFrame:
    """Clean raw records into the shared, embedding-ready schema."""
    if not isinstance(run_date, datetime):
        raise TypeError("run_date must be a datetime instance")
    evaluated_at = (
        run_date.replace(tzinfo=UTC)
        if run_date.tzinfo is None
        else run_date.astimezone(UTC)
    )
    rows: list[dict[str, object]] = []

    for record in records:
        paper_id = _clean_text(_value(record, "paper_id"))
        title = _clean_text(_value(record, "title"))
        summary = _clean_text(_value(record, "summary"))
        published = _parse_date(_value(record, "published"))
        if not paper_id or not title or not summary or published is None:
            continue

        authors = ", ".join(_clean_list(_value(record, "authors", [])))
        categories_list = _clean_list(_value(record, "categories", []))
        categories = ", ".join(categories_list)
        primary = _clean_text(_value(record, "primary_category"))
        primary = primary or (categories_list[0] if categories_list else "")
        updated = _parse_date(_value(record, "updated")) or published
        age_days = max(0, (evaluated_at.date() - published.date()).days)
        rows.append({
            "paper_id": paper_id,
            "title": title,
            "summary": summary,
            "authors_joined": authors,
            "categories_joined": categories,
            "primary_category": primary,
            "published": published.date().isoformat(),
            "updated": updated.date().isoformat(),
            "age_days": age_days,
            "summary_chars": len(summary),
            "text_for_embedding": (
                f"Title: {title} | Summary: {summary} | "
                f"Authors: {authors} | Subject: {categories or primary}"
            ),
            "abs_url": _clean_text(_value(record, "abs_url")),
            "pdf_url": _clean_text(_value(record, "pdf_url")),
        })

    if not rows:
        return pd.DataFrame(columns=CLEAN_COLUMNS)
    dataframe = pd.DataFrame(rows, columns=CLEAN_COLUMNS)
    dataframe = dataframe.drop_duplicates("paper_id", keep="first")
    dataframe = dataframe.sort_values(
        ["published", "paper_id"], ascending=[False, True], kind="stable"
    ).reset_index(drop=True)
    return dataframe.astype({"age_days": "int64", "summary_chars": "int64"})

def clean_repaired_data(
    raw_records: list[PaperRecord] | list[dict], run_date: datetime
) -> pd.DataFrame:
    """Rebuild the clean dataset from the trusted raw snapshot.

    Repair starts from raw records instead of modifying corrupted clean data,
    so every derived field is recreated from the source of truth.
    """
    repaired = build_clean_dataframe(raw_records, run_date=run_date)

    if list(repaired.columns) != CLEAN_COLUMNS:
        raise ValueError(
            "Repaired dataset violates the clean schema contract: "
            f"expected {CLEAN_COLUMNS}, got {list(repaired.columns)}"
        )
    if not repaired.empty:
        invalid_rows = (
            repaired["paper_id"].eq("")
            | repaired["title"].eq("")
            | repaired["summary"].eq("")
            | repaired["paper_id"].duplicated(keep=False)
        )
        if invalid_rows.any():
            raise ValueError("Repaired dataset contains invalid or duplicate records")

    return repaired
