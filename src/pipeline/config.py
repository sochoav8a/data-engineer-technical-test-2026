from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    data_dir: str = "data"
    output_dir: str = "output"
    sqlite_path: str = "output/extractions.db"
    model_name: str = "models/gemini-flash-latest"
    gemini_api_key: str | None = None
    llama_parse_api_key: str | None = None
    extraction_mode: str = "smart"  # full | smart
    extraction_strategy: str = "two_stage"  # two_stage | single
    max_chars: int = 350000
    llm_provider: str = "gemini"  # gemini | mock
    page_window: int = 1
    max_workers: int = 1
    log_level: str = "INFO"
    log_dir: str | None = None
    dry_run: bool = False
    sections: list[str] = field(
        default_factory=lambda: ["metadata", "resources", "reserves", "economics"]
    )

    # Embeddings
    embeddings_enabled: bool = True
    embedding_model: str = "models/text-embedding-004"
    embedding_max_chars: int = 4000
    embedding_max_pages: int = 60

    # Retry settings
    retries_enabled: bool = True
    retry_model: str = ""
    use_retry_model: bool = False

    def __post_init__(self) -> None:
        self.data_dir = os.getenv("DATA_DIR", self.data_dir)
        self.output_dir = os.getenv("OUTPUT_DIR", self.output_dir)
        self.sqlite_path = os.getenv("SQLITE_PATH", self.sqlite_path)
        self.model_name = os.getenv("GEMINI_MODEL", self.model_name)
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", self.gemini_api_key)
        self.llama_parse_api_key = os.getenv("LLAMA_PARSE_API_KEY", self.llama_parse_api_key)
        self.extraction_mode = os.getenv("EXTRACTION_MODE", self.extraction_mode)
        self.extraction_strategy = os.getenv("EXTRACTION_STRATEGY", self.extraction_strategy)
        self.max_chars = int(os.getenv("MAX_CHARS", str(self.max_chars)))
        self.llm_provider = os.getenv("LLM_PROVIDER", self.llm_provider)
        self.page_window = int(os.getenv("PAGE_WINDOW", str(self.page_window)))
        self.max_workers = int(os.getenv("MAX_WORKERS", str(self.max_workers)))
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        self.log_dir = os.getenv("LOG_DIR", self.log_dir)
        self.dry_run = os.getenv("DRY_RUN", str(self.dry_run)).lower() in ["1", "true", "yes"]

        sections_env = os.getenv("SECTIONS")
        if sections_env:
            self.sections = [
                section.strip() for section in sections_env.split(",") if section.strip()
            ]

        self.embeddings_enabled = os.getenv(
            "EMBEDDINGS_ENABLED", str(self.embeddings_enabled)
        ).lower() in [
            "1",
            "true",
            "yes",
        ]
        self.embedding_model = os.getenv("EMBEDDING_MODEL", self.embedding_model)
        self.embedding_max_chars = int(
            os.getenv("EMBEDDING_MAX_CHARS", str(self.embedding_max_chars))
        )
        self.embedding_max_pages = int(
            os.getenv("EMBEDDING_MAX_PAGES", str(self.embedding_max_pages))
        )

        self.retries_enabled = os.getenv("RETRIES_ENABLED", str(self.retries_enabled)).lower() in [
            "1",
            "true",
            "yes",
        ]
        self.retry_model = os.getenv("RETRY_MODEL", self.retry_model)
        self.use_retry_model = os.getenv("USE_RETRY_MODEL", str(self.use_retry_model)).lower() in [
            "1",
            "true",
            "yes",
        ]
