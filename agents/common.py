"""Shared helpers for the SecureLearn agents."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

DEMO_FILE = Path(__file__).resolve().parent.parent / "demo" / "demo_responses.json"
DEFAULT_MODEL = "gemini-2.5-flash"
MAX_TOPIC_LENGTH = 100


def demo_mode() -> bool:
    return os.getenv("DEMO_MODE", "false").strip().lower() in {"1", "true", "yes", "on"}


def load_demo(key: str):
    """Return one canned response from demo/demo_responses.json."""
    with DEMO_FILE.open("r", encoding="utf-8") as demo_file:
        return json.load(demo_file)[key]


def clean_topic(topic: str) -> str:
    """Trim, collapse whitespace and cap length. Raises ValueError if empty."""
    if not isinstance(topic, str):
        raise ValueError("topic must be a string")
    cleaned = re.sub(r"\s+", " ", topic).strip()
    if not cleaned:
        raise ValueError("topic must not be empty")
    if len(cleaned) > MAX_TOPIC_LENGTH:
        raise ValueError(f"topic must be at most {MAX_TOPIC_LENGTH} characters")
    return cleaned


def slugify(text: str) -> str:
    """Make a safe file name stem: letters, digits and underscores only."""
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug[:60] or "topic"


def extract_json(text: str):
    """Parse JSON from a model reply, tolerating markdown fences and chatter."""
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL)
    if fenced:
        cleaned = fenced.group(1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


class GeminiClient:
    """Thin wrapper over the google-genai SDK. The SDK is imported lazily."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to .env, or set DEMO_MODE=true."
            )
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self.model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    def generate(self, prompt: str) -> str:
        response = self._client.models.generate_content(model=self.model, contents=prompt)
        return response.text or ""
