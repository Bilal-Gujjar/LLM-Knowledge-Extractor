"""FastAPI application initialization module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import analyze, search


settings = get_settings()


app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix=settings.API_PREFIX, tags=["analyze"])
app.include_router(search.router, prefix=settings.API_PREFIX, tags=["search"])


@app.get("/")
def root() -> dict[str, dict[str, str]]:
    """Root endpoint providing basic service metadata."""
    return {
        "name": settings.APP_NAME,
        "endpoints": {
            "POST /api/analyze": "Analyze single text or batch.",
            "GET /api/search?topic=xyz": "Search analyses by topic or keyword.",
        },
    }