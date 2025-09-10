"""Database persistence layer supporting Supabase and in-memory storage.

This module defines two storage backends for analyses: an in-memory
store for development and testing, and a Supabase-based store for
production deployment. The choice of backend is controlled via
environment variables defined in the application settings.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List

from app.config import get_settings


settings = get_settings()

_supabase = None
if not settings.USE_INMEM_DB:
    try:
        from supabase import create_client  
        if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
            _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    except Exception:
        _supabase = None


class InMemoryDB:
    """Simple in-memory storage for analyses.

    This class stores analyses in a Python list. It assigns a UUID if
    one is not provided and supports a basic search by topic or keyword.
    """

    def __init__(self) -> None:
        self._rows: list[dict] = []

    def insert_analysis(self, row: Dict[str, Any]) -> Dict[str, Any]:
        item = dict(row)
        if not item.get("id"):
            item["id"] = str(uuid.uuid4())
        self._rows.append(item)
        return item

    def search(self, topic: str) -> List[Dict[str, Any]]:
        q = (topic or "").lower().strip()
        if not q:
            return list(self._rows)
        results = []
        for r in self._rows:
            topics = [str(t).lower() for t in r.get("topics", [])]
            keywords = [str(k).lower() for k in r.get("keywords", [])]
            if q in topics or q in keywords:
                results.append(r)
        return results


class SupabaseDB:
    """Supabase implementation for persistent storage.

    This class relies on the Supabase Python client to insert and
    query analyses from a Postgres table. It uses array ``contains``
    semantics for searching topics and keywords.
    """

    def __init__(self, table_name: str) -> None:
        if _supabase is None:
            raise RuntimeError(
                "Supabase client not initialized. Check SUPABASE_URL and SUPABASE_ANON_KEY."
            )
        self.client = _supabase
        self.table = table_name

    def insert_analysis(self, row: Dict[str, Any]) -> Dict[str, Any]:
        res = self.client.table(self.table).insert(row).execute()
        data = getattr(res, "data", None)
        if data and len(data) > 0:
            return data[0]
        raise RuntimeError(f"Supabase insert failed: {res}")

    def search(self, topic: str) -> List[Dict[str, Any]]:
        q = (topic or "").strip()
        if not q:
            res = (
                self.client.table(self.table)
                .select("*")
                .order("created_at", desc=True)
                .limit(100)
                .execute()
            )
            return getattr(res, "data", []) or []

        topics_res = self.client.table(self.table).select("*").contains("topics", [q]).execute()
        keywords_res = (
            self.client.table(self.table).select("*").contains("keywords", [q]).execute()
        )
        ids: set[str] = set()
        results: list[dict] = []
        for row in getattr(topics_res, "data", []) or []:
            rid = row.get("id")
            if rid not in ids:
                ids.add(rid)
                results.append(row)
        for row in getattr(keywords_res, "data", []) or []:
            rid = row.get("id")
            if rid not in ids:
                ids.add(rid)
                results.append(row)
        return results


def get_db() -> InMemoryDB | SupabaseDB:
    """Return the appropriate database backend based on settings."""
    if settings.USE_INMEM_DB:
        return InMemoryDB()
    return SupabaseDB(settings.SUPABASE_TABLE)