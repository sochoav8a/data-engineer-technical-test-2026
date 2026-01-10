from __future__ import annotations

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
                        "page": table.page,
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
                                "page": idx + 1,
                                "method": "pdfplumber",
                                "text": text,
                            }
                        )
    except Exception:
        return tables
    return tables


def extract_tables_for_pages(pdf_path: Path, page_indices: list[int]) -> list[dict[str, str]]:
    if not page_indices:
        return []
    pages_one_based = sorted({idx + 1 for idx in page_indices})
    tables = []
    tables.extend(_tables_from_camelot(pdf_path, pages_one_based))
    tables.extend(_tables_from_pdfplumber(pdf_path, page_indices))
    return tables


def build_table_context(tables: list[dict[str, str]]) -> str:
    if not tables:
        return ""
    chunks: list[str] = []
    for table in tables:
        page = table.get("page")
        method = table.get("method")
        text = table.get("text")
        if not text:
            continue
        label = f"Page {page}" if page else "Page"
        if method:
            label = f"{label} ({method})"
        chunks.append(f"{label}:\n{text}")
    return "\n\n".join(chunks)
