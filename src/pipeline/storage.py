from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .models import ExtractionResult


def _q_value(q):
    return q.value if q else None


def _q_unit(q):
    return q.unit if q else None


def _normalize_pages(pages: str | None) -> str | None:
    if not pages:
        return pages
    cleaned = pages.replace("Page ", "").replace("page ", "")
    cleaned = cleaned.replace(";", ",")
    cleaned = cleaned.replace("|", ",")
    cleaned = cleaned.replace("/", ",")
    cleaned = " ".join(cleaned.split())
    return cleaned


def save_json(results: Iterable[ExtractionResult], output_dir: Path) -> None:
    json_dir = output_dir / "json"
    json_dir.mkdir(parents=True, exist_ok=True)
    for result in results:
        name = result.metadata.source_pdf or "unknown"
        stem = Path(name).stem
        path = json_dir / f"{stem}.json"
        path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def save_csvs(results: Iterable[ExtractionResult], output_dir: Path) -> None:
    metadata_rows = []
    resource_rows = []
    reserve_rows = []
    economics_rows = []

    for result in results:
        meta = result.metadata
        metadata_rows.append(
            {
                "source_pdf": meta.source_pdf,
                "project_name": meta.project_name,
                "company_name": meta.company_name,
                "location_country": meta.location_country,
                "location_region": meta.location_region,
                "report_date": meta.report_date,
                "report_date_raw": meta.report_date_raw,
            }
        )

        for res in result.resources:
            resource_rows.append(
                {
                    "source_pdf": meta.source_pdf,
                    "category": res.category,
                    "metal": res.metal,
                    "tonnes_value": res.tonnes.value,
                    "tonnes_unit": res.tonnes.unit,
                    "grade_value": res.grade.value,
                    "grade_unit": res.grade.unit,
                    "contained_value": res.contained_metal.value,
                    "contained_unit": res.contained_metal.unit,
                    "source_pages": _normalize_pages(res.source_pages),
                }
            )

        for res in result.reserves:
            reserve_rows.append(
                {
                    "source_pdf": meta.source_pdf,
                    "category": res.category,
                    "metal": res.metal,
                    "tonnes_value": res.tonnes.value,
                    "tonnes_unit": res.tonnes.unit,
                    "grade_value": res.grade.value,
                    "grade_unit": res.grade.unit,
                    "contained_value": res.contained_metal.value,
                    "contained_unit": res.contained_metal.unit,
                    "source_pages": _normalize_pages(res.source_pages),
                }
            )

        econ = result.economics
        economics_rows.append(
            {
                "source_pdf": meta.source_pdf,
                "capex_value": _q_value(econ.capex),
                "capex_unit": _q_unit(econ.capex),
                "opex_value": _q_value(econ.opex),
                "opex_unit": _q_unit(econ.opex),
                "npv_value": _q_value(econ.npv),
                "npv_unit": _q_unit(econ.npv),
                "irr_value": _q_value(econ.irr),
                "irr_unit": _q_unit(econ.irr),
                "currency": econ.currency,
                "source_pages": _normalize_pages(econ.source_pages),
            }
        )

    _write_csv(output_dir / "metadata.csv", metadata_rows)
    _write_csv(output_dir / "resources.csv", resource_rows)
    _write_csv(output_dir / "reserves.csv", reserve_rows)
    _write_csv(output_dir / "economics.csv", economics_rows)


def save_sqlite(results: Iterable[ExtractionResult], sqlite_path: Path, reset: bool = True) -> None:
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    if reset and sqlite_path.exists():
        sqlite_path.unlink()

    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            source_pdf TEXT PRIMARY KEY,
            project_name TEXT,
            company_name TEXT,
            location_country TEXT,
            location_region TEXT,
            report_date TEXT,
            report_date_raw TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_pdf TEXT,
            category TEXT,
            metal TEXT,
            tonnes_value REAL,
            tonnes_unit TEXT,
            grade_value REAL,
            grade_unit TEXT,
            contained_value REAL,
            contained_unit TEXT,
            source_pages TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reserves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_pdf TEXT,
            category TEXT,
            metal TEXT,
            tonnes_value REAL,
            tonnes_unit TEXT,
            grade_value REAL,
            grade_unit TEXT,
            contained_value REAL,
            contained_unit TEXT,
            source_pages TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS economics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_pdf TEXT,
            capex_value REAL,
            capex_unit TEXT,
            opex_value REAL,
            opex_unit TEXT,
            npv_value REAL,
            npv_unit TEXT,
            irr_value REAL,
            irr_unit TEXT,
            currency TEXT,
            source_pages TEXT
        )
        """
    )

    for result in results:
        meta = result.metadata
        cur.execute(
            """
            INSERT OR REPLACE INTO documents
            (source_pdf, project_name, company_name, location_country, location_region, report_date, report_date_raw)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                meta.source_pdf,
                meta.project_name,
                meta.company_name,
                meta.location_country,
                meta.location_region,
                meta.report_date,
                meta.report_date_raw,
            ),
        )

        for res in result.resources:
            cur.execute(
                """
                INSERT INTO resources
                (source_pdf, category, metal, tonnes_value, tonnes_unit, grade_value, grade_unit,
                 contained_value, contained_unit, source_pages)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    meta.source_pdf,
                    res.category,
                    res.metal,
                    res.tonnes.value,
                    res.tonnes.unit,
                    res.grade.value,
                    res.grade.unit,
                    res.contained_metal.value,
                    res.contained_metal.unit,
                    _normalize_pages(res.source_pages),
                ),
            )

        for res in result.reserves:
            cur.execute(
                """
                INSERT INTO reserves
                (source_pdf, category, metal, tonnes_value, tonnes_unit, grade_value, grade_unit,
                 contained_value, contained_unit, source_pages)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    meta.source_pdf,
                    res.category,
                    res.metal,
                    res.tonnes.value,
                    res.tonnes.unit,
                    res.grade.value,
                    res.grade.unit,
                    res.contained_metal.value,
                    res.contained_metal.unit,
                    _normalize_pages(res.source_pages),
                ),
            )

        econ = result.economics
        cur.execute(
            """
            INSERT INTO economics
            (source_pdf, capex_value, capex_unit, opex_value, opex_unit, npv_value, npv_unit,
             irr_value, irr_unit, currency, source_pages)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                meta.source_pdf,
                _q_value(econ.capex),
                _q_unit(econ.capex),
                _q_value(econ.opex),
                _q_unit(econ.opex),
                _q_value(econ.npv),
                _q_unit(econ.npv),
                _q_value(econ.irr),
                _q_unit(econ.irr),
                econ.currency,
                _normalize_pages(econ.source_pages),
            ),
        )

    conn.commit()
    conn.close()
