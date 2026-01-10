from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


class ParseResult:
    def __init__(self, text: str, parser_name: str):
        self.text = text
        self.parser_name = parser_name


def get_pdf_page_count(pdf_path: Path) -> int:
    try:
        info = subprocess.check_output(["pdfinfo", str(pdf_path)], text=True, errors="ignore")
    except subprocess.CalledProcessError:
        return 0
    match = re.search(r"^Pages:\s+(\d+)", info, re.M)
    return int(match.group(1)) if match else 0


def _cache_signature(pdf_path: Path) -> str:
    stat = pdf_path.stat()
    return f"{stat.st_mtime_ns}:{stat.st_size}"


def _cache_path(pdf_path: Path, cache_dir: Path) -> Path:
    digest = hashlib.sha256(str(pdf_path).encode("utf-8")).hexdigest()[:12]
    return cache_dir / f"{pdf_path.stem}-{digest}.json"


def extract_pdf_pages(pdf_path: Path, cache_dir: Path | None = None) -> tuple[list[str], bool]:
    cache_hit = False
    signature = _cache_signature(pdf_path)
    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = _cache_path(pdf_path, cache_dir)
        if cache_path.exists():
            try:
                payload = json.loads(cache_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = None
            if isinstance(payload, dict) and payload.get("signature") == signature:
                pages = payload.get("pages", [])
                if isinstance(pages, list):
                    cache_hit = True
                    return pages, cache_hit

    page_count = get_pdf_page_count(pdf_path)
    if page_count <= 0:
        try:
            text = subprocess.check_output(
                ["pdftotext", "-layout", str(pdf_path), "-"],
                text=True,
                errors="ignore",
            )
        except subprocess.CalledProcessError:
            text = ""
        pages = [text]
        if cache_dir:
            cache_path = _cache_path(pdf_path, cache_dir)
            cache_path.write_text(json.dumps({"signature": signature, "pages": pages}), encoding="utf-8")
        return pages, cache_hit

    pages: list[str] = []
    for page_num in range(1, page_count + 1):
        try:
            text = subprocess.check_output(
                [
                    "pdftotext",
                    "-layout",
                    "-f",
                    str(page_num),
                    "-l",
                    str(page_num),
                    str(pdf_path),
                    "-",
                ],
                text=True,
                errors="ignore",
            )
        except subprocess.CalledProcessError:
            text = ""
        pages.append(text)
    if cache_dir:
        cache_path = _cache_path(pdf_path, cache_dir)
        cache_path.write_text(json.dumps({"signature": signature, "pages": pages}), encoding="utf-8")
    return pages, cache_hit


def parse_pdf_to_markdown(pdf_path: Path, llama_api_key: str | None) -> ParseResult:
    if llama_api_key:
        try:
            from llama_parse import LlamaParse

            parser = LlamaParse(api_key=llama_api_key, result_type="markdown", verbose=False)
            docs = parser.load_data(str(pdf_path))
            text = "\n\n".join(d.text for d in docs)
            return ParseResult(text=text, parser_name="llama_parse")
        except Exception:
            pass

    text = subprocess.check_output(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        text=True,
        errors="ignore",
    )
    return ParseResult(text=text, parser_name="pdftotext")
