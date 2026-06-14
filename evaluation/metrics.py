"""
evaluation/metrics.py
Deterministic functions to evaluate retrieval quality by comparing
retrieved chunks with ground_truth_context.

Implements:
  - Precision@K
  - Recall@K
  - Mean Reciprocal Rank (MRR)
  - Normalized Discounted Cumulative Gain (NDCG)
"""

import logging
import re
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

# ── token overlap helpers ───────────────────────────────────────────────────


def tokenize(text: str) -> Set[str]:
    """Lowercase, split on non-alphanum, return set of tokens >= 2 chars."""
    tokens = re.findall(r"\b[a-z]{2,}\b", text.lower())
    return set(tokens)


def _is_relevant(
    retrieved_text: str,
    ground_truth_context: str,
    threshold: float = 0.15,
) -> bool:
    """
    Determine relevance by token overlap (Jaccard similarity) between
    retrieved chunk text and the ground_truth_context.
    """
    gt_tokens = tokenize(ground_truth_context)
    if not gt_tokens:
        return False
    rt_tokens = tokenize(retrieved_text)
    if not rt_tokens:
        return False
    intersection = gt_tokens & rt_tokens
    jaccard = len(intersection) / len(gt_tokens | rt_tokens)
    return jaccard >= threshold


def _relevance_vector(
    retrieved: List[Dict],
    ground_truth_context: str,
    threshold: float = 0.15,
) -> List[int]:
    """Return binary relevance list [1, 0, 1, ...] for each retrieved item."""
    return [
        1 if _is_relevant(r.get("text", ""), ground_truth_context, threshold)
        else 0
        for r in retrieved
    ]


# ── core metrics ────────────────────────────────────────────────────────────


def precision_at_k(
    retrieved: List[Dict],
    ground_truth_context: str,
    k: int,
    threshold: float = 0.15,
) -> float:
    """
    Precision@K = (# of relevant items in top-K) / K
    """
    if k <= 0 or not retrieved:
        return 0.0
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    rel = _relevance_vector(top_k, ground_truth_context, threshold)
    return sum(rel) / k


def recall_at_k(
    retrieved: List[Dict],
    ground_truth_context: str,
    k: int,
    total_relevant_in_corpus: int = 0,
    threshold: float = 0.15,
) -> float:
    """
    Recall@K = (# of relevant items in top-K) / total_relevant_in_corpus

    If total_relevant_in_corpus is not provided (0), we approximate it as
    the number of relevant items in the full retrieved set (top_k up to len(retrieved)).
    This is a reasonable approximation for evaluation purposes.
    """
    if k <= 0 or not retrieved:
        return 0.0
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    rel_top_k = _relevance_vector(top_k, ground_truth_context, threshold)
    relevant_in_top_k = sum(rel_top_k)

    if total_relevant_in_corpus > 0:
        denominator = total_relevant_in_corpus
    else:
        # Estimate: check relevance across ALL retrieved items
        rel_all = _relevance_vector(retrieved, ground_truth_context, threshold)
        denominator = sum(rel_all) if sum(rel_all) > 0 else relevant_in_top_k

    return relevant_in_top_k / denominator if denominator > 0 else 0.0


def mean_reciprocal_rank(
    retrieved: List[Dict],
    ground_truth_context: str,
    threshold: float = 0.15,
) -> float:
    """
    MRR = 1 / rank_of_first_relevant_item

    Returns 0 if no relevant item is found in the retrieved list.
    """
    if not retrieved:
        return 0.0
    for i, r in enumerate(retrieved):
        if _is_relevant(r.get("text", ""), ground_truth_context, threshold):
            return 1.0 / (i + 1)
    return 0.0


def ndcg_at_k(
    retrieved: List[Dict],
    ground_truth_context: str,
    k: int,
    threshold: float = 0.15,
) -> float:
    """
    NDCG@K = DCG@K / IDCG@K

    Where DCG = sum( (2^rel_i - 1) / log2(i+2) )
    and IDCG is DCG of perfect ranking.
    """
    if k <= 0 or not retrieved:
        return 0.0
    top_k = retrieved[:k]
    if not top_k:
        return 0.0

    relevances = _relevance_vector(top_k, ground_truth_context, threshold)

    # DCG
    dcg = 0.0
    for i, rel in enumerate(relevances):
        dcg += (2**rel - 1) / (i + 2)  # log2(i+2) approximated as i+2

    # IDCG — perfect ordering: all 1s first
    ideal_rel = sorted(relevances, reverse=True)
    idcg = 0.0
    for i, rel in enumerate(ideal_rel):
        idcg += (2**rel - 1) / (i + 2)

    return dcg / idcg if idcg > 0 else 0.0


def compute_all_retrieval_metrics(
    retrieved: List[Dict],
    ground_truth_context: str,
    ks: List[int] = None,
    threshold: float = 0.15,
) -> Dict:
    """
    Compute all retrieval metrics at specified K values.

    Returns a dict like:
    {
        "precision@1": 1.0,
        "precision@3": 0.667,
        "precision@5": 0.4,
        "recall@1": 0.5,
        "recall@3": 1.0,
        "recall@5": 1.0,
        "mrr": 1.0,
        "ndcg@5": 0.9,
    }
    """
    if ks is None:
        ks = [1, 3, 5]

    metrics = {}

    for k in ks:
        metrics[f"precision@{k}"] = round(
            precision_at_k(retrieved, ground_truth_context, k, threshold), 4
        )
        metrics[f"recall@{k}"] = round(
            recall_at_k(retrieved, ground_truth_context, k, threshold=threshold), 4
        )

    metrics["mrr"] = round(
        mean_reciprocal_rank(retrieved, ground_truth_context, threshold), 4
    )

    for k in ks:
        metrics[f"ndcg@{k}"] = round(
            ndcg_at_k(retrieved, ground_truth_context, k, threshold), 4
        )

    return metrics


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Quick self-test
    gt = "Section 103 BNS prescribes death or life imprisonment for murder."
    retrieved = [
        {"text": "Section 103 BNS prescribes death or life imprisonment for murder."},
        {"text": "The sky is blue."},
        {"text": "Murder is defined in Section 101 BNS as culpable homicide."},
        {"text": "Bail is a matter of right for bailable offences."},
        {"text": "Life imprisonment means imprisonment for the remainder of natural life."},
    ]

    metrics = compute_all_retrieval_metrics(retrieved, gt)
    for k, v in metrics.items():
        print(f"  {k}: {v}")
