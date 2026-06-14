"""
Script: curate_eval_set.py
Purpose: Parse existing training/knowledge files and produce a balanced
         evaluation set (100–200 samples) with ground-truth context and answers.

Output: data/evaluation_set.json
"""

import json
import logging
import os
import random
import re
import sys
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("curate_eval_set")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
EVAL_OUTPUT = os.path.join(PROJECT_ROOT, "data", "evaluation_set.json")

# Seed for reproducibility
random.seed(42)

# ── helpers ─────────────────────────────────────────────────────────────────


def load_jsonl(path: str) -> List[Dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    logger.info(f"Loaded {len(rows)} rows from {path}")
    return rows


def detect_language(text: str) -> str:
    """Rough heuristic: if text contains Devanagari/Tamil/Telugu/etc, label as that language."""
    scripts = {
        "hi": re.compile(r"[\u0900-\u097F]"),
        "ta": re.compile(r"[\u0B80-\u0BFF]"),
        "te": re.compile(r"[\u0C00-\u0C7F]"),
        "kn": re.compile(r"[\u0C80-\u0CFF]"),
        "ml": re.compile(r"[\u0D00-\u0D7F]"),
        "bn": re.compile(r"[\u0980-\u09FF]"),
        "mr": re.compile(r"[\u0900-\u097F]"),
        "gu": re.compile(r"[\u0A80-\u0AFF]"),
    }
    for lang, pattern in scripts.items():
        if pattern.search(text):
            return lang
    return "en"


def extract_ground_truth_context(
    row: Dict, source_label: str = "statute"
) -> str:
    """Try to build a context string from whatever fields are available."""
    parts = []
    for key in ("text_summary", "chunk_text", "definition", "ingredients",
                 "exceptions", "punishment", "response", "text"):
        val = row.get(key)
        if val:
            if isinstance(val, list):
                val = "; ".join(str(v) for v in val)
            parts.append(str(val))
    if parts:
        return " | ".join(parts)
    return ""


# ── samplers ────────────────────────────────────────────────────────────────


def sample_from_optimized(path: str, n: int = 60) -> List[Dict]:
    rows = load_jsonl(path)
    random.shuffle(rows)
    samples = []
    for row in rows:
        if len(samples) >= n:
            break
        prompt = row.get("prompt", "").strip()
        response = row.get("response", "").strip()
        if not prompt or not response:
            continue
        # Extract the actual question from the prompt
        q_match = re.search(r"Question:\s*(.+)", prompt, re.IGNORECASE)
        query = q_match.group(1).strip() if q_match else prompt[:300]
        samples.append({
            "id": f"eval_opt_{len(samples)+1:03d}",
            "query": query,
            "ground_truth_context": response,
            "ground_truth_answer": response,
            "language": detect_language(query + response),
            "source": "optimized_legal_train",
        })
    logger.info(f"Sampled {len(samples)} from optimized_legal_train")
    return samples


def sample_from_indic(path: str, n: int = 60) -> List[Dict]:
    rows = load_jsonl(path)
    random.shuffle(rows)
    samples = []
    seen_queries = set()
    for row in rows:
        if len(samples) >= n:
            break
        prompt = row.get("prompt", "").strip()
        response = row.get("response", "").strip()
        if not prompt or not response:
            continue
        q_match = re.search(r"Question:\s*(.+)", prompt, re.IGNORECASE)
        query = q_match.group(1).strip() if q_match else prompt[:300]
        # Deduplicate
        q_normalised = query.lower().strip()[:80]
        if q_normalised in seen_queries:
            continue
        seen_queries.add(q_normalised)
        samples.append({
            "id": f"eval_indic_{len(samples)+1:03d}",
            "query": query,
            "ground_truth_context": response,
            "ground_truth_answer": response,
            "language": detect_language(query + response),
            "source": "indic_legal_qa_train",
        })
    logger.info(f"Sampled {len(samples)} from indic_legal_qa_train")
    return samples


def sample_from_kb_seed(path: str, n: int = 20) -> List[Dict]:
    rows = load_jsonl(path)
    samples = []
    # Generate synthetic queries for each kb row
    kb_questions = [
        "What is the punishment for murder under Indian law?",
        "When does culpable homicide amount to murder?",
        "What is the definition of murder under the Bharatiya Nyaya Sanhita?",
        "What are the exceptions to murder under Section 101 BNS?",
        "What is the procedure for filing an FIR?",
        "What are the ingredients of murder under Section 101 BNS?",
        "Is murder a bailable offence?",
        "What court tries murder cases in India?",
        "What constitutes grave and sudden provocation?",
        "What is the difference between culpable homicide and murder?",
        "What are the leading cases on murder in India?",
        "What is the punishment for theft under BNS?",
        "What is a cognizable offence?",
        "What is the procedure for bail in non-bailable offences?",
        "What are the rights of an accused under Indian law?",
        "What is the burden of proof in criminal cases?",
        "What is the definition of rape under Indian law?",
        "What is the punishment for dowry death?",
        "What constitutes criminal breach of trust?",
        "How is abetment defined under IPC?",
    ]
    random.shuffle(kb_questions)
    for row in rows:
        if len(samples) >= n:
            break
        context = extract_ground_truth_context(row)
        if not context:
            continue
        query = kb_questions.pop(0) if kb_questions else f"What does {row.get('title', 'this section')} say?"
        samples.append({
            "id": f"eval_kb_{len(samples)+1:03d}",
            "query": query,
            "ground_truth_context": context,
            "ground_truth_answer": context[:500],
            "language": "en",
            "source": "kb_seed",
        })
    logger.info(f"Sampled {len(samples)} from kb_seed")
    return samples


def sample_from_seed_notes(path: str, n: int = 15) -> List[Dict]:
    rows = load_jsonl(path)
    random.shuffle(rows)
    samples = []
    for row in rows:
        if len(samples) >= n:
            break
        text = row.get("text_summary", row.get("chunk_text", row.get("text", "")))
        if not text or len(text) < 30:
            continue
        title = row.get("title", "")
        query = f"What is the legal position regarding {title.lower() if title else 'this provision'}?"
        samples.append({
            "id": f"eval_seed_{len(samples)+1:03d}",
            "query": query,
            "ground_truth_context": text,
            "ground_truth_answer": text[:500],
            "language": detect_language(text),
            "source": "seed_notes",
        })
    logger.info(f"Sampled {len(samples)} from seed_notes")
    return samples


def sample_from_legal_training(path: str, n: int = 15) -> List[Dict]:
    rows = load_jsonl(path)
    random.shuffle(rows)
    samples = []
    for row in rows:
        if len(samples) >= n:
            break
        text = row.get("text", "").strip()
        if not text or len(text) < 50:
            continue
        source = row.get("source", "legal_training")
        query = f"What does the {source} say about {row.get('type', 'constitutional provisions')}?"
        samples.append({
            "id": f"eval_legal_{len(samples)+1:03d}",
            "query": query,
            "ground_truth_context": text[:1000],
            "ground_truth_answer": text[:500],
            "language": detect_language(text),
            "source": source,
        })
    logger.info(f"Sampled {len(samples)} from legal_training_data")
    return samples


# ── main ────────────────────────────────────────────────────────────────────


def main():
    logger.info("=" * 60)
    logger.info("Starting evaluation set curation")
    logger.info("=" * 60)

    backend_dir = os.path.join(PROJECT_ROOT, "backend")
    data_processed = os.path.join(DATA_DIR, "processed")
    data_raw = os.path.join(DATA_DIR, "raw_laws")

    all_samples = []

    # 1. Optimized legal train (60 samples)
    opt_path = os.path.join(backend_dir, "optimized_legal_train.jsonl")
    if os.path.exists(opt_path):
        all_samples.extend(sample_from_optimized(opt_path, n=60))
    else:
        logger.warning(f"File not found: {opt_path}")

    # 2. Indic legal QA train (60 samples)
    indic_path = os.path.join(backend_dir, "indic_legal_qa_train.jsonl")
    if os.path.exists(indic_path):
        all_samples.extend(sample_from_indic(indic_path, n=60))
    else:
        logger.warning(f"File not found: {indic_path}")

    # 3. KB seed (20 samples)
    kb_path = os.path.join(data_processed, "kb_seed.jsonl")
    if os.path.exists(kb_path):
        all_samples.extend(sample_from_kb_seed(kb_path, n=20))
    else:
        logger.warning(f"File not found: {kb_path}")

    # 4. Seed notes (15 samples)
    seed_path = os.path.join(data_raw, "seed_notes.jsonl")
    if os.path.exists(seed_path):
        all_samples.extend(sample_from_seed_notes(seed_path, n=15))
    else:
        logger.warning(f"File not found: {seed_path}")

    # 5. Legal training data (15 samples)
    legal_path = os.path.join(data_processed, "legal_training_data.jsonl")
    if os.path.exists(legal_path):
        all_samples.extend(sample_from_legal_training(legal_path, n=15))
    else:
        logger.warning(f"File not found: {legal_path}")

    random.shuffle(all_samples)
    total = len(all_samples)

    # Assign final eval IDs sequentially
    for i, s in enumerate(all_samples):
        s["id"] = f"eval_{i+1:03d}"

    lang_dist = {}
    for s in all_samples:
        lang_dist[s["language"]] = lang_dist.get(s["language"], 0) + 1

    logger.info(f"Total evaluation samples: {total}")
    logger.info(f"Language distribution: {lang_dist}")

    # Write output
    os.makedirs(os.path.dirname(EVAL_OUTPUT), exist_ok=True)
    with open(EVAL_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(all_samples, f, indent=2, ensure_ascii=False)
    logger.info(f"Written to {EVAL_OUTPUT}")

    # Quick summary
    print(f"\n{'='*60}")
    print(f"  Evaluation Set Summary")
    print(f"{'='*60}")
    print(f"  Total samples : {total}")
    print(f"  Languages     : {lang_dist}")
    print(f"  Output        : {EVAL_OUTPUT}")
    print(f"{'='*60}\n")

    return all_samples


if __name__ == "__main__":
    main()
