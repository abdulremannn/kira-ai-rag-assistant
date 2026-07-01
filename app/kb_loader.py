"""Loads the knowledge base from a JSON file (safe — no code execution)."""
import json
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class KBDocument:
    id: str
    category: str
    title: str
    content: str


def load_kb(path: str) -> list[KBDocument]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Knowledge base file not found at '{path}'. "
            f"If you're migrating from a kb.py file, convert it to JSON first "
            f"(see scripts/convert_kb.py)."
        )

    with open(file_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    docs = []
    seen_ids = set()
    for i, entry in enumerate(raw):
        missing = [k for k in ("id", "category", "title", "content") if k not in entry]
        if missing:
            raise ValueError(f"KB entry #{i} is missing fields: {missing}")
        if entry["id"] in seen_ids:
            raise ValueError(f"Duplicate KB id found: '{entry['id']}'")
        seen_ids.add(entry["id"])
        docs.append(KBDocument(**entry))

    if not docs:
        raise ValueError("Knowledge base is empty — nothing to serve.")

    logger.info("Loaded %d KB documents from %s", len(docs), path)
    return docs
