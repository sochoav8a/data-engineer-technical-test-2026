from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from .config import Settings
from .observability import configure_logging
from .pipeline import run_pipeline


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Extract NI 43-101 data into structured outputs")
    parser.add_argument("--data-dir", default="data", help="Directory with PDFs")
    parser.add_argument("--output-dir", default="output", help="Output directory for JSON/CSV")
    parser.add_argument("--sqlite-path", default="output/extractions.db", help="SQLite DB path")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of PDFs")
    parser.add_argument("--mode", default=None, choices=["full", "smart"], help="Extraction mode")
    parser.add_argument("--provider", default=None, choices=["gemini", "mock"], help="LLM provider")
    parser.add_argument("--no-embeddings", action="store_true", help="Disable embedding-based ranking")
    parser.add_argument("--no-retries", action="store_true", help="Disable fallback retries")
    parser.add_argument("--dry-run", action="store_true", help="Skip LLM calls and only score/select pages")
    parser.add_argument("--only-resources", action="store_true", help="Extract only resources section")
    parser.add_argument("--only-reserves", action="store_true", help="Extract only reserves section")
    parser.add_argument("--workers", type=int, default=None, help="Parallel workers for PDF processing")
    parser.add_argument("--log-level", default=None, help="Logging level (e.g., INFO, DEBUG)")
    parser.add_argument("--log-dir", default=None, help="Directory for log files")

    args = parser.parse_args()
    settings = Settings()
    settings.data_dir = args.data_dir
    settings.output_dir = args.output_dir
    settings.sqlite_path = args.sqlite_path

    if args.mode:
        settings.extraction_mode = args.mode
    if args.provider:
        settings.llm_provider = args.provider
    if args.no_embeddings:
        settings.embeddings_enabled = False
    if args.no_retries:
        settings.retries_enabled = False
    if args.dry_run:
        settings.dry_run = True
    if args.workers is not None:
        settings.max_workers = args.workers
    if args.log_level:
        settings.log_level = args.log_level
    if args.log_dir:
        settings.log_dir = args.log_dir

    if args.only_resources or args.only_reserves:
        sections = []
        if args.only_resources:
            sections.append("resources")
        if args.only_reserves:
            sections.append("reserves")
        settings.sections = sections

    configure_logging(Path(settings.log_dir) if settings.log_dir else Path(settings.output_dir) / "logs", settings.log_level)
    run_pipeline(
        data_dir=Path(args.data_dir),
        output_dir=Path(args.output_dir),
        sqlite_path=Path(args.sqlite_path),
        settings=settings,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
