"""
bm25_retriever.py — BM25 lexical retrieval layer for Specter hybrid search.

Builds a BM25Okapi index over all document chunks stored in ChromaDB
(or loaded from the same source files). Provides search_bm25() returning
results in the same format as embed_store.search_chunks() for seamless
RRF fusion.
"""

import logging
import re
import threading
from typing import List, Dict, Optional

import numpy as np
from rank_bm25 import BM25Okapi

from embed_store import _get_collection

logger = logging.getLogger(__name__)

_BM25_LOCK = threading.Lock()
_BM25: Optional[BM25Okapi] = None
_BM25_CORPUS: List[str] = []
_BM25_METADATA: List[Dict] = []


def tokenise(text: str) -> List[str]:
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return [t for t in text.split() if len(t) > 1]


BATCH_SIZE = 500


def _load_all_chunks_from_chromadb() -> List[Dict]:
    collection = _get_collection()
    count = collection.count()
    if count == 0:
        logger.warning("ChromaDB collection is empty — BM25 index will have no data.")
        return []

    all_docs = []
    all_metas = []
    offset = 0
    while offset < count:
        batch = collection.get(
            include=["documents", "metadatas"],
            limit=BATCH_SIZE,
            offset=offset,
        )
        batch_docs = batch.get("documents", []) or []
        batch_metas = batch.get("metadatas", []) or []
        all_docs.extend(batch_docs)
        all_metas.extend(batch_metas)
        offset += BATCH_SIZE
        logger.info(f"  BM25 load progress: {offset}/{count} chunks")

    seen_texts = set()
    results = []
    for doc, meta in zip(all_docs, all_metas):
        if doc and doc.strip():
            text = doc.strip()
            text_dedup_key = text[:500]
            if text_dedup_key in seen_texts:
                continue
            seen_texts.add(text_dedup_key)
            results.append({
                "text": text,
                "source": (meta or {}).get("source", "legal_kb"),
                "chunk_index": (meta or {}).get("chunk_index", 0),
                "namespace": (meta or {}).get("namespace", "global"),
            })
    dups = len(all_docs) - len(results)
    if dups > 0:
        logger.info(f"Deduplicated {dups} duplicate chunks from BM25 index.")
    logger.info(f"Loaded {len(results)} unique chunks from ChromaDB for BM25 index.")
    return results


def build_bm25_index(force: bool = False) -> BM25Okapi:
    global _BM25, _BM25_CORPUS, _BM25_METADATA

    with _BM25_LOCK:
        if _BM25 is not None and not force:
            return _BM25

        chunks = _load_all_chunks_from_chromadb()
        _BM25_CORPUS = [c["text"] for c in chunks]
        _BM25_METADATA = [{"source": c["source"], "chunk_index": c["chunk_index"],
                           "namespace": c["namespace"]} for c in chunks]

        if not _BM25_CORPUS:
            logger.warning("No chunks available — BM25 index will be empty.")
            _BM25 = BM25Okapi([])
            return _BM25

        tokenized_corpus = [tokenise(doc) for doc in _BM25_CORPUS]
        _BM25 = BM25Okapi(tokenized_corpus)
        logger.info(f"BM25 index built with {len(_BM25_CORPUS)} documents.")
        return _BM25


def search_bm25(query: str, top_k: int = 10) -> List[Dict]:
    bm25 = build_bm25_index()

    if not _BM25_CORPUS:
        return []

    tokenized_query = tokenise(query)
    scores = bm25.get_scores(tokenized_query)

    if scores.max() > 0:
        scores = scores / scores.max()
    else:
        scores = np.zeros_like(scores)

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            "text": _BM25_CORPUS[idx],
            "source": _BM25_METADATA[idx].get("source", "legal_kb"),
            "score": round(float(scores[idx]), 4),
            "chunk_index": _BM25_METADATA[idx].get("chunk_index", int(idx)),
            "namespace": _BM25_METADATA[idx].get("namespace", "global"),
            "retriever": "bm25",
        })

    logger.debug(f"BM25 retrieved {len(results)} results for query: {query[:60]}")
    return results


def rebuild_bm25_index():
    build_bm25_index(force=True)
    logger.info("BM25 index forcibly rebuilt.")
