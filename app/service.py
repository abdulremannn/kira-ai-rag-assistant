"""Core service: orchestrates retrieval, guardrails, and LLM generation."""
import logging
import time

from app.config import settings
from app.guardrails import InvalidInput, is_relevant, validate_question
from app.kb_loader import load_kb
from app.llm import generate_answer
from app.retriever import Retriever
from app.session_memory import SessionMemory

logger = logging.getLogger(__name__)

OFF_TOPIC_MESSAGE = (
    "I'm the Kira AI support assistant, so I can only help with questions "
    f"about Kira AI's product, features, account, billing, or privacy. "
    f"For anything else, contact {settings.SUPPORT_EMAIL}."
)


class RagService:
    def __init__(self):
        docs = load_kb(settings.KB_PATH)
        self.retriever = Retriever(docs, settings.EMBED_MODEL_NAME)
        self.memory = SessionMemory(max_turns=5, ttl_seconds=1800)

    def ask(self, raw_question: str, session_id: str = "default") -> dict:
        start = time.monotonic()

        try:
            question = validate_question(raw_question, settings.MAX_QUESTION_CHARS)
        except InvalidInput as e:
            return {"answer": str(e), "sources": [], "refused": True, "reason": "invalid_input"}

        history = self.memory.get_history(session_id)
        search_query = question
        if history:
            search_query = f"{history[-1].question} {question}"

        results = self.retriever.retrieve(search_query, settings.TOP_K)
        best_score = results[0][1] if results else 0.0

        if not is_relevant(best_score, settings.RELEVANCE_THRESHOLD):
            logger.info(
                "REFUSED (score=%.3f) q=%r best_match=%r",
                best_score, question, results[0][0].title if results else None,
            )
            return {
                "answer": OFF_TOPIC_MESSAGE,
                "sources": [],
                "refused": True,
                "reason": "below_threshold",
                "top_score": round(best_score, 3),
            }

        answer = generate_answer(question, results, history)
        elapsed_ms = round((time.monotonic() - start) * 1000)

        self.memory.add_turn(session_id, question, answer)

        logger.info(
            "ANSWERED (score=%.3f, %dms) q=%r top_source=%r",
            best_score, elapsed_ms, question, results[0][0].id,
        )

        return {
            "answer": answer,
            "sources": [
                {"id": d.id, "title": d.title, "category": d.category, "score": round(s, 3)}
                for d, s in results
            ],
            "refused": False,
            "top_score": round(best_score, 3),
            "latency_ms": elapsed_ms,
        }
