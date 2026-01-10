from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .genai_client import extract_embedding, get_genai_client


@dataclass
class EmbeddingSettings:
    enabled: bool
    api_key: str | None
    model_name: str
    max_chars: int
    max_pages: int


def _hash_text(model_name: str, text: str) -> str:
    digest = hashlib.sha256(f"{model_name}::{text}".encode("utf-8")).hexdigest()
    return digest


def cosine_similarity(vec_a: Iterable[float] | None, vec_b: Iterable[float] | None) -> float:
    if not vec_a or not vec_b:
        return 0.0
    a = list(vec_a)
    b = list(vec_b)
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class EmbeddingStore:
    def __init__(self, cache_dir: Path, settings: EmbeddingSettings) -> None:
        self.cache_dir = cache_dir
        self.settings = settings
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, model_name: str, text: str) -> Path:
        digest = _hash_text(model_name, text)
        return self.cache_dir / f"{digest}.json"

    def _load_cache(self, path: Path) -> list[float] | None:
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        if isinstance(data, dict) and "embedding" in data:
            return data.get("embedding")
        if isinstance(data, list):
            return data
        return None

    def _save_cache(self, path: Path, embedding: list[float]) -> None:
        path.write_text(json.dumps({"embedding": embedding}), encoding="utf-8")

    def embed_text(self, text: str) -> list[float] | None:
        if not self.settings.enabled or not self.settings.api_key:
            return None

        clipped = text[: self.settings.max_chars]
        cache_path = self._cache_path(self.settings.model_name, clipped)
        cached = self._load_cache(cache_path)
        if cached:
            return cached

        client = get_genai_client(self.settings.api_key)
        response = client.models.embed_content(
            model=self.settings.model_name,
            contents=clipped,
        )
        embedding = extract_embedding(response)
        if not embedding:
            return None
        self._save_cache(cache_path, embedding)
        return embedding
