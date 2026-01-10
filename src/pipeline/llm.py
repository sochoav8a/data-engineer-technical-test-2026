from __future__ import annotations

import json
import re
from typing import Any, Type, TypeVar

from pydantic import BaseModel

from .genai_client import extract_text, get_genai_client
from .models import ExtractionResult

T = TypeVar("T", bound=BaseModel)

SYSTEM_PROMPT = """You are a data extraction engine for NI 43-101 mining technical reports.
Extract ONLY the fields in the provided JSON schema. Return valid JSON and nothing else.
If a field is missing, set it to null or [] as appropriate.
Do not convert units or scale values; keep value as shown in the document.
Fill `raw` with the original string and `unit` with the unit text if present.
Use source_pages only from Page N references in the provided context. Ignore table of contents page numbers.
Use the document content only; do not guess.
Tables may appear as CSV/TSV text; use the headers and numeric rows to extract values.
"""

SECTION_TASKS = {
    "metadata": (
        "Extract project metadata (project name, company name, location country/region, report date). "
        "Use report_date in ISO format if possible and keep the original in report_date_raw."
    ),
    "resources": (
        "Extract mineral resources (Measured, Indicated, Inferred). "
        "If a combined category appears (e.g., Measured + Indicated), capture it as its own row. "
        "For each row include category, tonnes, grade, metal, contained_metal, and source_pages."
    ),
    "reserves": (
        "Extract mineral reserves (Proven, Probable). "
        "If a combined category appears (e.g., Proven + Probable), capture it as its own row. "
        "Do not invent reserves if only resource categories are present. "
        "For each row include category, tonnes, grade, metal, contained_metal, and source_pages."
    ),
    "economics": (
        "Extract CAPEX, OPEX, NPV, and IRR with units and currency when available. "
        "Return null when a field is not present."
    ),
}


def _extract_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("No JSON object found in LLM response")
    return json.loads(match.group(0))


def _build_prompt(document_text: str, schema: dict[str, Any], task: str | None = None) -> str:
    prompt = SYSTEM_PROMPT
    if task:
        prompt += f"\n\nTask: {task}\n"
    return (
        prompt
        + "\nJSON schema:\n"
        + json.dumps(schema, indent=2)
        + "\n\nDocument content:\n"
        + document_text
    )


def _call_gemini(
    document_text: str, model_name: str, api_key: str, schema: dict[str, Any], task: str | None
) -> dict[str, Any]:
    client = get_genai_client(api_key)
    prompt = _build_prompt(document_text, schema, task)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={"temperature": 0.1},
    )
    return _extract_json(extract_text(response))


def extract_with_schema(
    document_text: str,
    model_name: str,
    api_key: str | None,
    provider: str,
    schema_model: Type[T],
    task: str | None = None,
) -> T:
    if provider == "mock":
        return schema_model()
    if provider != "gemini":
        raise ValueError(f"Unsupported LLM provider: {provider}")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required for gemini extraction")

    schema = schema_model.model_json_schema()
    data = _call_gemini(document_text, model_name, api_key, schema, task)
    return schema_model.model_validate(data)


def extract_structured(
    document_text: str, model_name: str, api_key: str | None, provider: str
) -> ExtractionResult:
    return extract_with_schema(
        document_text=document_text,
        model_name=model_name,
        api_key=api_key,
        provider=provider,
        schema_model=ExtractionResult,
        task=None,
    )
