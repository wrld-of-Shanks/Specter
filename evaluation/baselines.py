"""
evaluation/baselines.py
Implements BM25 keyword-search baseline for retrieval comparison.
Ingests the same document chunks that the production vector store uses.
"""

import json
import logging
import os
import re
import sys
from typing import Dict, List, Optional

import numpy as np
from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

# Path to the ChromaDB-adjacent data (the same kb_seed + train files used in seeder)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
DATA_PROCESSED = os.path.join(PROJECT_ROOT, "data", "processed")

# ── tokeniser ───────────────────────────────────────────────────────────────


def tokenise(text: str) -> List[str]:
    """Simple whitespace + punctuation tokeniser, lowercased."""
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return [t for t in text.split() if len(t) > 1]


# ── corpus loader ───────────────────────────────────────────────────────────


def load_corpus_chunks() -> List[str]:
    """Collect all chunk-text strings from the same sources kb_seeder uses."""
    chunks = []

    # 1. kb_seed.jsonl
    kb_path = os.path.join(DATA_PROCESSED, "kb_seed.jsonl")
    if os.path.exists(kb_path):
        with open(kb_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                for key in ("chunk_text", "text_summary", "definition"):
                    val = row.get(key)
                    if val:
                        if isinstance(val, list):
                            chunks.extend(str(v) for v in val)
                        else:
                            chunks.append(str(val))
        logger.info(f"Loaded {len(chunks)} chunks from kb_seed")

    # 2. optimized_legal_train.jsonl
    opt_path = os.path.join(BACKEND_DIR, "optimized_legal_train.jsonl")
    if os.path.exists(opt_path):
        with open(opt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                resp = row.get("response", "").strip()
                prompt = row.get("prompt", "").strip()
                if resp:
                    chunks.append(f"{prompt[:300]} {resp}")
        logger.info(f"Added {len(chunks) - (len(chunks) - len(open(opt_path).readlines()))} chunks from optimized_legal_train")

    # Re-count accurately
    return chunks


# ── singleton BM25 index ────────────────────────────────────────────────────

_BM25: Optional[BM25Okapi] = None
_CORPUS: List[str] = []


def get_bm25_index() -> BM25Okapi:
    global _BM25, _CORPUS
    if _BM25 is not None:
        return _BM25

    _CORPUS = load_corpus_chunks()
    if not _CORPUS:
        logger.warning("Corpus is empty — BM25 will return no results")
        tokenized_corpus = []
    else:
        tokenized_corpus = [tokenise(doc) for doc in _CORPUS]

    _BM25 = BM25Okapi(tokenized_corpus)
    logger.info(f"BM25 index built with {len(_CORPUS)} documents")
    return _BM25


def retrieve_baseline(
    query: str,
    top_k: int = 5,
    source_label: str = "bm25_baseline",
) -> List[Dict]:
    """
    Retrieve top_k chunks using BM25.

    Returns a list of dicts matching the shape produced by `embed_store.search_chunks`:
        [{"text": ..., "source": ..., "score": ..., "chunk_index": ...}, ...]
    """
    bm25 = get_bm25_index()
    if not _CORPUS:
        return []

    tokenized_query = tokenise(query)
    scores = bm25.get_scores(tokenized_query)

    # Normalise scores to [0, 1] range for consistency
    if scores.max() > 0:
        scores = scores / scores.max()
    else:
        scores = np.zeros_like(scores)

    # Get top_k indices
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            "text": _CORPUS[idx][:2000],  # truncate for safety
            "source": source_label,
            "score": round(float(scores[idx]), 4),
            "chunk_index": int(idx),
        })

    return results


def reset_bm25_index():
    """Force re-build on next call (useful after corpus changes)."""
    global _BM25, _CORPUS
    _BM25 = None
    _CORPUS = []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    idx = get_bm25_index()
    print(f"Corpus size: {len(_CORPUS)}")
    q = "What is the punishment for murder under BNS?"
    res = retrieve_baseline(q, top_k=3)
    for r in res:
        print(f"  score={r['score']:.4f} | {r['text'][:100]}...")
