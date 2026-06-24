"""
rrf_fusion.py — Reciprocal Rank Fusion for hybrid retrieval.

Merges ranked results from BM25 and dense vector search using the
standard RRF formula: score = Σ (1 / (k + rank_i))

Where k = 60 and rank is 1-indexed position in each result list.

Supports citation-aware weighting: when the query contains legal
citations (section numbers, act names), BM25 contributions are
boosted since exact keyword matching is more important for citations.
"""

import logging
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

RRF_K = 60
CITATION_BOOST = 1.5

CITATION_PATTERNS = [
    re.compile(r"\b\d{2,4}\s*(?:IPC|BNS|BNSS|CrPC|IT\s*Act|IPA)\b", re.IGNORECASE),
    re.compile(r"\b(?:section|s\.?|sec\.?|art\.?|article)\s+\d{1,4}[A-Z]?\b", re.IGNORECASE),
    re.compile(r"\b\d{2,4}[A-Z]?\s+(?:IPC|BNS|BNSS|CrPC)\b", re.IGNORECASE),
    re.compile(r"\b(?:IPC|BNS|BNSS|CrPC|IT\s*Act)\s+\d{1,4}\b", re.IGNORECASE),
]


def detect_citations(query: str) -> bool:
    for pattern in CITATION_PATTERNS:
        if pattern.search(query):
            return True
    return False


def fuse_results(
    bm25_results: List[Dict],
    dense_results: List[Dict],
    top_k: int = 10,
    rrf_k: int = RRF_K,
    citation_weight: float = 1.0,
) -> List[Dict]:
    if not bm25_results and not dense_results:
        return []

    rrf_scores: Dict[str, Dict] = {}

    bm25_weight = citation_weight

    for rank, result in enumerate(bm25_results, start=1):
        text = result.get("text", "")
        text_key = text[:200]
        contribution = bm25_weight / (rrf_k + rank)
        if text_key not in rrf_scores:
            entry = {
                "text": text,
                "source": result.get("source", "unknown"),
                "chunk_index": result.get("chunk_index", 0),
                "namespace": result.get("namespace", "global"),
                "bm25_score": result.get("score", 0.0),
                "dense_score": 0.0,
                "rrf_score": contribution,
                "sources": [],
            }
            rrf_scores[text_key] = entry
        else:
            entry = rrf_scores[text_key]
            entry["bm25_score"] = max(entry["bm25_score"], result.get("score", 0.0))
            entry["rrf_score"] += contribution

        entry["sources"].append(result.get("source", "bm25"))
        if "bm25" not in entry.setdefault("retrievers", []):
            entry["retrievers"].append("bm25")

    for rank, result in enumerate(dense_results, start=1):
        text = result.get("text", "")
        text_key = text[:200]
        contribution = 1.0 / (rrf_k + rank)
        if text_key not in rrf_scores:
            entry = {
                "text": text,
                "source": result.get("source", "unknown"),
                "chunk_index": result.get("chunk_index", 0),
                "namespace": result.get("namespace", "global"),
                "bm25_score": 0.0,
                "dense_score": result.get("score", 0.0),
                "rrf_score": contribution,
                "sources": [],
            }
            rrf_scores[text_key] = entry
        else:
            entry = rrf_scores[text_key]
            entry["dense_score"] = max(entry["dense_score"], result.get("score", 0.0))
            entry["rrf_score"] += contribution

        entry["sources"].append(result.get("source", "dense"))
        if "dense" not in entry.setdefault("retrievers", []):
            entry["retrievers"].append("dense")

    fused = sorted(rrf_scores.values(), key=lambda x: x["rrf_score"], reverse=True)

    for entry in fused:
        entry["retrievers"] = entry.get("retrievers", [])
        entry["rrf_score"] = round(entry["rrf_score"], 4)
        entry["sources"] = list(set(entry["sources"]))

    top_fused = fused[:top_k]

    if citation_weight > 1.0:
        logger.debug(
            f"Citation-aware RRF (boost={citation_weight}): "
            f"{len(bm25_results)} BM25 + {len(dense_results)} dense "
            f"→ {len(fused)} unique → {len(top_fused)} final."
        )
    else:
        logger.debug(
            f"RRF fusion: {len(bm25_results)} BM25 + {len(dense_results)} dense "
            f"→ {len(fused)} unique → {len(top_fused)} final."
        )

    return top_fused
