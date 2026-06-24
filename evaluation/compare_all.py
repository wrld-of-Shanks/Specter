"""
evaluation/compare_all.py — Comprehensive comparison across all retrieval strategies.

Tests: Dense-Only, BM25-Only, Hybrid (standard RRF), Hybrid+Reranker,
       Citation-Aware Hybrid, Citation-Aware Hybrid+Reranker.

Outputs a comparison table and saves JSON results.
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, List, Optional

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "evaluation"))

from embed_store import search_chunks as dense_search
from bm25_retriever import search_bm25
from hybrid_retrieval import hybrid_search
from metrics import compute_all_retrieval_metrics

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("compare_all")
logger.setLevel(logging.INFO)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_EVAL_SET = os.path.join(PROJECT_ROOT, "data", "evaluation_set.json")

STRATEGIES = {
    "dense": {
        "label": "Dense-Only",
        "runner": lambda q, **kw: dense_search(q, top_k=kw.get("top_k", 10), namespace=kw.get("namespace", "global")),
    },
    "bm25": {
        "label": "BM25-Only",
        "runner": lambda q, **kw: search_bm25(q, top_k=kw.get("top_k", 10)),
    },
    "hybrid": {
        "label": "Hybrid (RRF)",
        "runner": lambda q, **kw: hybrid_search(
            q, top_k=kw.get("top_k", 10), namespace=kw.get("namespace", "global"),
            bm25_top_k=20, dense_top_k=20, use_reranker=False, citation_boost=False,
        ),
    },
    "hybrid_reranker": {
        "label": "Hybrid + Reranker",
        "runner": lambda q, **kw: hybrid_search(
            q, top_k=kw.get("top_k", 10), namespace=kw.get("namespace", "global"),
            bm25_top_k=20, dense_top_k=20, use_reranker=True, citation_boost=False,
        ),
    },
    "hybrid_citation": {
        "label": "Hybrid + Citation",
        "runner": lambda q, **kw: hybrid_search(
            q, top_k=kw.get("top_k", 10), namespace=kw.get("namespace", "global"),
            bm25_top_k=20, dense_top_k=20, use_reranker=False, citation_boost=True,
        ),
    },
    "hybrid_full": {
        "label": "Hybrid + Citation + Reranker",
        "runner": lambda q, **kw: hybrid_search(
            q, top_k=kw.get("top_k", 10), namespace=kw.get("namespace", "global"),
            bm25_top_k=20, dense_top_k=20, use_reranker=True, citation_boost=True,
        ),
    },
}


def load_eval_set(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Loaded {len(data)} evaluation samples from {path}")
    return data


def evaluate_strategy(
    key: str,
    samples: List[Dict],
    top_k: int = 10,
) -> Dict:
    cfg = STRATEGIES[key]
    runner = cfg["runner"]
    latencies = []
    hit_count = 0
    all_metrics = []

    for i, sample in enumerate(samples):
        query = sample["query"]
        gt_context = sample.get("ground_truth_context", "")
        if not gt_context:
            continue

        start = time.time()
        try:
            results = runner(query, top_k=top_k)
        except Exception as e:
            logger.error(f"[{key}] Sample {sample.get('id', i)} failed: {e}")
            results = []
        elapsed = time.time() - start
        latencies.append(elapsed)

        hit = any(
            gt_context.lower()[:60] in r.get("text", "").lower()
            or r.get("text", "").lower().startswith(gt_context.lower()[:60])
            for r in results[:top_k]
        )
        if hit:
            hit_count += 1

        metrics = compute_all_retrieval_metrics(
            results, gt_context, ks=[5, 10], threshold=0.12,
        )
        all_metrics.append(metrics)

    n = len(all_metrics)
    if n == 0:
        return {"error": "No samples with ground_truth_context", "mode": key}

    avg_metrics = {}
    for mk in all_metrics[0]:
        avg_metrics[mk] = round(sum(m[mk] for m in all_metrics) / n, 4)

    return {
        "mode": key,
        "label": cfg["label"],
        "samples": n,
        "hit_rate": round(hit_count / n, 4) if n > 0 else 0.0,
        "avg_latency_s": round(float(np.mean(latencies)), 4) if latencies else 0.0,
        **avg_metrics,
    }


def print_table(results: List[Dict]):
    print()
    print("=" * 120)
    print("  COMPREHENSIVE RETRIEVAL STRATEGY COMPARISON")
    print("=" * 120)

    metrics_to_show = [
        ("Hit Rate", "hit_rate"),
        ("Recall@5", "recall@5"),
        ("Recall@10", "recall@10"),
        ("Precision@5", "precision@5"),
        ("Precision@10", "precision@10"),
        ("MRR", "mrr"),
        ("NDCG@5", "ndcg@5"),
        ("NDCG@10", "ndcg@10"),
        ("Avg Latency (s)", "avg_latency_s"),
    ]

    header = f"{'Metric':<22}"
    for r in results:
        header += f"  {r['label']:<24}"
    print(header)
    print("-" * len(header))

    for label, key in metrics_to_show:
        row = f"{label:<22}"
        for r in results:
            val = r.get(key, "N/A")
            if isinstance(val, float):
                row += f"  {val:<24.4f}"
            else:
                row += f"  {str(val):<24}"
        print(row)

    print("=" * 120)

    if results:
        best_hr = max(r["hit_rate"] for r in results)
        best_mrr = max(r["mrr"] for r in results)
        best_r5 = max(r["recall@5"] for r in results)
        best_r10 = max(r["recall@10"] for r in results)
        print(f"  Best Hit Rate : {best_hr:.4f}")
        print(f"  Best MRR      : {best_mrr:.4f}")
        print(f"  Best Recall@5 : {best_r5:.4f}")
        print(f"  Best Recall@10: {best_r10:.4f}")
    print("=" * 120)
    print()

    for r in results:
        if r["mode"] == "hybrid_full":
            dense = next(x for x in results if x["mode"] == "dense")
            print(f"  Hybrid+Citation+Reranker vs Dense:")
            print(f"    Hit Rate : {r['hit_rate']:.4f} vs {dense['hit_rate']:.4f} "
                  f"({'▲' if r['hit_rate'] > dense['hit_rate'] else '▼'} "
                  f"{abs(r['hit_rate'] - dense['hit_rate'])*100:.1f}%)")
            print(f"    MRR      : {r['mrr']:.4f} vs {dense['mrr']:.4f} "
                  f"({'▲' if r['mrr'] > dense['mrr'] else '▼'} "
                  f"{abs(r['mrr'] - dense['mrr'])*100:.1f}%)")
            print(f"    Recall@10: {r['recall@10']:.4f} vs {dense['recall@10']:.4f} "
                  f"({'▲' if r['recall@10'] > dense['recall@10'] else '▼'} "
                  f"{abs(r['recall@10'] - dense['recall@10'])*100:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Compare all retrieval strategies")
    parser.add_argument("--eval-set", default=DEFAULT_EVAL_SET)
    parser.add_argument("--max-samples", type=int, default=50)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--strategies", nargs="+",
                        default=["dense", "bm25", "hybrid", "hybrid_citation",
                                 "hybrid_reranker", "hybrid_full"],
                        help="Strategies to compare")
    args = parser.parse_args()

    if not os.path.exists(args.eval_set):
        logger.error(f"Evaluation set not found: {args.eval_set}")
        sys.exit(1)

    samples = load_eval_set(args.eval_set)
    if args.max_samples > 0:
        samples = samples[:args.max_samples]
        logger.info(f"Limited to {args.max_samples} samples")

    results = []
    for key in args.strategies:
        if key not in STRATEGIES:
            logger.warning(f"Unknown strategy: {key}")
            continue
        logger.info(f"Evaluating: {STRATEGIES[key]['label']}")
        result = evaluate_strategy(key, samples, top_k=args.top_k)
        results.append(result)
        hr = result.get("hit_rate", "N/A")
        r10 = result.get("recall@10", "N/A")
        mrr = result.get("mrr", "N/A")
        logger.info(f"  {result.get('label', key)}: HR={hr} R@10={r10} MRR={mrr}")

    print_table(results)

    output_path = os.path.join(
        os.path.dirname(__file__), "retrieval_strategy_comparison.json"
    )
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
