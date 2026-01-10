from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from .embeddings import EmbeddingSettings, EmbeddingStore, cosine_similarity
from .utils import is_toc_page, normalize_whitespace


@dataclass
class SectionConfig:
    name: str
    query: str
    keywords: list[str]
    table_keywords: list[str]
    top_k: int = 5
    window: int = 1
    keyword_weight: float = 0.6
    table_weight: float = 1.0
    numeric_weight: float = 0.3
    embedding_weight: float = 2.0


def _keyword_hits(text: str, keywords: list[str]) -> int:
    lower = text.lower()
    return sum(1 for kw in keywords if kw in lower)


def _numeric_density(text: str) -> float:
    tokens = re.findall(r"[A-Za-z0-9.%/-]+", text)
    if not tokens:
        return 0.0
    numeric = sum(1 for t in tokens if any(ch.isdigit() for ch in t))
    return numeric / max(1, len(tokens))


def _table_number_hit(text: str) -> bool:
    return bool(re.search(r"\btable\s+\d+(?:[-.]\d+)?", text, re.I))


def _has_table_signal(text: str) -> bool:
    lower = text.lower()
    if "table" in lower:
        return True
    for line in text.splitlines():
        if line.count("  ") >= 2 and sum(ch.isdigit() for ch in line) >= 2:
            return True
    return False


def _truncate(text: str, max_chars: int) -> str:
    return text[:max_chars]


def rank_pages(
    page_texts: Sequence[str],
    config: SectionConfig,
    embed_store: EmbeddingStore,
    embed_settings: EmbeddingSettings,
) -> list[tuple[int, float]]:
    toc_pages = {idx for idx, text in enumerate(page_texts) if is_toc_page(text)}
    base_scores: list[tuple[int, float]] = []

    for idx, text in enumerate(page_texts):
        if idx in toc_pages:
            continue
        hits = _keyword_hits(text, config.keywords + config.table_keywords)
        table_hit = _has_table_signal(text)
        table_number_hit = _table_number_hit(text)
        numeric_density = _numeric_density(text)
        score = (
            hits * config.keyword_weight
            + (config.table_weight if table_hit else 0.0)
            + (config.table_weight * 0.5 if table_number_hit else 0.0)
            + numeric_density * config.numeric_weight
        )
        base_scores.append((idx, score))

    candidates = [idx for idx, score in base_scores if score > 0]
    if not candidates:
        candidates = [
            idx
            for idx, _ in sorted(base_scores, key=lambda x: x[1], reverse=True)[
                : embed_settings.max_pages
            ]
        ]

    if len(candidates) > embed_settings.max_pages:
        candidates = [
            idx
            for idx, _ in sorted(base_scores, key=lambda x: x[1], reverse=True)[
                : embed_settings.max_pages
            ]
        ]

    sim_scores: dict[int, float] = {}
    if embed_settings.enabled:
        query_embedding = embed_store.embed_text(config.query)
        if query_embedding:
            for idx in candidates:
                text = _truncate(page_texts[idx], embed_settings.max_chars)
                page_embedding = embed_store.embed_text(text)
                sim_scores[idx] = cosine_similarity(page_embedding, query_embedding)

    ranked: list[tuple[int, float]] = []
    for idx, base_score in base_scores:
        sim = sim_scores.get(idx, 0.0)
        total = base_score + sim * config.embedding_weight
        ranked.append((idx, total))

    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


def select_pages(
    page_texts: Sequence[str],
    config: SectionConfig,
    embed_store: EmbeddingStore,
    embed_settings: EmbeddingSettings,
) -> list[int]:
    toc_pages = {idx for idx, text in enumerate(page_texts) if is_toc_page(text)}
    ranked = rank_pages(page_texts, config, embed_store, embed_settings)
    selected = [idx for idx, score in ranked[: config.top_k] if score > 0]

    if not selected:
        selected = [idx for idx, _ in ranked[: config.top_k]]

    expanded: set[int] = set()
    for idx in selected:
        start = max(0, idx - config.window)
        end = min(len(page_texts), idx + config.window + 1)
        expanded.update(range(start, end))

    expanded.difference_update(toc_pages)
    return sorted(expanded)


def build_context(page_texts: Sequence[str], page_indices: Sequence[int]) -> str:
    chunks: list[str] = []
    for idx in page_indices:
        text = normalize_whitespace(page_texts[idx])
        if not text:
            continue
        chunks.append(f"Page {idx + 1}:\n{page_texts[idx].strip()}")
    return "\n\n".join(chunks)


SECTION_CONFIGS = {
    "metadata": SectionConfig(
        name="metadata",
        query="technical report project name company name location country region report date effective date",
        keywords=[
            "technical report",
            "project",
            "company",
            "location",
            "effective date",
            "report date",
        ],
        table_keywords=[],
        top_k=3,
        window=0,
        keyword_weight=0.8,
        table_weight=0.0,
        numeric_weight=0.1,
        embedding_weight=1.5,
    ),
    "resources": SectionConfig(
        name="resources",
        query="mineral resources measured indicated inferred tonnes grade contained metal table",
        keywords=[
            "mineral resource",
            "mineral resources",
            "resource estimate",
            "resource statement",
            "measured",
            "indicated",
            "inferred",
            "measured and indicated",
            "measured + indicated",
            "tonnes",
            "grade",
            "contained",
        ],
        table_keywords=["table"],
        top_k=6,
        window=1,
        keyword_weight=0.6,
        table_weight=1.2,
        numeric_weight=0.4,
        embedding_weight=2.0,
    ),
    "reserves": SectionConfig(
        name="reserves",
        query="mineral reserves proven probable tonnes grade contained metal table",
        keywords=[
            "mineral reserve",
            "mineral reserves",
            "reserve estimate",
            "reserve statement",
            "proven",
            "probable",
            "proven and probable",
            "proven + probable",
            "p&p",
            "tonnes",
            "grade",
            "contained",
        ],
        table_keywords=["table"],
        top_k=6,
        window=1,
        keyword_weight=0.7,
        table_weight=1.4,
        numeric_weight=0.4,
        embedding_weight=2.0,
    ),
    "economics": SectionConfig(
        name="economics",
        query="capital cost operating cost capex opex capital and operating costs npv irr cash flow payback",
        keywords=[
            "capital cost",
            "capital costs",
            "capital expenditure",
            "operating cost",
            "operating costs",
            "operating expenditure",
            "capital and operating costs",
            "capex",
            "opex",
            "npv",
            "irr",
            "economic",
            "sustaining capital",
            "initial capital",
            "total capital",
            "cash flow",
            "payback",
            "life of mine",
            "mine life",
        ],
        table_keywords=["table"],
        top_k=6,
        window=1,
        keyword_weight=0.7,
        table_weight=1.2,
        numeric_weight=0.4,
        embedding_weight=2.0,
    ),
}

FALLBACK_SECTION_CONFIGS = {
    "resources": SectionConfig(
        name="resources",
        query="resource conclusions mineral resources measured indicated inferred",
        keywords=[
            "resource conclusions",
            "historic resource",
            "mineral resources",
            "measured",
            "indicated",
            "inferred",
            "resource estimate",
            "the author believes",
            "the project has",
            "project has",
        ],
        table_keywords=[],
        top_k=8,
        window=2,
        keyword_weight=0.7,
        table_weight=0.5,
        numeric_weight=0.5,
        embedding_weight=2.0,
    ),
    "reserves": SectionConfig(
        name="reserves",
        query="reserve conclusions mineral reserves proven probable",
        keywords=[
            "reserve conclusions",
            "mineral reserves",
            "reserve estimate",
            "proven",
            "probable",
        ],
        table_keywords=[],
        top_k=8,
        window=2,
        keyword_weight=0.7,
        table_weight=0.5,
        numeric_weight=0.5,
        embedding_weight=2.0,
    ),
    "economics": SectionConfig(
        name="economics",
        query="capital cost operating cost sustaining capital LOM cash flow NPV IRR",
        keywords=[
            "capital cost",
            "operating cost",
            "capital and operating costs",
            "sustaining capital",
            "life of mine",
            "cash flow",
            "npv",
            "irr",
        ],
        table_keywords=[],
        top_k=8,
        window=2,
        keyword_weight=0.7,
        table_weight=0.5,
        numeric_weight=0.5,
        embedding_weight=2.0,
    ),
}
