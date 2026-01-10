from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def _load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _estimate_tokens(chars: int, chars_per_token: float) -> float:
    if chars_per_token <= 0:
        return 0.0
    return chars / chars_per_token


def _read_json_output(output_dir: Path, pdf_name: str) -> int:
    stem = Path(pdf_name).stem
    path = output_dir / "json" / f"{stem}.json"
    if not path.exists():
        return 0
    return len(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Estimate LLM cost from run_manifest.json + JSON outputs"
    )
    parser.add_argument(
        "--manifest", default="output/run_manifest.json", help="Path to run_manifest.json"
    )
    parser.add_argument("--output-dir", default="output", help="Output directory with json/ folder")
    parser.add_argument("--chars-per-token", type=float, default=4.0, help="Approx chars per token")
    parser.add_argument("--input-per-1m", type=float, default=0.30, help="USD per 1M input tokens")
    parser.add_argument(
        "--output-per-1m", type=float, default=2.50, help="USD per 1M output tokens"
    )
    args = parser.parse_args()

    manifest = _load_manifest(Path(args.manifest))
    output_dir = Path(args.output_dir)

    totals = defaultdict(float)
    rows = []

    for metric in manifest.get("pdfs", []):
        pdf = metric.get("source_pdf")
        input_chars = sum(metric.get("llm_input_chars", {}).values())
        output_chars = _read_json_output(output_dir, pdf) if pdf else 0
        input_tokens = _estimate_tokens(input_chars, args.chars_per_token)
        output_tokens = _estimate_tokens(output_chars, args.chars_per_token)

        input_cost = (input_tokens / 1_000_000) * args.input_per_1m
        output_cost = (output_tokens / 1_000_000) * args.output_per_1m
        total_cost = input_cost + output_cost

        totals["input_chars"] += input_chars
        totals["output_chars"] += output_chars
        totals["input_tokens"] += input_tokens
        totals["output_tokens"] += output_tokens
        totals["input_cost"] += input_cost
        totals["output_cost"] += output_cost
        totals["total_cost"] += total_cost

        rows.append(
            {
                "pdf": pdf,
                "input_chars": int(input_chars),
                "output_chars": int(output_chars),
                "input_tokens": round(input_tokens, 1),
                "output_tokens": round(output_tokens, 1),
                "estimated_cost_usd": round(total_cost, 4),
            }
        )

    now = datetime.now(timezone.utc).isoformat()
    print(f"Estimate generated: {now}")
    print("Per PDF:")
    for row in rows:
        print(
            "- {pdf}: input_chars={input_chars}, output_chars={output_chars}, "
            "input_tokens={input_tokens}, output_tokens={output_tokens}, cost=${estimated_cost_usd}".format(
                **row
            )
        )

    print("\nTotals:")
    print(f"- input_chars: {int(totals['input_chars'])}")
    print(f"- output_chars: {int(totals['output_chars'])}")
    print(f"- input_tokens: {round(totals['input_tokens'], 1)}")
    print(f"- output_tokens: {round(totals['output_tokens'], 1)}")
    print(f"- input_cost_usd: {round(totals['input_cost'], 4)}")
    print(f"- output_cost_usd: {round(totals['output_cost'], 4)}")
    print(f"- total_cost_usd: {round(totals['total_cost'], 4)}")


if __name__ == "__main__":
    main()
