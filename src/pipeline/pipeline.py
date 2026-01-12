from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from .config import Settings
from .embeddings import EmbeddingSettings, EmbeddingStore
from .llm import SECTION_TASKS, extract_structured, extract_with_schema
from .models import (
    EconomicsResult,
    ExtractionResult,
    MetadataResult,
    ReservesResult,
    ResourcesResult,
)
from .observability import configure_logging, log_event
from .parsers import extract_pdf_pages, parse_pdf_to_markdown
from .quality import apply_quality_checks
from .selector import FALLBACK_SECTION_CONFIGS, SECTION_CONFIGS, build_context, select_pages
from .storage import save_csvs, save_json, save_sqlite
from .table_extractor import (
    build_table_context,
    extract_tables_for_pages,
    filter_tables_for_section,
)
from .utils import (
    NO_ECONOMICS_PATTERNS,
    NO_RESERVES_PATTERNS,
    clamp_text,
    extract_relevant_page_snippets,
    file_sha256,
    find_pages_with_patterns,
)

SchemaModel = TypeVar("SchemaModel", bound=BaseModel)
TABLE_LIMITS = {
    "resources": 8,
    "reserves": 8,
    "economics": 8,
}


def _score_result(result: ExtractionResult) -> float:
    score = 0
    if result.resources:
        score += 1
    if result.reserves:
        score += 1
    econ = result.economics
    econ_values = [
        econ.capex.value if econ.capex else None,
        econ.opex.value if econ.opex else None,
        econ.npv.value if econ.npv else None,
        econ.irr.value if econ.irr else None,
    ]
    if any(econ_values):
        score += 1
    if result.metadata.project_name or result.metadata.company_name:
        score += 1
    return score / 4


def _has_economics(econ) -> bool:
    if not econ:
        return False
    return any([econ.capex, econ.opex, econ.npv, econ.irr])


def _build_embedding_settings(settings: Settings) -> EmbeddingSettings:
    enabled = settings.embeddings_enabled and bool(settings.gemini_api_key)
    return EmbeddingSettings(
        enabled=enabled,
        api_key=settings.gemini_api_key,
        model_name=settings.embedding_model,
        max_chars=settings.embedding_max_chars,
        max_pages=settings.embedding_max_pages,
    )


def _resolve_sections(settings: Settings) -> set[str]:
    if settings.sections:
        return set(settings.sections)
    return {"metadata", "resources", "reserves", "economics"}


def _combine_contexts(table_context: str, text_context: str, max_chars: int) -> str:
    if not table_context:
        return text_context
    if not text_context:
        return table_context
    # Keep a budget for tables because they carry dense numeric signals.
    table_budget = int(max_chars * 0.4)
    text_budget = max_chars - table_budget - 2
    table_part = clamp_text(table_context, table_budget)
    text_part = clamp_text(text_context, text_budget)
    return f"{table_part}\n\n{text_part}"


def _focus_context(context: str, keywords: list[str], settings: Settings) -> str:
    if settings.extraction_mode != "smart":
        return context
    if not context or len(context) < 20000:
        return context
    focused = extract_relevant_page_snippets(context, keywords, window=12)
    if focused and len(focused) < len(context):
        return focused
    return context


def _build_two_stage_contexts(
    pdf_path: Path,
    settings: Settings,
    sections: set[str],
) -> tuple[list[str], dict[str, str], dict[str, list[int]], dict]:
    page_start = time.perf_counter()
    pages, cache_hit = extract_pdf_pages(
        pdf_path,
        cache_dir=Path(settings.output_dir) / "cache" / "pages",
    )
    page_duration = time.perf_counter() - page_start
    embed_settings = _build_embedding_settings(settings)
    cache_dir = Path(settings.output_dir) / "cache" / "embeddings"
    embed_store = EmbeddingStore(cache_dir, embed_settings)

    contexts: dict[str, str] = {}
    page_indices_by_section: dict[str, list[int]] = {}
    selection_durations: dict[str, float] = {}
    for section, config in SECTION_CONFIGS.items():
        if section not in sections:
            continue
        select_start = time.perf_counter()
        page_indices = select_pages(pages, config, embed_store, embed_settings)
        selection_durations[section] = time.perf_counter() - select_start
        page_indices_by_section[section] = page_indices
        contexts[section] = build_context(pages, page_indices)

    metrics = {
        "page_count": len(pages),
        "page_extract_sec": page_duration,
        "cache_hit": cache_hit,
        "selection_sec": selection_durations,
    }
    return pages, contexts, page_indices_by_section, metrics


def _fallback_context(
    pages: list[str],
    settings: Settings,
    section: str,
) -> str:
    embed_settings = _build_embedding_settings(settings)
    cache_dir = Path(settings.output_dir) / "cache" / "embeddings"
    embed_store = EmbeddingStore(cache_dir, embed_settings)
    fallback = FALLBACK_SECTION_CONFIGS.get(section)
    if not fallback:
        return ""
    page_indices = select_pages(pages, fallback, embed_store, embed_settings)
    return build_context(pages, page_indices)


def _extract_section(
    context: str,
    settings: Settings,
    schema_model,
    task_key: str,
    retry: bool = False,
):
    model_name = (
        settings.retry_model
        if (retry and settings.use_retry_model and settings.retry_model)
        else settings.model_name
    )
    return extract_with_schema(
        document_text=clamp_text(context, settings.max_chars),
        model_name=model_name,
        api_key=settings.gemini_api_key,
        provider=settings.llm_provider,
        schema_model=schema_model,
        task=SECTION_TASKS.get(task_key),
    )


def _extract_section_with_metrics(
    context: str,
    settings: Settings,
    schema_model: type[SchemaModel],
    task_key: str,
    logger: logging.Logger,
    pdf_name: str,
    section: str,
    retry: bool = False,
) -> tuple[SchemaModel, float, int]:
    input_chars = len(context)
    if settings.dry_run:
        log_event(
            logger,
            "section_skipped",
            pdf=pdf_name,
            section=section,
            retry=retry,
            input_chars=input_chars,
        )
        return schema_model(), 0.0, input_chars

    start = time.perf_counter()
    result = _extract_section(context, settings, schema_model, task_key, retry=retry)
    duration = time.perf_counter() - start
    log_event(
        logger,
        "section_extracted",
        pdf=pdf_name,
        section=section,
        retry=retry,
        duration_sec=round(duration, 3),
        input_chars=input_chars,
    )
    return result, duration, input_chars


def process_pdf_two_stage(pdf_path: Path, settings: Settings) -> tuple[ExtractionResult, dict]:
    logger = logging.getLogger("pipeline")
    pdf_name = pdf_path.name
    sections = _resolve_sections(settings)

    pdf_start = time.perf_counter()
    log_event(logger, "pdf_start", pdf=pdf_name, strategy="two_stage", sections=sorted(sections))

    pages, contexts, page_indices, context_metrics = _build_two_stage_contexts(
        pdf_path, settings, sections
    )
    # Detect explicit "no reserves/economics" statements to explain empty outputs.
    no_reserves_pages = find_pages_with_patterns(pages, NO_RESERVES_PATTERNS)
    no_economics_pages = find_pages_with_patterns(pages, NO_ECONOMICS_PATTERNS)
    log_event(
        logger,
        "pages_extracted",
        pdf=pdf_name,
        page_count=context_metrics.get("page_count"),
        cache_hit=context_metrics.get("cache_hit"),
        duration_sec=round(context_metrics.get("page_extract_sec", 0.0), 3),
    )
    for section, indices in page_indices.items():
        log_event(
            logger,
            "pages_selected",
            pdf=pdf_name,
            section=section,
            pages=indices,
            duration_sec=round(context_metrics.get("selection_sec", {}).get(section, 0.0), 3),
        )
    if context_metrics.get("cache_hit"):
        log_event(
            logger,
            "page_cache_hit",
            pdf=pdf_name,
            page_count=context_metrics.get("page_count"),
        )

    resources_context = contexts.get("resources", "")
    reserves_context = contexts.get("reserves", "")
    economics_context = contexts.get("economics", "")
    if "resources" in sections:
        resources_context = _focus_context(
            resources_context,
            SECTION_CONFIGS["resources"].keywords + SECTION_CONFIGS["resources"].table_keywords,
            settings,
        )
    if "reserves" in sections:
        reserves_context = _focus_context(
            reserves_context,
            SECTION_CONFIGS["reserves"].keywords + SECTION_CONFIGS["reserves"].table_keywords,
            settings,
        )
    # Economics tends to be sparse; keep full context to avoid losing values.

    table_counts: dict[str, int] = {}
    table_selected: dict[str, int] = {}
    table_durations: dict[str, float] = {}
    for key in ["resources", "reserves", "economics"]:
        if key not in sections:
            continue
        pages_for_section = page_indices.get(key, [])
        table_start = time.perf_counter()
        tables = extract_tables_for_pages(pdf_path, pages_for_section)
        filtered_tables = filter_tables_for_section(
            tables, key, max_tables=TABLE_LIMITS.get(key, 6)
        )
        table_durations[key] = time.perf_counter() - table_start
        table_counts[key] = len(tables)
        table_selected[key] = len(filtered_tables)
        table_context = build_table_context(filtered_tables)
        if table_context:
            if key == "resources":
                resources_context = _combine_contexts(
                    table_context, resources_context, settings.max_chars
                )
            elif key == "reserves":
                reserves_context = _combine_contexts(
                    table_context, reserves_context, settings.max_chars
                )
            else:
                economics_context = _combine_contexts(
                    table_context, economics_context, settings.max_chars
                )
        log_event(
            logger,
            "tables_extracted",
            pdf=pdf_name,
            section=key,
            tables=table_counts[key],
            tables_selected=table_selected[key],
            pages=pages_for_section,
            duration_sec=round(table_durations[key], 3),
        )

    llm_durations: dict[str, float] = {}
    llm_inputs: dict[str, int] = {}
    metadata_result = MetadataResult()
    resources_result = ResourcesResult()
    reserves_result = ReservesResult()
    economics_result = EconomicsResult()

    if "metadata" in sections:
        metadata_result, llm_durations["metadata"], llm_inputs["metadata"] = (
            _extract_section_with_metrics(
                contexts.get("metadata", ""),
                settings,
                MetadataResult,
                "metadata",
                logger,
                pdf_name,
                "metadata",
            )
        )
    if "resources" in sections:
        resources_result, llm_durations["resources"], llm_inputs["resources"] = (
            _extract_section_with_metrics(
                resources_context,
                settings,
                ResourcesResult,
                "resources",
                logger,
                pdf_name,
                "resources",
            )
        )
    if "reserves" in sections:
        reserves_result, llm_durations["reserves"], llm_inputs["reserves"] = (
            _extract_section_with_metrics(
                reserves_context,
                settings,
                ReservesResult,
                "reserves",
                logger,
                pdf_name,
                "reserves",
            )
        )
    if "economics" in sections:
        economics_result, llm_durations["economics"], llm_inputs["economics"] = (
            _extract_section_with_metrics(
                economics_context,
                settings,
                EconomicsResult,
                "economics",
                logger,
                pdf_name,
                "economics",
            )
        )

    warnings: list[str] = []

    if "metadata" in sections and not settings.dry_run:
        if not metadata_result.metadata.project_name and not metadata_result.metadata.company_name:
            if settings.retries_enabled:
                warnings.append("metadata missing; retrying with fallback selection")
                fallback_context = _fallback_context(pages, settings, "metadata")
                if fallback_context:
                    (
                        metadata_result,
                        llm_durations["metadata_retry"],
                        llm_inputs["metadata_retry"],
                    ) = _extract_section_with_metrics(
                        fallback_context,
                        settings,
                        MetadataResult,
                        "metadata",
                        logger,
                        pdf_name,
                        "metadata",
                        retry=True,
                    )
            else:
                warnings.append("metadata missing; retries disabled")

    if "resources" in sections and not settings.dry_run:
        if not resources_result.resources:
            if settings.retries_enabled:
                warnings.append("resources missing; retrying with fallback selection")
                fallback_context = _fallback_context(pages, settings, "resources")
                if fallback_context:
                    (
                        resources_result,
                        llm_durations["resources_retry"],
                        llm_inputs["resources_retry"],
                    ) = _extract_section_with_metrics(
                        fallback_context,
                        settings,
                        ResourcesResult,
                        "resources",
                        logger,
                        pdf_name,
                        "resources",
                        retry=True,
                    )
            else:
                warnings.append("resources missing; retries disabled")

    if "reserves" in sections and not settings.dry_run:
        if not reserves_result.reserves:
            if settings.retries_enabled:
                warnings.append("reserves missing; retrying with fallback selection")
                fallback_context = _fallback_context(pages, settings, "reserves")
                if fallback_context:
                    (
                        reserves_result,
                        llm_durations["reserves_retry"],
                        llm_inputs["reserves_retry"],
                    ) = _extract_section_with_metrics(
                        fallback_context,
                        settings,
                        ReservesResult,
                        "reserves",
                        logger,
                        pdf_name,
                        "reserves",
                        retry=True,
                    )
            else:
                warnings.append("reserves missing; retries disabled")
            if no_reserves_pages:
                warnings.append(
                    f"no reserves reported in document (pages: {', '.join(map(str, no_reserves_pages))})"
                )

    if "economics" in sections and not settings.dry_run:
        if not _has_economics(economics_result.economics):
            if settings.retries_enabled:
                warnings.append("economics missing; retrying with fallback selection")
                fallback_context = _fallback_context(pages, settings, "economics")
                if fallback_context:
                    (
                        economics_result,
                        llm_durations["economics_retry"],
                        llm_inputs["economics_retry"],
                    ) = _extract_section_with_metrics(
                        fallback_context,
                        settings,
                        EconomicsResult,
                        "economics",
                        logger,
                        pdf_name,
                        "economics",
                        retry=True,
                    )
            else:
                warnings.append("economics missing; retries disabled")
            if no_economics_pages:
                warnings.append(
                    f"economics not reported in document (pages: {', '.join(map(str, no_economics_pages))})"
                )

    result = ExtractionResult(
        metadata=metadata_result.metadata,
        resources=resources_result.resources,
        reserves=reserves_result.reserves,
        economics=economics_result.economics,
        warnings=warnings,
    )

    result.metadata.source_pdf = pdf_name
    result, quality_metrics, quality_warnings = apply_quality_checks(result, sections=sections)
    result.warnings.extend(quality_warnings)
    if settings.dry_run:
        result.warnings.append("dry_run: extraction skipped")

    if result.confidence is None:
        result.confidence = _score_result(result)

    total_duration = time.perf_counter() - pdf_start
    metrics = {
        "source_pdf": pdf_name,
        "sha256": file_sha256(pdf_path),
        "sections": sorted(sections),
        "page_count": context_metrics["page_count"],
        "cache_hit": context_metrics["cache_hit"],
        "selected_pages": page_indices,
        "table_counts": table_counts,
        "table_selected": table_selected,
        "no_reserves_pages": no_reserves_pages,
        "no_economics_pages": no_economics_pages,
        "durations_sec": {
            "page_extract": round(context_metrics["page_extract_sec"], 3),
            "selection": {k: round(v, 3) for k, v in context_metrics["selection_sec"].items()},
            "table_extract": {k: round(v, 3) for k, v in table_durations.items()},
            "llm": {k: round(v, 3) for k, v in llm_durations.items()},
            "total": round(total_duration, 3),
        },
        "llm_input_chars": llm_inputs,
        "warnings": result.warnings,
        "confidence": result.confidence,
        **quality_metrics,
    }

    log_event(
        logger,
        "pdf_end",
        pdf=pdf_name,
        duration_sec=round(total_duration, 3),
        resources=metrics["resources_count"],
        reserves=metrics["reserves_count"],
        economics_has_values=metrics["economics_has_values"],
        warnings=len(result.warnings),
    )

    return result, metrics


def process_pdf(pdf_path: Path, settings: Settings) -> tuple[ExtractionResult, dict]:
    logger = logging.getLogger("pipeline")
    pdf_name = pdf_path.name
    sections = _resolve_sections(settings)

    pdf_start = time.perf_counter()
    log_event(logger, "pdf_start", pdf=pdf_name, strategy="single", sections=sorted(sections))

    parse_start = time.perf_counter()
    parsed = parse_pdf_to_markdown(pdf_path, settings.llama_parse_api_key)
    parse_duration = time.perf_counter() - parse_start
    text = clamp_text(parsed.text, settings.max_chars)

    llm_duration = 0.0
    if settings.dry_run:
        result = ExtractionResult()
    else:
        llm_start = time.perf_counter()
        result = extract_structured(
            document_text=text,
            model_name=settings.model_name,
            api_key=settings.gemini_api_key,
            provider=settings.llm_provider,
        )
        llm_duration = time.perf_counter() - llm_start

    result.metadata.source_pdf = pdf_name
    if result.confidence is None:
        result.confidence = _score_result(result)
    if parsed.parser_name != "llama_parse":
        result.warnings.append("llama_parse not used; parsing quality may be lower")

    result, quality_metrics, quality_warnings = apply_quality_checks(result, sections=sections)
    result.warnings.extend(quality_warnings)
    if settings.dry_run:
        result.warnings.append("dry_run: extraction skipped")

    total_duration = time.perf_counter() - pdf_start
    metrics = {
        "source_pdf": pdf_name,
        "sha256": file_sha256(pdf_path),
        "sections": sorted(sections),
        "page_count": None,
        "cache_hit": None,
        "selected_pages": {},
        "table_counts": {},
        "durations_sec": {
            "parse": round(parse_duration, 3),
            "llm": round(llm_duration, 3),
            "total": round(total_duration, 3),
        },
        "llm_input_chars": {"full": len(text)},
        "parser": parsed.parser_name,
        "warnings": result.warnings,
        "confidence": result.confidence,
        **quality_metrics,
    }

    log_event(
        logger,
        "pdf_end",
        pdf=pdf_name,
        duration_sec=round(total_duration, 3),
        resources=metrics["resources_count"],
        reserves=metrics["reserves_count"],
        economics_has_values=metrics["economics_has_values"],
        warnings=len(result.warnings),
    )

    return result, metrics


def run_pipeline(
    data_dir: Path,
    output_dir: Path,
    sqlite_path: Path,
    settings: Settings,
    limit: int | None = None,
) -> list[ExtractionResult]:
    if not logging.getLogger().handlers:
        configure_logging(
            Path(settings.log_dir) if settings.log_dir else output_dir / "logs", settings.log_level
        )
    logger = logging.getLogger("pipeline")
    output_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(Path(data_dir).glob("*.pdf"))
    if limit:
        pdfs = pdfs[:limit]

    run_id = datetime.now(timezone.utc).isoformat()
    run_start = time.perf_counter()
    log_event(
        logger,
        "run_start",
        run_id=run_id,
        pdfs=len(pdfs),
        strategy=settings.extraction_strategy,
        max_workers=settings.max_workers,
        dry_run=settings.dry_run,
    )

    results: list[ExtractionResult | None] = [None] * len(pdfs)
    metrics: list[dict | None] = [None] * len(pdfs)

    def _process(pdf_path: Path) -> tuple[ExtractionResult, dict]:
        if settings.extraction_strategy == "two_stage":
            return process_pdf_two_stage(pdf_path, settings)
        return process_pdf(pdf_path, settings)

    if settings.max_workers > 1 and len(pdfs) > 1:
        with ThreadPoolExecutor(max_workers=settings.max_workers) as executor:
            future_map = {executor.submit(_process, pdf): idx for idx, pdf in enumerate(pdfs)}
            for future in as_completed(future_map):
                idx = future_map[future]
                result, info = future.result()
                results[idx] = result
                metrics[idx] = info
    else:
        for idx, pdf in enumerate(pdfs):
            result, info = _process(pdf)
            results[idx] = result
            metrics[idx] = info

    final_results = [result for result in results if result is not None]
    save_json(final_results, output_dir)
    save_csvs(final_results, output_dir)
    save_sqlite(final_results, sqlite_path)

    settings_dict = settings.__dict__.copy()
    if settings_dict.get("gemini_api_key"):
        settings_dict["gemini_api_key"] = "set"
    if settings_dict.get("llama_parse_api_key"):
        settings_dict["llama_parse_api_key"] = "set"

    run_duration = time.perf_counter() - run_start
    manifest = {
        "run_id": run_id,
        "started_at": run_id,
        "duration_sec": round(run_duration, 3),
        "settings": settings_dict,
        "pdfs": [m for m in metrics if m is not None],
    }
    manifest_path = output_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    log_event(
        logger,
        "run_end",
        run_id=run_id,
        duration_sec=round(run_duration, 3),
        pdfs=len(final_results),
    )
    return final_results
