"""Embedding + retrieval, with on-disk caching so restarts are instant."""
import hashlib
import logging
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from app.kb_loader import KBDocument

logger = logging.getLogger(__name__)

CACHE_DIR = Path(".cache")


class Retriever:
    def __init__(self, docs: list[KBDocument], model_name: str):
        self.docs = docs
        self.model = SentenceTransformer(model_name)
        self.embeddings = self._load_or_build_embeddings(model_name)

    def _kb_fingerprint(self) -> str:
        """Hash of KB content so cache auto-invalidates when kb.json changes."""
        blob = "".join(f"{d.id}{d.title}{d.content}" for d in self.docs)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]

    def _load_or_build_embeddings(self, model_name: str) -> np.ndarray:
        CACHE_DIR.mkdir(exist_ok=True)
        cache_file = CACHE_DIR / f"embeddings_{self._kb_fingerprint()}.npy"

        if cache_file.exists():
            logger.info("Loading cached embeddings from %s", cache_file)
            return np.load(cache_file)

        logger.info("Building embeddings for %d docs (cache miss)...", len(self.docs))
        texts = [f"{d.title}. {d.content}" for d in self.docs]
        embeddings = self.model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )
        embeddings = np.array(embeddings)

        # Clear stale cache files, then write the fresh one
        for old in CACHE_DIR.glob("embeddings_*.npy"):
            old.unlink()
        np.save(cache_file, embeddings)
        return embeddings

    def retrieve(self, query: str, top_k: int) -> list[tuple[KBDocument, float]]:
        q_emb = self.model.encode([query], normalize_embeddings=True)[0]
        sims = self.embeddings @ q_emb
        top_idx = np.argsort(sims)[::-1][:top_k]
        return [(self.docs[i], float(sims[i])) for i in top_idx]
