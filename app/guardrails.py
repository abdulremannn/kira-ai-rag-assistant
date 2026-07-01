"""Guardrail logic: input validation + the retrieval-based relevance gate."""
import re

# Very cheap pre-filter for obvious junk before we even embed anything.
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


class InvalidInput(Exception):
    pass


def validate_question(question: str, max_chars: int) -> str:
    q = question.strip()
    if not q:
        raise InvalidInput("Question is empty.")
    if len(q) > max_chars:
        raise InvalidInput(f"Question is too long (max {max_chars} characters).")
    if _CONTROL_CHARS.search(q):
        raise InvalidInput("Question contains invalid characters.")
    return q


def is_relevant(best_score: float, threshold: float) -> bool:
    return best_score >= threshold
