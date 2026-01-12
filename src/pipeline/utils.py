import hashlib
import re
from pathlib import Path
from typing import Sequence

KEYWORDS = [
    "mineral resource",
    "mineral reserve",
    "measured",
    "indicated",
    "inferred",
    "proven",
    "probable",
    "capital cost",
    "capex",
    "operating cost",
    "opex",
    "npv",
    "irr",
    "economic",
    "summary",
    "project",
    "company",
    "location",
]

TOC_MARKERS = [
    "table of contents",
    "contents",
    "list of tables",
    "list of figures",
]

NO_RESERVES_PATTERNS = [
    re.compile(r"no (current )?mineral reserve", re.I),
    re.compile(r"no reserves conforming", re.I),
    re.compile(r"no reserves (have been )?estimated", re.I),
    re.compile(r"no reserve estimates", re.I),
    re.compile(r"no mineral resource or mineral reserve", re.I),
    re.compile(r"no reserves reported", re.I),
]

NO_ECONOMICS_PATTERNS = [
    re.compile(r"capital and operating costs? .*not.*determined", re.I),
    re.compile(r"capital costs? .*not.*determined", re.I),
    re.compile(r"operating costs? .*not.*determined", re.I),
    re.compile(r"not at a state where .*costs are determined", re.I),
    re.compile(r"no economic (analysis|assessment|study)", re.I),
    re.compile(r"economic (analysis|assessment|study) has not been completed", re.I),
]


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def is_toc_page(text: str) -> bool:
    lower = text.lower()
    if any(marker in lower for marker in TOC_MARKERS):
        dot_lines = sum(1 for line in text.splitlines() if "...." in line)
        if "contents" in lower or dot_lines >= 3:
            return True
    return False


def find_pages_with_keywords(page_texts: Sequence[str], keywords: Sequence[str]) -> set[int]:
    hits: set[int] = set()
    for idx, text in enumerate(page_texts):
        lower = text.lower()
        if any(keyword in lower for keyword in keywords):
            hits.add(idx)
    return hits


def find_table_pages(page_texts: Sequence[str], keywords: Sequence[str]) -> set[int]:
    hits: set[int] = set()
    for idx, text in enumerate(page_texts):
        lower = text.lower()
        if "table" in lower and any(keyword in lower for keyword in keywords):
            hits.add(idx)
    return hits


def find_pages_with_patterns(
    page_texts: Sequence[str], patterns: Sequence[re.Pattern[str]]
) -> list[int]:
    hits: list[int] = []
    if not patterns:
        return hits
    for idx, text in enumerate(page_texts):
        if any(pattern.search(text) for pattern in patterns):
            hits.append(idx + 1)
    return hits


def build_llm_context(page_texts: Sequence[str], window: int = 1) -> str:
    if not page_texts:
        return ""

    toc_pages = {idx for idx, text in enumerate(page_texts) if is_toc_page(text)}

    selected_pages: set[int] = set()

    for idx in range(min(3, len(page_texts))):
        if idx not in toc_pages:
            selected_pages.add(idx)

    meta_keywords = [
        "summary",
        "executive summary",
        "project description",
        "property description",
        "location",
    ]
    selected_pages.update(find_pages_with_keywords(page_texts, meta_keywords))

    resource_keywords = ["mineral resource", "resource estimate", "resources"]
    reserve_keywords = ["mineral reserve", "reserves"]
    resource_pages = find_table_pages(page_texts, resource_keywords)
    reserve_pages = find_table_pages(page_texts, reserve_keywords)

    econ_keywords = ["capital cost", "capex", "operating cost", "opex", "npv", "irr"]
    econ_pages = find_pages_with_keywords(page_texts, econ_keywords)

    for idx in resource_pages | reserve_pages | econ_pages:
        start = max(0, idx - window)
        end = min(len(page_texts), idx + window + 1)
        selected_pages.update(range(start, end))

    selected_pages.difference_update(toc_pages)

    if not selected_pages:
        selected_pages = set(range(len(page_texts))) - toc_pages

    chunks: list[str] = []
    for idx in sorted(selected_pages):
        text = page_texts[idx].strip()
        if not text:
            continue
        chunks.append(f"Page {idx + 1}:\n{text}")

    return "\n\n".join(chunks)


def extract_relevant_sections(text: str, window: int = 20) -> str:
    lines = text.splitlines()
    keep: list[str] = []
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(k in line_lower for k in KEYWORDS):
            start = max(0, i - 3)
            end = min(len(lines), i + window)
            keep.extend(lines[start:end])
    seen = set()
    cleaned = []
    for line in keep:
        key = normalize_whitespace(line)
        if not key or key in seen:
            continue
        seen.add(key)
        cleaned.append(line)
    if not cleaned:
        return text
    return "\n".join(cleaned)


def extract_relevant_page_snippets(text: str, keywords: Sequence[str], window: int = 12) -> str:
    if not text or not keywords:
        return text

    parts = re.split(r"\n\n(?=Page \d+:)", text)
    kept_parts: list[str] = []
    keyword_set = [kw.lower() for kw in keywords if kw]

    for part in parts:
        lines = part.splitlines()
        if not lines:
            continue
        header = lines[0]
        body = lines[1:]
        if not body:
            continue

        hit_indices = []
        for idx, line in enumerate(body):
            lower = line.lower()
            if any(kw in lower for kw in keyword_set):
                hit_indices.append(idx)

        if not hit_indices:
            continue

        keep_indices: set[int] = set()
        for idx in hit_indices:
            start = max(0, idx - 3)
            end = min(len(body), idx + window)
            keep_indices.update(range(start, end))

        seen: set[str] = set()
        snippet: list[str] = []
        for idx in sorted(keep_indices):
            line = body[idx]
            key = normalize_whitespace(line)
            if not key or key in seen:
                continue
            seen.add(key)
            snippet.append(line)

        if snippet:
            # Preserve Page N headers so source_pages remains traceable.
            kept_parts.append("\n".join([header] + snippet))

    if kept_parts:
        return "\n\n".join(kept_parts)
    return text


def clamp_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def any_value(*values: object | None) -> bool:
    return any(v is not None and v != "" for v in values)


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()
