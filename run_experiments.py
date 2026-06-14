#!/usr/bin/env python3
"""
run_experiments.py — Master Orchestrator for Specter 2.0 Evaluation.

Sequentially evaluates 4 pipeline configurations against the curated
evaluation set and produces:
  - evaluation/results_matrix.csv  (raw row-by-row dump)
  - evaluation/benchmark_report.txt (human-readable markdown table)

Usage:
    python run_experiments.py [--eval-set data/evaluation_set.json]
                              [--max-samples 50]
                              [--skip-config A]
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

# ChromaDB uses a relative path — change to backend/ so it finds chroma_db/
os.chdir(BACKEND_DIR)

# Default paths
DEFAULT_EVAL_SET = os.path.join(PROJECT_ROOT, "data", "evaluation_set.json")
RESULTS_CSV = os.path.join(PROJECT_ROOT, "evaluation", "results_matrix.csv")
REPORT_TXT = os.path.join(PROJECT_ROOT, "evaluation", "benchmark_report.txt")

# ── config descriptions ────────────────────────────────────────────────────

CONFIG_DESCRIPTIONS = {
    "A": "BM25 Baseline + Gemini Flash",
    "B": "Naive Chunk + Vector Search + Gemini Flash",
    "C": "Overlapping Chunker + Vector Search + Gemini Flash [Specter Current]",
    "D": "Overlapping Chunker + Multi-Turn Memory + Gemini Flash",
}

# ── pipeline runners ────────────────────────────────────────────────────────


def _wrap_error(result_dict: Dict, error_msg: str) -> Dict:
    result_dict["answer"] = f"[EVAL ERROR] {error_msg}"
    result_dict["error"] = error_msg
    return result_dict


def run_config_a(query: str) -> Dict:
    """Baseline: BM25 + Gemini Flash (no vector search)."""
    try:
        from baselines import retrieve_baseline
    except ImportError as e:
        return _wrap_error({"sources": [], "confidence": 0.0, "matched_chunks": []}, f"ImportError: {e}")

    retrieved = retrieve_baseline(query, top_k=5)
    context_block = "\n\n".join(
        f"[Source {i}] {r['text']}" for i, r in enumerate(retrieved, 1)
    ) if retrieved else "No context retrieved."

    answer = "[EVAL SKIP] No LLM API key configured."
    if _LLM_AVAILABLE:
        try:
            from local_llm import generate_with_context
            system_prompt = "You are SPECTER, an AI legal assistant. Answer based on the context provided."
            user_prompt = f"Context:\n{context_block}\n\nQuestion: {query}"
            answer = generate_with_context(system_prompt, user_prompt, temperature=0.2)
        except Exception as e:
            logger.warning(f"Config A LLM call failed: {e}")
            answer = f"[EVAL ERROR] LLM call failed: {e}"

    return {
        "answer": answer,
        "sources": [r["source"] for r in retrieved],
        "confidence": round(sum(r["score"] for r in retrieved) / len(retrieved), 3) if retrieved else 0.0,
        "matched_chunks": retrieved,
    }


def run_config_b(query: str) -> Dict:
    """Naive chunk split + vector search + Gemini Flash."""
    try:
        from embed_store import search_chunks
    except ImportError as e:
        return _wrap_error({"sources": [], "confidence": 0.0, "matched_chunks": []}, f"ImportError: {e}")

    chunks = search_chunks(query, top_k=5, namespace="global")

    answer = "[EVAL SKIP] No LLM API key configured."
    if _LLM_AVAILABLE:
        try:
            from local_llm import generate_with_context
            context_block = "\n\n".join(
                f"[Source {i}: score={c['score']:.3f}] {c['text']}" for i, c in enumerate(chunks, 1)
            ) if chunks else "No context retrieved."
            system_prompt = "You are SPECTER, an AI legal assistant. Answer based on the context provided."
            user_prompt = f"Context:\n{context_block}\n\nQuestion: {query}"
            answer = generate_with_context(system_prompt, user_prompt, temperature=0.2)
        except Exception as e:
            logger.warning(f"Config B LLM call failed: {e}")
            answer = f"[EVAL ERROR] LLM call failed: {e}"

    avg_conf = sum(c["score"] for c in chunks) / len(chunks) if chunks else 0
    return {
        "answer": answer,
        "sources": [c["source"] for c in chunks],
        "confidence": round(avg_conf, 3),
        "matched_chunks": chunks,
    }


def run_config_c(query: str) -> Dict:
    """Specter current production: overlapping chunker + vector search."""
    try:
        from chat_engine_rag import answer_query_with_rag
    except ImportError as e:
        return _wrap_error({"sources": [], "confidence": 0.0, "matched_chunks": []}, f"ImportError: {e}")

    # Synchronous call for evaluation simplicity
    result = answer_query_with_rag(query=query, user_id="eval_runner", namespace="global")
    if "error" in result:
        return result
    return result


async def run_config_d_async(query: str, history: List[Dict] = None) -> Dict:
    """Overlapping chunker + multi-turn memory + Gemini Flash."""
    try:
        from chat_engine_rag import answer_query_with_rag
    except ImportError as e:
        return _wrap_error({"sources": [], "confidence": 0.0, "matched_chunks": []}, f"ImportError: {e}")

    result = await answer_query_with_rag(
        query=query, user_id="eval_runner", chat_history=history or [], namespace="global",
    )
    return result


def run_config_d(query: str) -> Dict:
    """Synchronous entry point for config D."""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_config_d_async(query))
    finally:
        loop.close()


# ── runner map ─────────────────────────────────────────────────────────────

CONFIG_RUNNERS = {
    "A": run_config_a,
    "B": run_config_b,
    "C": run_config_c,
    "D": run_config_d,
}

# ── main evaluation loop ────────────────────────────────────────────────────


def load_eval_set(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Loaded {len(data)} evaluation samples from {path}")
    return data


def _check_llm_available() -> bool:
    """Check if a Google API key is available for LLM calls."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    return bool(api_key)


_LLM_AVAILABLE = _check_llm_available()


def run_single_sample(
    sample: Dict,
    configs: List[str],
) -> Dict:
    """
    Run all active configs on one sample and record results.
    """
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

            # For configs C & D which call the async RAG engine, handle missing API key gracefully
            if cfg in ("C", "D") and not _LLM_AVAILABLE:
                result = {
                    "answer": "[EVAL SKIP] No LLM API key configured. Cannot generate answer.",
                    "sources": [],
                    "confidence": 0.0,
                    "matched_chunks": [],
                    "skip_llm": True,
                }
            else:
                result = runner(query)

            elapsed = time.time() - start
        except Exception as e:
            logger.error(f"Config {cfg} failed for {sample['id']}: {e}")
            result = _wrap_error({}, str(e))
            elapsed = 0

        # Compute retrieval metrics
        from metrics import compute_all_retrieval_metrics

        retrieved = result.get("matched_chunks", [])
        ret_metrics = compute_all_retrieval_metrics(retrieved, gt_context)

        # Fill row
        prefix = f"config_{cfg}"
        row[f"{prefix}_answer"] = result.get("answer", "")[:500]
        row[f"{prefix}_confidence"] = result.get("confidence", 0.0)
        row[f"{prefix}_sources"] = "; ".join(result.get("sources", []))
        row[f"{prefix}_error"] = result.get("error", "")
        row[f"{prefix}_latency_s"] = round(elapsed, 2)

        for mk, mv in ret_metrics.items():
            row[f"{prefix}_{mk}"] = mv

        # LLM-as-a-Judge evaluation (skip if LLM unavailable or answer was skipped)
        if _LLM_AVAILABLE and not result.get("skip_llm"):
            try:
                from llm_judge import judge_answer
                judge_result = judge_answer(
                    query=query,
                    context=gt_context,
                    generated_answer=result.get("answer", ""),
                )
            except Exception as je:
                logger.warning(f"Judge call failed for {sample['id']} config {cfg}: {je}")
                judge_result = {"faithfulness": 0, "relevance": 0, "reasoning": "Judge call failed", "judge_success": False}
        else:
            judge_result = {"faithfulness": 0, "relevance": 0, "reasoning": "Skipped (no LLM)", "judge_success": False}

        row[f"{prefix}_faithfulness"] = judge_result.get("faithfulness", 0)
        row[f"{prefix}_relevance"] = judge_result.get("relevance", 0)
        row[f"{prefix}_judge_reasoning"] = judge_result.get("reasoning", "")
        row[f"{prefix}_judge_success"] = judge_result.get("judge_success", False)

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
        "--configs", type=str, default="A,B,C,D",
        help="Comma-separated configs to run (default: A,B,C,D)",
    )
    parser.add_argument(
        "--skip-health-check", action="store_true",
        help="Skip initial health check against the eval set file",
    )
    args = parser.parse_args()

    configs = [c.strip().upper() for c in args.configs.split(",") if c.strip()]
    for c in configs:
        assert c in CONFIG_RUNNERS, f"Unknown config: {c}. Valid: {list(CONFIG_RUNNERS.keys())}"

    logger.info("=" * 60)
    logger.info("Specter 2.0 — Evaluation Pipeline")
    logger.info("=" * 60)
    logger.info(f"Configs active: {', '.join(f'{c} ({CONFIG_DESCRIPTIONS[c]})' for c in configs)}")
    logger.info(f"Eval set: {args.eval_set}")

    # ── Load evaluation set ──────────────────────────────────────────────
    if not os.path.exists(args.eval_set):
        logger.error(f"Evaluation set not found at {args.eval_set}")
        logger.info("Run `python scripts/curate_eval_set.py` first.")
        sys.exit(1)

    samples = load_eval_set(args.eval_set)
    if args.max_samples > 0:
        samples = samples[: args.max_samples]
        logger.info(f"Limited to {args.max_samples} samples")

    # ── Ensure output directory ─────────────────────────────────────────
    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)

    # ── Run evaluation ───────────────────────────────────────────────────
    results = []

    pbar = tqdm.tqdm(samples, desc="Evaluating", unit="sample")
    for sample in pbar:
        logger.info(f"Processing {sample['id']}: {sample['query'][:80]}...")
        row = run_single_sample(sample, configs)
        results.append(row)

        # Log progress summary for this sample
        faithfulness_scores = {cfg: row.get(f"config_{cfg}_faithfulness", "?") for cfg in configs}
        relevance_scores = {cfg: row.get(f"config_{cfg}_relevance", "?") for cfg in configs}
        pbar.set_postfix(
            {f"F{c}": faithfulness_scores[c] for c in configs},
            {f"R{c}": relevance_scores[c] for c in configs},
        )

    # ── Write CSV ────────────────────────────────────────────────────────
    if not results:
        logger.error("No results collected. Aborting.")
        sys.exit(1)

    fieldnames = list(results[0].keys())
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    logger.info(f"Results matrix written to {RESULTS_CSV} ({len(results)} rows)")

    # ── Gather corpus stats for report ──────────────────────────────────
    corpus_bm25 = "N/A"
    corpus_vector = "N/A"
    try:
        from baselines import get_bm25_index, _CORPUS
        _ = get_bm25_index()  # ensure built
        corpus_bm25 = len(_CORPUS)
    except Exception:
        pass
    try:
        from embed_store import _get_collection
        col = _get_collection()
        corpus_vector = col.count()
    except Exception:
        pass

    # ── Generate benchmark report ────────────────────────────────────────
    generate_report(results, configs, corpus_bm25, corpus_vector)

    logger.info("=" * 60)
    logger.info("Evaluation complete!")
    logger.info(f"  CSV : {RESULTS_CSV}")
    logger.info(f"  Report : {REPORT_TXT}")
    logger.info("=" * 60)


def generate_report(results: List[Dict], configs: List[str],
                    corpus_bm25: object = "N/A", corpus_vector: object = "N/A"):
    """Aggregate scores across configs and write a human-readable markdown report."""

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

    # ── Retrieval metrics table ──────────────────────────────────────────
    lines.append("## Retrieval Performance (Mean)")
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

    # ── LLM-as-a-Judge metrics table ─────────────────────────────────────
    lines.append("## LLM-as-a-Judge Scores (Mean)")
    lines.append("")
    judge_keys = ["faithfulness", "relevance"]

    header2 = "| Dimension | " + " | ".join(f"Config {c}" for c in configs) + " |"
    sep2 = "|-----------|" + "|".join("--------:" for _ in configs) + "|"
    lines.append(header2)
    lines.append(sep2)

    for jk in judge_keys:
        row_vals = []
        for c in configs:
            val = avg(f"config_{c}_{jk}")
            row_vals.append(f"{val:.2f} / 5.00")
        lines.append(f"| **{jk.title()}** | " + " | ".join(row_vals) + " |")

    lines.append("")

    # ── Confidence / Latency ─────────────────────────────────────────────
    lines.append("## Additional Metrics (Mean)")
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

    # ── Judge success rate ───────────────────────────────────────────────
    lines.append("## Judge Success Rate")
    lines.append("")
    for c in configs:
        key = f"config_{c}_judge_success"
        success_count = sum(1 for r in results if r.get(key) is True)
        rate = success_count / len(results) * 100 if results else 0
        lines.append(f"- **Config {c}**: {success_count}/{len(results)} ({rate:.1f}%)")
    lines.append("")

    # ── Footer ──────────────────────────────────────────────────────────
    lines.append("---")
    lines.append("*Report auto-generated by `run_experiments.py`*")

    report = "\n".join(lines)
    with open(REPORT_TXT, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info(f"Benchmark report written to {REPORT_TXT}")


if __name__ == "__main__":
    main()
