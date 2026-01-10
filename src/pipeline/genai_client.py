from __future__ import annotations

from typing import Any


def get_genai_client(api_key: str):
    try:
        from google import genai
    except ImportError as exc:
        raise ImportError(
            "google-genai is required. Install with: pip install google-genai"
        ) from exc
    return genai.Client(api_key=api_key)


def extract_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text
    raise ValueError("No text found in GenAI response")


def extract_embedding(response: Any) -> list[float] | None:
    if response is None:
        return None
    if isinstance(response, dict):
        embedding = response.get("embedding")
        if isinstance(embedding, list):
            return embedding
        if isinstance(embedding, dict):
            values = embedding.get("values")
            if isinstance(values, list):
                return values
    embedding = getattr(response, "embedding", None)
    if embedding is not None:
        values = getattr(embedding, "values", None)
        if isinstance(values, list):
            return values
        if isinstance(embedding, list):
            return embedding
    embeddings = getattr(response, "embeddings", None)
    if isinstance(embeddings, list) and embeddings:
        first = embeddings[0]
        values = getattr(first, "values", None)
        if isinstance(values, list):
            return values
        if isinstance(first, list):
            return first
    return None
