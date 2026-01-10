from __future__ import annotations

from typing import Any

from .models import Economics, ExtractionResult, MineralReserve
from .utils import any_value


def _is_reserve_category(category: str | None) -> bool:
    if not category:
        return True
    lower = category.lower()
    if "proven" in lower or "probable" in lower:
        return True
    return "p&p" in lower or "p+p" in lower or lower.strip() == "pp"


def _economics_has_values(econ: Economics) -> bool:
    return any(
        any_value(q.value, q.raw)
        for q in [econ.capex, econ.opex, econ.npv, econ.irr]
        if q is not None
    )


def _resource_row_has_values(row) -> bool:
    return any_value(
        row.tonnes.value,
        row.tonnes.raw,
        row.grade.value,
        row.grade.raw,
        row.contained_metal.value,
        row.contained_metal.raw,
    )


def _reserve_row_has_values(row) -> bool:
    return any_value(
        row.tonnes.value,
        row.tonnes.raw,
        row.grade.value,
        row.grade.raw,
        row.contained_metal.value,
        row.contained_metal.raw,
    )


def _filter_reserves(reserves: list[MineralReserve]) -> tuple[list[MineralReserve], list[str]]:
    kept: list[MineralReserve] = []
    warnings: list[str] = []
    for row in reserves:
        if _is_reserve_category(row.category):
            kept.append(row)
        else:
            warnings.append(f"reserve category filtered: {row.category}")
    return kept, warnings


def apply_quality_checks(
    result: ExtractionResult,
    sections: set[str] | None = None,
) -> tuple[ExtractionResult, dict[str, Any], list[str]]:
    active_sections = sections or {"metadata", "resources", "reserves", "economics"}
    warnings: list[str] = []

    if "reserves" in active_sections:
        filtered_reserves, reserve_warnings = _filter_reserves(result.reserves)
        if reserve_warnings:
            warnings.extend(reserve_warnings)
            result.reserves = filtered_reserves

    resource_empty = sum(1 for row in result.resources if not _resource_row_has_values(row))
    reserve_empty = sum(1 for row in result.reserves if not _reserve_row_has_values(row))
    economics_has_values = _economics_has_values(result.economics)

    metrics = {
        "resources_count": len(result.resources),
        "reserves_count": len(result.reserves),
        "resource_empty_rows": resource_empty,
        "reserve_empty_rows": reserve_empty,
        "economics_has_values": economics_has_values,
        "metadata_filled": bool(result.metadata.project_name or result.metadata.company_name),
    }

    if "resources" in active_sections and resource_empty:
        warnings.append(f"resources with empty quantities: {resource_empty}")
    if "reserves" in active_sections and reserve_empty:
        warnings.append(f"reserves with empty quantities: {reserve_empty}")
    if "economics" in active_sections and not economics_has_values:
        warnings.append("economics missing numeric values")

    return result, metrics, warnings
