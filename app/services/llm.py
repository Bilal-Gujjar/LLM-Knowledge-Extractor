"""Gemini LLM client wrapper with optional mocking.

This module abstracts interactions with Google's Gemini generative
models. It supports switching between real API calls and a mock
implementation for testing. The client exposes high-level methods for
summarizing text and extracting structured metadata. When using the
mock, deterministic values are returned for unit test stability.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from app.config import get_settings


settings = get_settings()



_SUMMARY_PROMPT = (
    "You are a precise assistant. Summarize the user's text in 1–3 sentences."
    " Be concise and neutral."
)

_META_PROMPT = (
    "Extract the following as pure JSON (no extra text):\n"
    "{\n  \"title\": string|null,\n  \"topics\": string[3],\n  \"sentiment\": \"positive\"|\"neutral\"|\"negative\"\n}\n"
    "Rules:\n"
    "- \"title\" should be a short title if one can be inferred; otherwise null.\n"
    "- \"topics\" must be exactly 3 short, general themes.\n"
    "- \"sentiment\" is overall tone (positive/neutral/negative).\n"
    "Return ONLY the JSON."
)


class LLMClient:
    """Thin wrapper around Gemini generative models or a mock implementation."""

    def __init__(self) -> None:
        self.use_mock = settings.USE_MOCK_LLM
        if not self.use_mock:
            if not settings.GOOGLE_API_KEY:
                raise RuntimeError("GOOGLE_API_KEY is required to use the Gemini client.")
            import google.generativeai as genai  

            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def summarize(self, text: str) -> str:
        """Generate a concise summary using the LLM.

        If the client is configured to mock the LLM, a fixed string is
        returned. Otherwise, the Gemini API is invoked with the
        summary prompt followed by user text. On error, the exception is
        propagated to the caller.
        """
        if self.use_mock:
            return "This is a mock summary of the provided text."
        try:
            response = self.model.generate_content([_SUMMARY_PROMPT, text])
            return (response.text or "").strip()
        except Exception as exc:
            logging.exception("LLM summarize failed: %s", exc)
            raise

    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract title, topics and sentiment from text using the LLM.

        The model is instructed to return a JSON object only. If the
        response includes fencing (e.g., ```json) it is stripped before
        parsing. Invalid or missing fields are normalized to sensible
        defaults. When the LLM is mocked, a constant payload is
        returned.
        """
        if self.use_mock:
            return {
                "title": None,
                "topics": ["technology", "ai", "engineering"],
                "sentiment": "neutral",
            }
        try:
            response = self.model.generate_content([_META_PROMPT, text])
            raw = (response.text or "").strip()
            cleaned = raw
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            data = json.loads(cleaned)
            title = data.get("title") if isinstance(data.get("title"), (str, type(None))) else None
            topics = data.get("topics") or []
            sentiment = data.get("sentiment") or "neutral"
            topics = [t for t in topics if isinstance(t, str)]
            if len(topics) >= 3:
                topics = topics[:3]
            else:
                topics = (topics + ["general"] * 3)[:3]
            if sentiment not in {"positive", "neutral", "negative"}:
                sentiment = "neutral"
            return {"title": title, "topics": topics, "sentiment": sentiment}
        except Exception as exc:
            logging.exception("LLM extract_metadata failed: %s", exc)
            raise