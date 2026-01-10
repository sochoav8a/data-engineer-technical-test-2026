import csv
import json
import sys
from pathlib import Path

from scripts import report_coverage


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_report_coverage_includes_no_flags(tmp_path, monkeypatch):
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    manifest_path = tmp_path / "run_manifest.json"
    output_path = tmp_path / "coverage_report.md"

    _write_csv(
        csv_dir / "resources.csv",
        [
            "source_pdf",
            "category",
            "metal",
            "tonnes_value",
            "tonnes_unit",
            "grade_value",
            "grade_unit",
            "contained_value",
            "contained_unit",
            "source_pages",
        ],
        [
            {
                "source_pdf": "a.pdf",
                "category": "Measured",
                "metal": "Au",
                "tonnes_value": "1",
                "tonnes_unit": "kt",
                "grade_value": "1.0",
                "grade_unit": "g/t",
                "contained_value": "1",
                "contained_unit": "koz",
                "source_pages": "1",
            },
            {
                "source_pdf": "b.pdf",
                "category": "Indicated",
                "metal": "Au",
                "tonnes_value": "2",
                "tonnes_unit": "kt",
                "grade_value": "2.0",
                "grade_unit": "g/t",
                "contained_value": "2",
                "contained_unit": "koz",
                "source_pages": "2",
            },
        ],
    )

    _write_csv(
        csv_dir / "reserves.csv",
        [
            "source_pdf",
            "category",
            "metal",
            "tonnes_value",
            "tonnes_unit",
            "grade_value",
            "grade_unit",
            "contained_value",
            "contained_unit",
            "source_pages",
        ],
        [],
    )

    _write_csv(
        csv_dir / "economics.csv",
        [
            "source_pdf",
            "capex_value",
            "capex_unit",
            "opex_value",
            "opex_unit",
            "npv_value",
            "npv_unit",
            "irr_value",
            "irr_unit",
            "currency",
            "source_pages",
        ],
        [
            {
                "source_pdf": "a.pdf",
                "capex_value": "100",
                "capex_unit": "US$ 000",
                "opex_value": "",
                "opex_unit": "",
                "npv_value": "",
                "npv_unit": "",
                "irr_value": "",
                "irr_unit": "",
                "currency": "US$",
                "source_pages": "1",
            },
            {
                "source_pdf": "b.pdf",
                "capex_value": "",
                "capex_unit": "",
                "opex_value": "",
                "opex_unit": "",
                "npv_value": "",
                "npv_unit": "",
                "irr_value": "",
                "irr_unit": "",
                "currency": "",
                "source_pages": "",
            },
        ],
    )

    manifest = {
        "run_id": "test-run",
        "duration_sec": 3.5,
        "settings": {"extraction_strategy": "two_stage"},
        "pdfs": [
            {
                "source_pdf": "a.pdf",
                "durations_sec": {"total": 1.2},
                "warnings": ["economics missing numeric values"],
                "page_count": 10,
                "cache_hit": True,
                "no_reserves_pages": [5],
                "no_economics_pages": [],
            },
            {
                "source_pdf": "b.pdf",
                "durations_sec": {"total": 2.3},
                "warnings": [],
                "page_count": 12,
                "cache_hit": False,
                "no_reserves_pages": [],
                "no_economics_pages": [7, 8],
            },
        ],
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "report_coverage.py",
            "--manifest",
            str(manifest_path),
            "--csv-dir",
            str(csv_dir),
            "--output",
            str(output_path),
        ],
    )

    report_coverage.main()

    text = output_path.read_text(encoding="utf-8")
    assert "| resources_rows | 2 |" in text
    assert "| economics_with_values | 1 |" in text
    assert "no_reserves" in text
    assert "no_econ" in text

    row_a = next(line for line in text.splitlines() if line.startswith("| a.pdf |"))
    parts_a = [part.strip() for part in row_a.strip("|").split("|")]
    assert parts_a[6] == "yes"
    assert parts_a[7] == ""

    row_b = next(line for line in text.splitlines() if line.startswith("| b.pdf |"))
    parts_b = [part.strip() for part in row_b.strip("|").split("|")]
    assert parts_b[6] == ""
    assert parts_b[7] == "yes"
