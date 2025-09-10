"""Routes implementing the /analyze API endpoint."""

from typing import List

from fastapi import APIRouter, HTTPException

from app.models import AnalyzeRequest, AnalyzeResponse, Analysis
from app.services.keywords import extract_top3_nouns_like
from app.services.llm import LLMClient
from app.services.db import get_db
import math


router = APIRouter()

llm_client = LLMClient()
db = get_db()


def _confidence_heuristic(text: str, llm_ok: bool) -> float:
    """Compute a naive confidence score for a given text.

    The heuristic starts from a base of 0.55 and grows with the
    logarithm of the number of words, saturating at +0.30. A small
    bonus is added if the LLM successfully responded. Scores are
    clamped to the range [0.5, 0.98].
    """
    n = max(1, len(text.split()))
    length_bonus = min(0.30, math.log10(n + 9) / 10.0)
    llm_bonus = 0.10 if llm_ok else 0.0
    conf = 0.55 + length_bonus + llm_bonus
    return max(0.50, min(0.98, round(conf, 3)))


def _analyze_single(text: str) -> Analysis:
    """Process a single piece of text and return an Analysis object.

    This function coordinates keyword extraction, LLM calls for
    summary and metadata, computes a confidence score, persists the
    record, and returns the resulting Analysis. Exceptions from the
    LLM are caught and handled gracefully.
    """
    t = (text or "").strip()
    if not t:
        raise HTTPException(status_code=400, detail="Empty input text.")

    keywords = extract_top3_nouns_like(t)

    summary = ""
    title = None
    topics: List[str] = []
    sentiment = "neutral"
    llm_ok = True
    try:
        summary = llm_client.summarize(t)
        meta = llm_client.extract_metadata(t)
        title = meta.get("title")
        topics = meta.get("topics", [])
        sentiment = meta.get("sentiment", "neutral")
    except Exception:

        llm_ok = False
        summary = "LLM unavailable. Summary could not be generated."
        title = None
        topics = ["general", "unknown", "llm-failure"]
        sentiment = "neutral"

    confidence = _confidence_heuristic(t, llm_ok)

    row = {
        "title": title,
        "summary": summary,
        "topics": topics,
        "sentiment": sentiment,
        "keywords": keywords,
        "confidence": confidence,
        "text": t,
    }
    saved = db.insert_analysis(row)
    return Analysis(**saved)


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Endpoint to analyze single or batch texts.

    At least one of ``text`` or ``items`` must be provided. Batch
    processing is supported via the ``items`` list. Validation is
    performed to ensure non-empty inputs. Returns a list of results.
    """
    items: List[str] = []
    if payload.items is not None:
        if not isinstance(payload.items, list) or len(payload.items) == 0:
            raise HTTPException(
                status_code=400,
                detail="Batch 'items' must be a non-empty list of strings.",
            )
        items = payload.items
    elif payload.text is not None:
        items = [payload.text]
    else:
        raise HTTPException(
            status_code=400, detail="Provide 'text' or 'items' with data."
        )

    results: List[Analysis] = []
    for t in items:
        results.append(_analyze_single(t))
    return AnalyzeResponse(results=results)