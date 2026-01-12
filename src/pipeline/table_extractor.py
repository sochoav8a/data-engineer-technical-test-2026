from __future__ import annotations

import hashlib
from pathlib import Path


def _tables_from_camelot(pdf_path: Path, pages: list[int]) -> list[dict[str, str]]:
    tables: list[dict[str, str]] = []
    if not pages:
        return tables
    pages_str = ",".join(str(p) for p in pages)
    try:
        import camelot
    except Exception:
        return tables

    for flavor in ("lattice", "stream"):
        try:
            extracted = camelot.read_pdf(str(pdf_path), pages=pages_str, flavor=flavor)
        except Exception:
            continue
        for table in extracted:
            try:
                df = table.df
                text = df.to_csv(index=False)
            except Exception:
                continue
            if text.strip():
                tables.append(
                    {
                        "page": str(table.page),
                        "method": f"camelot_{flavor}",
                        "text": text.strip(),
                    }
                )
    return tables


def _tables_from_pdfplumber(pdf_path: Path, page_indices: list[int]) -> list[dict[str, str]]:
    tables: list[dict[str, str]] = []
    if not page_indices:
        return tables
    try:
        import pdfplumber
    except Exception:
        return tables

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for idx in page_indices:
                if idx < 0 or idx >= len(pdf.pages):
                    continue
                page = pdf.pages[idx]
                extracted = page.extract_tables() or []
                for table in extracted:
                    rows = []
                    for row in table:
                        rows.append("\t".join(cell or "" for cell in row))
                    text = "\n".join(rows).strip()
                    if text:
                        tables.append(
                            {
                                "page": str(idx + 1),
                                "method": "pdfplumber",
                                "text": text,
                            }
                        )
    except Exception:
        return tables
    return tables


SECTION_TABLE_KEYWORDS = {
    "resources": [
        "mineral resource",
        "resource estimate",
        "measured",
        "indicated",
        "inferred",
        "measured and indicated",
        "measured + indicated",
        "m+i",
        "tonnes",
        "kt",
        "mt",
        "grade",
        "g/t",
        "oz",
        "contained",
        "au",
        "ag",
        "cu",
    ],
    "reserves": [
        "mineral reserve",
        "reserve estimate",
        "proven",
        "probable",
        "proven and probable",
        "proven + probable",
        "p&p",
        "tonnes",
        "kt",
        "mt",
        "grade",
        "g/t",
        "oz",
        "contained",
        "au",
        "ag",
        "cu",
    ],
    "economics": [
        "capital",
        "operating",
        "capex",
        "opex",
        "npv",
        "irr",
        "payback",
        "cash flow",
        "sustaining",
        "initial",
        "pre-tax",
        "after-tax",
        "life of mine",
        "mine life",
        "usd",
        "us$",
        "$",
    ],
}


def _table_score(text: str, keywords: list[str]) -> float:
    lower = text.lower()
    hits = sum(1 for kw in keywords if kw in lower)
    numeric = sum(1 for ch in text if ch.isdigit())
    rows = text.splitlines()
    dense_rows = sum(1 for row in rows if row.count(",") >= 2 or row.count("\t") >= 2)
    return hits * 3 + dense_rows + min(numeric / 50, 5)


def filter_tables_for_section(
    tables: list[dict[str, str]],
    section: str,
    max_tables: int = 6,
) -> list[dict[str, str]]:
    keywords = SECTION_TABLE_KEYWORDS.get(section, [])
    seen: dict[str, tuple[float, dict[str, str]]] = {}
    for table in tables:
        text = (table.get("text") or "").strip()
        if not text:
            continue
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if digest in seen:
            continue
        # Score tables to prioritize high-signal rows and avoid flooding the LLM context.
        score = _table_score(text, keywords)
        seen[digest] = (score, table)

    scored = sorted(seen.values(), key=lambda item: item[0], reverse=True)
    if not scored:
        return []

    filtered = [table for score, table in scored if score > 0]
    if not filtered:
        filtered = [table for _, table in scored]
    return filtered[:max_tables]


def extract_tables_for_pages(pdf_path: Path, page_indices: list[int]) -> list[dict[str, str]]:
    if not page_indices:
        return []
    pages_one_based = sorted({idx + 1 for idx in page_indices})
    tables = []
    tables.extend(_tables_from_camelot(pdf_path, pages_one_based))
    tables.extend(_tables_from_pdfplumber(pdf_path, page_indices))
    return tables


def build_table_context(
    tables: list[dict[str, str]], max_rows: int = 40, max_chars: int = 20000
) -> str:
    if not tables:
        return ""
    chunks: list[str] = []
    for table in tables:
        page = table.get("page")
        method = table.get("method")
        text = table.get("text")
        if not text:
            continue
        rows = text.splitlines()
        if max_rows and len(rows) > max_rows:
            rows = rows[:max_rows]
            text = "\n".join(rows)
        if max_chars and len(text) > max_chars:
            text = text[:max_chars]
        label = f"Page {page}" if page else "Page"
        if method:
            label = f"{label} ({method})"
        chunks.append(f"{label}:\n{text}")
    return "\n\n".join(chunks)
