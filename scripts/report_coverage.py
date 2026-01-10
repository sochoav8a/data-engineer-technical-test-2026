from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _count_rows(rows: list[dict[str, str]], key: str) -> Counter:
    counter = Counter()
    for row in rows:
        counter[row.get(key) or ""] += 1
    return counter


def _economics_with_values(rows: list[dict[str, str]]) -> Counter:
    counter = Counter()
    for row in rows:
        has_values = any(row.get(k) for k in ["capex_value", "opex_value", "npv_value", "irr_value"])
        if has_values:
            counter[row.get("source_pdf") or ""] += 1
    return counter


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate coverage report from run_manifest.json and CSV outputs")
    parser.add_argument("--manifest", default="output/run_manifest.json", help="Path to run_manifest.json")
    parser.add_argument("--csv-dir", default="output", help="Directory with CSV outputs")
    parser.add_argument("--output", default="output/coverage_report.md", help="Path to write markdown report")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    csv_dir = Path(args.csv_dir)
    output_path = Path(args.output)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pdf_metrics = manifest.get("pdfs", [])

    resources_rows = _read_csv(csv_dir / "resources.csv")
    reserves_rows = _read_csv(csv_dir / "reserves.csv")
    economics_rows = _read_csv(csv_dir / "economics.csv")

    resources_counts = _count_rows(resources_rows, "source_pdf")
    reserves_counts = _count_rows(reserves_rows, "source_pdf")
    economics_counts = _count_rows(economics_rows, "source_pdf")
    economics_with_values = _economics_with_values(economics_rows)

    now = datetime.now(timezone.utc).isoformat()
    summary = {
        "pdfs": len(pdf_metrics),
        "resources_rows": len(resources_rows),
        "reserves_rows": len(reserves_rows),
        "economics_rows": len(economics_rows),
        "economics_with_values": sum(economics_with_values.values()),
        "run_id": manifest.get("run_id"),
        "duration_sec": manifest.get("duration_sec"),
        "strategy": manifest.get("settings", {}).get("extraction_strategy"),
    }

    lines = [
        "# coverage_report",
        "",
        f"Generated: {now}",
        "",
        "## Summary",
        "| Metric | Value |",
        "| --- | --- |",
    ]
    for key, value in summary.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## Per PDF",
            "| PDF | resources | reserves | economics | econ_values | warnings | time_sec | page_count | cache_hit |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    for metric in pdf_metrics:
        pdf = metric.get("source_pdf")
        durations = metric.get("durations_sec", {})
        total = durations.get("total")
        warnings = metric.get("warnings") or []
        lines.append(
            "| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                pdf,
                resources_counts.get(pdf, 0),
                reserves_counts.get(pdf, 0),
                economics_counts.get(pdf, 0),
                economics_with_values.get(pdf, 0),
                len(warnings),
                total,
                metric.get("page_count"),
                metric.get("cache_hit"),
            )
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
