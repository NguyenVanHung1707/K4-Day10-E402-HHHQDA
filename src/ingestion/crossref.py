from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.config import Settings


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


import re
import time
import requests
from dataclasses import asdict

from core.utils import normalize_whitespace, safe_slug, write_json, read_json


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """Parse Crossref payload thanh list PaperRecord.

    Pseudo-code:
    1. Duyet `payload["message"]["items"]`.
    2. Lay DOI, title, abstract, authors, subject, dates, URLs.
    3. Chuan hoa text va bo record khong hop le.
    4. Tra ve list `PaperRecord`.
    """
    if not payload or "message" not in payload or "items" not in payload["message"]:
        return []

    records = []
    items = payload["message"]["items"]

    for item in items:
        # Extract DOI
        doi = item.get("DOI", "")
        if not doi:
            continue

        # Extract Title
        titles = item.get("title", [])
        title = normalize_whitespace(titles[0]) if titles else ""

        # Extract Summary/Abstract and remove JATS XML/HTML tags
        abstract_raw = item.get("abstract", "")
        if abstract_raw:
            abstract_clean = re.sub(r"<[^>]+>", "", abstract_raw)
            summary = normalize_whitespace(abstract_clean)
        else:
            summary = ""

        # Discard invalid records (must have non-empty title and abstract)
        if not title or not summary:
            continue

        paper_id = safe_slug(doi)

        # Extract Authors
        authors = []
        for aut in item.get("author", []):
            given = aut.get("given", "").strip()
            family = aut.get("family", "").strip()
            name = aut.get("name", "").strip()
            if given and family:
                authors.append(normalize_whitespace(f"{given} {family}"))
            elif family:
                authors.append(normalize_whitespace(family))
            elif given:
                authors.append(normalize_whitespace(given))
            elif name:
                authors.append(normalize_whitespace(name))

        # Extract Categories
        categories = item.get("subject", [])
        categories = [normalize_whitespace(cat) for cat in categories if cat]
        primary_category = categories[0] if categories else ""

        # Extract Dates
        def extract_date(date_dict: dict | None) -> str:
            if not date_dict or "date-parts" not in date_dict:
                return ""
            parts = date_dict["date-parts"]
            if not parts or not isinstance(parts, list):
                return ""
            inner = parts[0]
            if not inner or not isinstance(inner, list):
                return ""
            year = inner[0] if len(inner) > 0 else None
            month = inner[1] if len(inner) > 1 else 1
            day = inner[2] if len(inner) > 2 else 1
            if year is None:
                return ""
            try:
                return f"{year:04d}-{month:02d}-{day:02d}"
            except Exception:
                return f"{year}-{month}-{day}"

        published = ""
        for field in ["published", "published-online", "published-print", "issued", "created"]:
            d_dict = item.get(field)
            if d_dict:
                d_str = extract_date(d_dict)
                if d_str:
                    published = d_str
                    break

        updated = ""
        for field in ["deposited", "created", "indexed"]:
            d_dict = item.get(field)
            if d_dict:
                d_str = extract_date(d_dict)
                if d_str:
                    updated = d_str
                    break
        if not updated:
            updated = published

        if not published:
            continue

        # Extract URLs
        abs_url = item.get("URL", "")
        pdf_url = ""
        for link_item in item.get("link", []):
            url = link_item.get("URL", "")
            content_type = link_item.get("content-type", "")
            if "pdf" in content_type.lower() or "pdf" in url.lower():
                pdf_url = url
                break

        comment = str(item.get("comment", ""))

        records.append(
            PaperRecord(
                paper_id=paper_id,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=published,
                updated=updated,
                abs_url=abs_url,
                pdf_url=pdf_url,
                comment=comment,
            )
        )

    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Goi source API, luu raw response, parse thanh records.

    Pseudo-code:
    1. Tao params tu `settings.source_query`, `settings.source_filter`, `settings.max_results`.
    2. Goi API voi retry cho cac status code nhu 429/503.
    3. Luu raw response vao `settings.paths.raw_api_response`.
    4. Parse payload bang `parse_crossref_payload`.
    5. Luu records vao `settings.paths.raw_records_json`.
    """
    url = "https://api.crossref.org/works"
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results,
    }
    headers = {
        "User-Agent": "DataPipelineLab/1.0 (mailto:student-lab@example.com)"
    }

    max_retries = 5
    backoff_factor = 2.0
    response = None

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            if response.status_code == 200:
                break
            elif response.status_code in {429, 503}:
                sleep_time = backoff_factor ** attempt
                print(f"Received status code {response.status_code}. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                response.raise_for_status()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            sleep_time = backoff_factor ** attempt
            print(f"Request failed: {e}. Retrying in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

    if response is None or response.status_code != 200:
        raise RuntimeError(f"Failed to fetch data from Crossref API after {max_retries} attempts.")

    payload = response.json()

    # Save raw API response
    write_json(settings.paths.raw_api_response, payload)

    # Parse payload
    records = parse_crossref_payload(payload)

    # Save raw records to JSON
    records_dict = [asdict(rec) for rec in records]
    write_json(settings.paths.raw_records_json, records_dict)

    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Doc JSON snapshot va map thanh `PaperRecord`."""
    if not path.exists():
        return []
    records_data = read_json(path)
    return [PaperRecord(**rec) for rec in records_data]
