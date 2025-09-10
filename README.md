# LLM Knowledge Extractor (FastAPI + Gemini + Supabase)

This project implements a simple but complete service that takes
unstructured text, generates a concise summary and structured metadata
using an LLM, extracts keywords via a heuristic, stores results in a
database, and exposes a minimal HTTP API. It was designed to meet
requirements for a take‑home assignment.

## Features

- **POST `/api/analyze`** — Accepts a single text via the `text` field
  or a batch of texts via the `items` list. Produces a 1–2 sentence
  summary, a title (if discernible), three topics, sentiment
  classification, and the top three keywords. All results include a
  confidence score and are persisted to the configured database.
- **GET `/api/search?topic=xyz`** — Searches stored analyses where
  `topics` or `keywords` contain the query. Returns a list of
  matching analyses.
- **LLM integration** — Utilizes Google's Gemini models to generate
  summaries and structured metadata. A mock implementation is
  available for tests and offline operation.
- **Keywords extraction** — Implements a deterministic, dependency‑free
  heuristic to select noun‑like keywords based on frequency,
  capitalization, and token length.
- **Persistence** — Supports Supabase for production and an
  in‑memory store for development/testing.
- **Batch processing** — Allows analyzing multiple texts in a single
  request.
- **Robustness** — Returns HTTP 400 for empty inputs and
  gracefully handles LLM failures by returning fallback metadata.
- **Confidence heuristic** — Provides a naive confidence score based
  on text length and LLM availability.
- **Tests** — Includes unit tests for keyword extraction and API
  integration tests using a mock LLM and in‑memory storage.
- **Dockerized** — Comes with a Dockerfile and a compose config for
  easy deployment.

## Getting Started

### 1. Clone and prepare environment

```bash
git clone <this-repo>
cd llm-knowledge-extractor
cp .env.example .env
```

Populate `.env` with your **Google API key** and **Supabase project
details**. If you leave these blank, you should also set
`USE_MOCK_LLM=true` and/or `USE_INMEM_DB=true` depending on your
needs.

### 2. Create the database table

If using Supabase, run the SQL in `migrations/001_create_table.sql`
against your project. This will create the `analyses` table and
indexes.

### 3. Install dependencies and run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Access the
interactive docs at `/docs`.

### 4. Run with Docker

```bash
docker compose up --build
```

### 5. Execute tests

The tests use a mock LLM and in‑memory database. Run them with:

```bash
export USE_MOCK_LLM=true
export USE_INMEM_DB=true
pytest -q
```

## Design Overview

- **Separation of concerns** — The codebase is divided into
  configuration, models, services, routers, and tests. Each service
  (LLM, keywords, DB) encapsulates a single responsibility.
- **Pluggable backends** — Environment flags allow switching between
  real and mock LLMs and between Supabase and an in‑memory store.
  This makes testing fast and offline and simplifies deployment.
- **Lightweight keyword extraction** — A heuristic extractor avoids
  external NLP dependencies while offering reasonable results for
  short texts. It uses simple frequency analysis with boosts for
  capitalized proper nouns and longer tokens.
- **Naive confidence metric** — A simple formula based on text
  length and LLM availability provides a non‑binary sense of result
  reliability.
- **Minimal API** — Only two endpoints are exposed to satisfy the
  assignment requirements. A search API demonstrates basic querying of
  stored data.

## Trade‑offs

- The keyword heuristic may misclassify some terms due to its
  simplicity. Integrating a true POS tagger or keyword extractor
  would require additional dependencies.
- Search uses array containment semantics on topics/keywords and does
  not provide full-text ranking or fuzzy matching.
- LLM failures return generic fallback data rather than partial
  results; more sophisticated retry or caching strategies could be
  added.

## Environment Variables

| Variable           | Purpose                                    |
|--------------------|--------------------------------------------|
| `GOOGLE_API_KEY`   | API key for Gemini models.                 |
| `GEMINI_MODEL`     | Gemini model name (default: 1.5-flash).     |
| `SUPABASE_URL`     | Supabase instance URL.                     |
| `SUPABASE_ANON_KEY`| Supabase anonymous key.                    |
| `SUPABASE_TABLE`   | Table for storing analyses (default: analyses). |
| `USE_MOCK_LLM`     | If `true`, bypass Gemini and return mocks. |
| `USE_INMEM_DB`     | If `true`, store data in memory only.      |

## API Usage Examples

- **Analyze a single text**

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "An article about LLMs improving developer productivity and workflows."}'
```

- **Analyze a batch of texts**

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"items": ["First text about AI.", "Second text about databases."]}'
```

- **Search by topic or keyword**

```bash
curl "http://localhost:8000/api/search?topic=ai"
```

## License

This project is provided for educational purposes as part of a take‑home assignment.