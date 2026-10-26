
"""FastAPI application setup and non-student routes."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.ai_assistant import OllamaUnavailableError, ask_ollama
from app.config import APP_NAME, APP_VERSION
from app.database import init_db
from app.routers import stats as stats_router
from app.routers import students as students_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized.")
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Student CRUD, filtering, pagination, statistics, CSV export, "
        "optional local Ollama Q&A."
    ),
    lifespan=lifespan,
)

app.include_router(students_router.router)
app.include_router(stats_router.router)


class AIQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    model: str = Field(default="llama3.2:1b", min_length=1, max_length=100)


@app.get("/", tags=["Home"])
def home():
    return {
        "message": APP_NAME,
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "features": [
            "CRUD",
            "filtering",
            "pagination",
            "statistics",
            "CSV export",
            "optional Ollama AI",
        ],
    }


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "database": "configured"}


@app.post("/ai/ask", tags=["Optional AI"])
def ai_ask(request: AIQuestion):
    try:
        return ask_ollama(request.question, request.model)
    except OllamaUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
