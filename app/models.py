"""Pydantic models defining API schemas used by the service.

These models define both request payloads for the analyze endpoint and
response payloads returned from both analyze and search endpoints. The
Analysis model captures the persisted structure of a single
computation including metadata such as summary, extracted topics,
keywords, sentiment, and a confidence score. Using Pydantic ensures
automatic validation of incoming requests and strict typing for
outgoing responses.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Model representing the body for the POST /analyze endpoint.

    The endpoint accepts either a single text via the ``text`` field or
    a batch of texts via the ``items`` field. At least one of these
    fields must be provided; validation happens in the router.
    """

    text: Optional[str] = Field(
        None, description="A single text string to analyze if provided."
    )
    items: Optional[List[str]] = Field(
        default=None, description="A list of text strings to analyze in batch."
    )


class Analysis(BaseModel):
    """Representation of an analysis result returned to clients.

    Each analysis includes optional ``id`` and ``title`` fields from
    persistence, as well as the original text and all extracted
    structured data. The ``confidence`` score is a heuristic quantifier
    representing the reliability of the analysis.
    """

    id: Optional[str] = None
    title: Optional[str] = None
    summary: str
    topics: List[str]
    sentiment: str
    keywords: List[str]
    confidence: float
    text: str


class AnalyzeResponse(BaseModel):
    """Response wrapper for the analyze endpoint.

    Results are always returned as a list, even for single
    analyses. Clients can inspect individual ``Analysis`` objects in
    the ``results`` field.
    """

    results: List[Analysis]


class SearchResponse(BaseModel):
    """Response wrapper for the search endpoint.

    When searching analyses by topic or keyword, multiple results may
    match; thus, they are wrapped in the ``results`` list. The same
    ``Analysis`` model is reused here.
    """

    results: List[Analysis]