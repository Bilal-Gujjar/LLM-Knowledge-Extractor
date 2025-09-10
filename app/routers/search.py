"""Routes implementing the /search API endpoint."""

from typing import Optional

from fastapi import APIRouter, Query

from app.models import SearchResponse, Analysis
from app.services.db import get_db


router = APIRouter()


db = get_db()


@router.get("/search", response_model=SearchResponse)
def search(topic: Optional[str] = Query(default=None, description="Topic or keyword to match.")) -> SearchResponse:
    """Endpoint to search analyses by topic or keyword.

    The ``topic`` query parameter is matched against both the
    ``topics`` and ``keywords`` arrays stored in each analysis. If
    omitted, all analyses are returned (limited by backend).
    """
    rows = db.search(topic or "")
    results = [Analysis(**r) for r in rows]
    return SearchResponse(results=results)