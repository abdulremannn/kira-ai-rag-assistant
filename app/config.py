"""Centralized configuration. All tunables live here, loaded from env vars."""
import os
from dotenv import load_dotenv

load_dotenv()


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


class Settings:
    # --- Secrets / API ---
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")

    # --- Model config (fallback chain: primary tried first, then fallback) ---
    PRIMARY_MODEL: str = os.environ.get("PRIMARY_MODEL", "llama-3.3-70b-versatile")
    FALLBACK_MODEL: str = os.environ.get("FALLBACK_MODEL", "llama-3.1-8b-instant")
    EMBED_MODEL_NAME: str = os.environ.get("EMBED_MODEL_NAME", "all-MiniLM-L6-v2")

    # --- Retrieval / guardrails ---
    KB_PATH: str = os.environ.get("KB_PATH", "data/kb.json")
    TOP_K: int = _get_int("TOP_K", 4)
    RELEVANCE_THRESHOLD: float = _get_float("RELEVANCE_THRESHOLD", 0.30)
    MAX_QUESTION_CHARS: int = _get_int("MAX_QUESTION_CHARS", 500)
    MAX_ANSWER_TOKENS: int = _get_int("MAX_ANSWER_TOKENS", 100)  # keeps answers short

    # --- Rate limiting (per-IP, simple in-memory) ---
    RATE_LIMIT_REQUESTS: int = _get_int("RATE_LIMIT_REQUESTS", 20)
    RATE_LIMIT_WINDOW_SECONDS: int = _get_int("RATE_LIMIT_WINDOW_SECONDS", 60)

    # --- Support contact shown in refusals ---
    SUPPORT_EMAIL: str = os.environ.get("SUPPORT_EMAIL", "support@kira.ai")

    def validate(self):
        if not self.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Create a .env file with GROQ_API_KEY=... "
                "(see .env.example)."
            )


settings = Settings()
