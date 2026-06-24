"""
hybrid_retrieval.py — Unified hybrid retrieval entry point.

Orchestrates BM25 lexical retrieval + ChromaDB dense retrieval → RRF fusion.
Optionally supports cross-encoder reranking for further precision.

Supports citation-aware mode: when the query contains legal section/case
citations, BM25 contributions are boosted in RRF since exact keyword
matching is critical for legal citations.
"""

import logging
from typing import List, Dict, Optional

from bm25_retriever import search_bm25, rebuild_bm25_index
from embed_store import search_chunks
from rrf_fusion import fuse_results, detect_citations, CITATION_BOOST

logger = logging.getLogger(__name__)

BM25_TOP_K = 20
DENSE_TOP_K = 20
RRF_TOP_K = 10
RRF_K = 60

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
RERANKER_TOP_K = 5

_cross_encoder = None


def hybrid_search(
    query: str,
    top_k: int = RRF_TOP_K,
    namespace: str = "global",
    use_reranker: bool = False,
    bm25_top_k: int = BM25_TOP_K,
    dense_top_k: int = DENSE_TOP_K,
    citation_boost: bool = True,
) -> List[Dict]:
    bm25_results = search_bm25(query, top_k=bm25_top_k)
    dense_results = search_chunks(query, top_k=dense_top_k, namespace=namespace)

    citation_weight = 1.0
    has_citations = False
    if citation_boost:
        has_citations = detect_citations(query)
        if has_citations:
            citation_weight = CITATION_BOOST
            logger.info(f"Citations detected in query — BM25 boosted x{CITATION_BOOST}")

    fused = fuse_results(
        bm25_results=bm25_results,
        dense_results=dense_results,
        top_k=top_k + 5 if use_reranker else top_k,
        rrf_k=RRF_K,
        citation_weight=citation_weight,
    )

    if use_reranker and fused:
        fused = _rerank(query, fused, top_k=top_k)

    return fused[:top_k]


def _rerank(query: str, results: List[Dict], top_k: int = RERANKER_TOP_K) -> List[Dict]:
    global _cross_encoder
    if _cross_encoder is None:
        try:
            from sentence_transformers import CrossEncoder
            _cross_encoder = CrossEncoder(RERANKER_MODEL)
            logger.info(f"Cross-encoder reranker loaded: {RERANKER_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load cross-encoder: {e}")
            return results

    if not results:
        return results

    pairs = [(query, r["text"]) for r in results]
    try:
        scores = _cross_encoder.predict(pairs, show_progress_bar=False)
    except Exception as e:
        logger.error(f"Cross-encoder prediction failed: {e}")
        return results

    for r, score in zip(results, scores):
        r["reranker_score"] = round(float(score), 4)

    results.sort(key=lambda x: x.get("reranker_score", 0.0), reverse=True)
    logger.debug(f"Cross-encoder reranked {len(results)} results → top {top_k}")
    return results[:top_k]


def rebuild_hybrid_index():
    rebuild_bm25_index()
    logger.info("Hybrid index rebuilt (BM25). ChromaDB index is managed separately.")
