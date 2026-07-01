"""In-memory conversation history, per session."""
import time
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass
class Turn:
    question: str
    answer: str
    timestamp: float


class SessionMemory:
    def __init__(self, max_turns: int = 5, ttl_seconds: int = 1800):
        self.max_turns = max_turns
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[str, deque] = defaultdict(lambda: deque(maxlen=max_turns))
        self._last_seen: dict[str, float] = {}

    def _expire_if_stale(self, session_id: str):
        last = self._last_seen.get(session_id)
        if last and (time.monotonic() - last) > self.ttl_seconds:
            self._sessions.pop(session_id, None)
            self._last_seen.pop(session_id, None)

    def get_history(self, session_id: str) -> list[Turn]:
        self._expire_if_stale(session_id)
        return list(self._sessions[session_id])

    def add_turn(self, session_id: str, question: str, answer: str):
        self._expire_if_stale(session_id)
        self._sessions[session_id].append(Turn(question, answer, time.monotonic()))
        self._last_seen[session_id] = time.monotonic()

    def clear(self, session_id: str):
        self._sessions.pop(session_id, None)
        self._last_seen.pop(session_id, None)