"""FastAPI service exposing the RAG assistant over HTTP."""
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import settings
from app.rate_limiter import RateLimiter
from app.service import RagService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings.validate()

app = FastAPI(title="Kira AI Support Assistant", version="1.0.0")

# Lock this down to your real frontend origin(s) in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

service = RagService()
limiter = RateLimiter(settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW_SECONDS)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=settings.MAX_QUESTION_CHARS)
    session_id: str = Field(default="default", max_length=100)


class AskResponse(BaseModel):
    answer: str
    refused: bool
    sources: list[dict]


@app.get("/health")
def health():
    return {"status": "ok", "kb_docs_loaded": len(service.retriever.docs)}


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, request: Request):
    client_key = request.client.host if request.client else "unknown"
    if not limiter.allow(client_key):
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

    result = service.ask(payload.question, session_id=payload.session_id)
    return AskResponse(
        answer=result["answer"],
        refused=result["refused"],
        sources=result.get("sources", []),
    )
