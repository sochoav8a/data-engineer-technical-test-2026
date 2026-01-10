from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


def configure_logging(log_dir: Path | None, level: str = "INFO") -> Path:
    target_dir = log_dir or Path("output") / "logs"
    target_dir.mkdir(parents=True, exist_ok=True)
    log_path = target_dir / "run.log"

    root = logging.getLogger()
    if getattr(root, "_configured", False):
        return log_path

    root.setLevel(level.upper())
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    root._configured = True
    return log_path


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    logger.info(json.dumps(payload, ensure_ascii=True, sort_keys=True))
