"""
evaluation/compare_retrieval.py — Compare Dense-Only, BM25-Only, and Hybrid (BM25+Dense+RRF).

Evaluates each retrieval strategy on the evaluation set and outputs a
comparison table with Recall@5, Recall@10, MRR, Hit Rate, and Latency.
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

from embed_store import search_chunks as dense_search
from bm25_retriever import search_bm25
from hybrid_retrieval import hybrid_search
from metrics import compute_all_retrieval_metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("compare_retrieval")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_EVAL_SET = os.path.join(PROJECT_ROOT, "data", "evaluation_set.json")

RETRIEVAL_MODES = {
    "dense": lambda q, **kw: dense_search(q, top_k=kw.get("top_k", 10), namespace=kw.get("namespace", "global")),
    "bm25": lambda q, **kw: search_bm25(q, top_k=kw.get("top_k", 10)),
    "hybrid": lambda q, **kw: hybrid_search(
        q, top_k=kw.get("top_k", 10), namespace=kw.get("namespace", "global"),
        bm25_top_k=20, dense_top_k=20,
    ),
}


def load_eval_set(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Loaded {len(data)} evaluation samples from {path}")
    return data


def evaluate_mode(
    mode: str,
    samples: List[Dict],
    top_k: int = 10,
) -> Dict:
    runner = RETRIEVAL_MODES[mode]
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
            logger.error(f"[{mode}] Sample {sample.get('id', i)} failed: {e}")
            results = []
        elapsed = time.time() - start
        latencies.append(elapsed)

        hit = any(
            gt_context.lower()[:50] in r.get("text", "").lower()
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
        return {"error": "No samples with ground_truth_context"}

    avg_metrics = {}
    for key in all_metrics[0]:
        avg_metrics[key] = round(
            sum(m[key] for m in all_metrics) / n, 4
        )

    return {
        "mode": mode,
        "samples": n,
        "hit_rate": round(hit_count / n, 4) if n > 0 else 0.0,
        "avg_latency_s": round(float(np.mean(latencies)), 4) if latencies else 0.0,
        "p50_latency_s": round(float(np.median(latencies)), 4) if latencies else 0.0,
        **avg_metrics,
    }


def print_comparison_table(results: List[Dict]):
    print()
    print("=" * 90)
    print("  RETRIEVAL STRATEGY COMPARISON")
    print("=" * 90)

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
        ("P50 Latency (s)", "p50_latency_s"),
    ]

    header = f"{'Metric':<22}"
    for r in results:
        header += f"  {r['mode']:<12}"
    print(header)
    print("-" * len(header))

    for label, key in metrics_to_show:
        row = f"{label:<22}"
        for r in results:
            val = r.get(key, "N/A")
            if isinstance(val, float):
                row += f"  {val:<12.4f}"
            else:
                row += f"  {str(val):<12}"
        print(row)

    print("=" * 90)

    best_hybrid = True
    for r in results:
        if r["mode"] == "hybrid":
            for r2 in results:
                if r2["mode"] != "hybrid" and r.get("recall@10", 0) < r2.get("recall@10", 0):
                    best_hybrid = False

    if best_hybrid:
        print("  Hybrid (BM25 + Dense + RRF) shows best or tied performance.")
    else:
        print("  Note: Hybrid may not outperform on all metrics — inspect per-query.")

    print("=" * 90)
    print()


def main():
    parser = argparse.ArgumentParser(description="Compare retrieval strategies")
    parser.add_argument(
        "--eval-set", default=DEFAULT_EVAL_SET,
        help="Path to evaluation set JSON",
    )
    parser.add_argument(
        "--max-samples", type=int, default=0,
        help="Limit number of samples (0 = all)",
    )
    parser.add_argument(
        "--top-k", type=int, default=10,
        help="Top-K for evaluation (default: 10)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.eval_set):
        logger.error(f"Evaluation set not found: {args.eval_set}")
        sys.exit(1)

    samples = load_eval_set(args.eval_set)
    if args.max_samples > 0:
        samples = samples[:args.max_samples]
        logger.info(f"Limited to {args.max_samples} samples")

    results = []
    for mode in ["dense", "bm25", "hybrid"]:
        logger.info(f"Evaluating mode: {mode}")
        result = evaluate_mode(mode, samples, top_k=args.top_k)
        results.append(result)
        logger.info(f"  {mode}: Hit Rate={result.get('hit_rate', 'N/A')}, "
                     f"Recall@10={result.get('recall@10', 'N/A')}, "
                     f"Latency={result.get('avg_latency_s', 'N/A')}s")

    print_comparison_table(results)

    output_path = os.path.join(
        os.path.dirname(__file__), "retrieval_comparison.json"
    )
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
