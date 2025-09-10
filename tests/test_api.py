"""Integration tests for API endpoints using TestClient."""

from fastapi.testclient import TestClient


def test_analyze_single(client: TestClient) -> None:
    payload = {"text": "This article discusses LLM systems and their impact on engineering productivity."}
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "results" in data and len(data["results"]) == 1
    item = data["results"][0]
    assert "summary" in item and "topics" in item and "keywords" in item


def test_analyze_batch(client: TestClient) -> None:
    payload = {"items": ["First text about AI.", "Second text about databases."]}
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) == 2


def test_analyze_empty_error(client: TestClient) -> None:
    payload = {"text": "   "}
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 400


def test_search_roundtrip(client: TestClient) -> None:
    client.post("/api/analyze", json={"text": "AI engineering and model evaluation."})
    client.post("/api/analyze", json={"text": "PostgreSQL databases and indexing."})
    res = client.get("/api/search?topic=ai")
    assert res.status_code == 200
    results = res.json()["results"]
    assert isinstance(results, list)