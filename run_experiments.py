#!/usr/bin/env python3
"""
run_experiments.py — Evaluation Pipeline for Specter 2.0.

Evaluates the retrieval-only pipeline against the curated evaluation set
and produces:
  - evaluation/results_matrix.csv  (raw row-by-row dump)
  - evaluation/benchmark_report.txt (human-readable markdown table)

Usage:
    python run_experiments.py [--eval-set data/evaluation_set.json]
                              [--max-samples 50]
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("evaluation", "experiments.log"), mode="w"),
    ],
)
logger = logging.getLogger("run_experiments")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "evaluation"))

os.chdir(BACKEND_DIR)

DEFAULT_EVAL_SET = os.path.join(PROJECT_ROOT, "data", "evaluation_set.json")
RESULTS_CSV = os.path.join(PROJECT_ROOT, "evaluation", "results_matrix.csv")
REPORT_TXT = os.path.join(PROJECT_ROOT, "evaluation", "benchmark_report.txt")

CONFIG_DESCRIPTIONS = {
    "C": "Retrieval-Only: Vector Search + Situation-Aware Templates [Specter Current]",
}

CONFIG_RUNNERS = {
    "C": None,
}


def run_retrieval_only(query: str) -> Dict:
    """Current production pipeline: vector search + retrieval-only response."""
    try:
        from chat_engine_rag import answer_query_with_rag
    except ImportError as e:
        return {"answer": "", "sources": [], "confidence": 0.0, "matched_chunks": [],
                "error": f"ImportError: {e}"}

    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            answer_query_with_rag(query=query, user_id="eval_runner", namespace="global")
        )
        return result
    finally:
        loop.close()


CONFIG_RUNNERS["C"] = run_retrieval_only


def load_eval_set(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Loaded {len(data)} evaluation samples from {path}")
    return data


def run_single_sample(
    sample: Dict,
    configs: List[str],
) -> Dict:
    query = sample["query"]
    gt_context = sample.get("ground_truth_context", "")
    gt_answer = sample.get("ground_truth_answer", "")

    row = {
        "eval_id": sample["id"],
        "query": query[:200],
        "ground_truth_context": gt_context[:300],
        "ground_truth_answer": gt_answer[:300],
        "language": sample.get("language", "en"),
    }

    for cfg in configs:
        runner = CONFIG_RUNNERS.get(cfg)
        if not runner:
            continue

        try:
            start = time.time()
            result = runner(query)
            elapsed = time.time() - start
        except Exception as e:
            logger.error(f"Config {cfg} failed for {sample['id']}: {e}")
            result = {"answer": "", "sources": [], "confidence": 0.0, "matched_chunks": [],
                      "error": str(e)}
            elapsed = 0

        from metrics import compute_all_retrieval_metrics

        retrieved = result.get("matched_chunks", [])
        ret_metrics = compute_all_retrieval_metrics(retrieved, gt_context)

        prefix = f"config_{cfg}"
        row[f"{prefix}_answer"] = result.get("answer", "")[:500]
        row[f"{prefix}_confidence"] = result.get("confidence", 0.0)
        row[f"{prefix}_sources"] = "; ".join(result.get("sources", []))
        row[f"{prefix}_error"] = result.get("error", "")
        row[f"{prefix}_latency_s"] = round(elapsed, 2)

        for mk, mv in ret_metrics.items():
            row[f"{prefix}_{mk}"] = mv

    return row


def main():
    parser = argparse.ArgumentParser(description="Specter 2.0 Evaluation Pipeline")
    parser.add_argument(
        "--eval-set",
        default=DEFAULT_EVAL_SET,
        help=f"Path to evaluation set JSON (default: {DEFAULT_EVAL_SET})",
    )
    parser.add_argument(
        "--max-samples", type=int, default=0,
        help="Limit number of samples (0 = all)",
    )
    parser.add_argument(
        "--skip-health-check", action="store_true",
        help="Skip initial health check against the eval set file",
    )
    args = parser.parse_args()

    configs = ["C"]

    logger.info("=" * 60)
    logger.info("Specter 2.0 — Evaluation Pipeline (Retrieval-Only)")
    logger.info("=" * 60)
    logger.info(f"Configs active: {', '.join(f'{c} ({CONFIG_DESCRIPTIONS[c]})' for c in configs)}")
    logger.info(f"Eval set: {args.eval_set}")

    if not os.path.exists(args.eval_set):
        logger.error(f"Evaluation set not found at {args.eval_set}")
        logger.info("Run `python scripts/curate_eval_set.py` first.")
        sys.exit(1)

    samples = load_eval_set(args.eval_set)
    if args.max_samples > 0:
        samples = samples[: args.max_samples]
        logger.info(f"Limited to {args.max_samples} samples")

    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)

    results = []

    pbar = tqdm.tqdm(samples, desc="Evaluating", unit="sample")
    for sample in pbar:
        logger.info(f"Processing {sample['id']}: {sample['query'][:80]}...")
        row = run_single_sample(sample, configs)
        results.append(row)

        pbar.set_postfix({"conf": row.get("config_C_confidence", "?")})

    if not results:
        logger.error("No results collected. Aborting.")
        sys.exit(1)

    fieldnames = list(results[0].keys())
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    logger.info(f"Results matrix written to {RESULTS_CSV} ({len(results)} rows)")

    corpus_bm25 = "N/A"
    corpus_vector = "N/A"
    try:
        from baselines import get_bm25_index, _CORPUS
        _ = get_bm25_index()
        corpus_bm25 = len(_CORPUS)
    except Exception:
        pass
    try:
        from embed_store import _get_collection
        col = _get_collection()
        corpus_vector = col.count()
    except Exception:
        pass

    generate_report(results, configs, corpus_bm25, corpus_vector)

    logger.info("=" * 60)
    logger.info("Evaluation complete!")
    logger.info(f"  CSV : {RESULTS_CSV}")
    logger.info(f"  Report : {REPORT_TXT}")
    logger.info("=" * 60)


def generate_report(results: List[Dict], configs: List[str],
                    corpus_bm25: object = "N/A", corpus_vector: object = "N/A"):
    def avg(key: str) -> float:
        vals = [r.get(key, 0) for r in results if isinstance(r.get(key), (int, float))]
        return sum(vals) / len(vals) if vals else 0.0

    lines = []
    lines.append("# Specter 2.0 — Benchmark Report")
    lines.append("")
    lines.append(f"*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*")
    lines.append(f"*Total evaluation samples: {len(results)}*")
    lines.append(f"*Corpus size (BM25 / Vector DB): {corpus_bm25} / {corpus_vector} chunks*")
    lines.append("")
    lines.append("## Configuration Key")
    lines.append("")
    for c in configs:
        lines.append(f"- **Config {c}**: {CONFIG_DESCRIPTIONS[c]}")
    lines.append("")

    metrics_keys = ["precision@1", "precision@3", "precision@5",
                    "recall@1", "recall@3", "recall@5",
                    "mrr", "ndcg@5"]

    header = "| Metric | " + " | ".join(f"Config {c}" for c in configs) + " |"
    sep = "|--------|" + "|".join("--------:" for _ in configs) + "|"
    lines.append(header)
    lines.append(sep)

    for mk in metrics_keys:
        row_vals = []
        for c in configs:
            val = avg(f"config_{c}_{mk}")
            row_vals.append(f"{val:.4f}")
        lines.append(f"| **{mk}** | " + " | ".join(row_vals) + " |")

    lines.append("")

    extra_keys = ["confidence", "latency_s"]
    header3 = "| Metric | " + " | ".join(f"Config {c}" for c in configs) + " |"
    sep3 = "|--------|" + "|".join("--------:" for _ in configs) + "|"
    lines.append(header3)
    lines.append(sep3)

    for ek in extra_keys:
        row_vals = []
        for c in configs:
            val = avg(f"config_{c}_{ek}")
            if ek == "latency_s":
                row_vals.append(f"{val:.2f}s")
            else:
                row_vals.append(f"{val:.4f}")
        lines.append(f"| **{ek}** | " + " | ".join(row_vals) + " |")

    lines.append("")
    lines.append("---")
    lines.append("*Report auto-generated by `run_experiments.py`*")

    report = "\n".join(lines)
    with open(REPORT_TXT, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info(f"Benchmark report written to {REPORT_TXT}")


if __name__ == "__main__":
    main()
