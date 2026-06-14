"""
Re-index all training data into ChromaDB.
Batches entire files for efficient encoding.
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger("reindex")

from doc_parser import parse_and_chunk
from embed_store import add_chunks_to_db, _get_collection

BASE = Path(__file__).resolve().parent.parent
BACKEND = BASE / "backend"
DATA_PROC = BASE / "data" / "processed"

DATA_FILES = [
    (BACKEND / "optimized_legal_train.jsonl", "optimized_train"),
    (BACKEND / "indic_legal_qa_train.jsonl", "indic_qa"),
    (DATA_PROC / "kb_seed.jsonl", "kb_seed"),
    (DATA_PROC / "legal_training_data.jsonl", "legal_train"),
    (DATA_PROC / "faq_training_data.jsonl", "faq"),
    (DATA_PROC / "meera_legal_qa.jsonl", "meera_qa"),
    (DATA_PROC / "indian_laws_training.jsonl", "indian_laws"),
]

SKIP_PATTERNS = {"seed_notes.jsonl"}
NAMESPACE = "global"


def process_file_batched(filepath: Path, source_label: str) -> int:
    if not filepath.exists():
        logger.warning(f"File not found: {filepath}")
        return 0

    if filepath.name in SKIP_PATTERNS:
        logger.info(f"Skipping {filepath.name}")
        return 0

    all_chunks = []
    with open(filepath, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            answer_text = ""
            if record.get("chunk_text"):
                answer_text = record["chunk_text"]
            elif record.get("text_summary"):
                answer_text = record["text_summary"]
            elif record.get("response"):
                answer_text = record["response"]
            elif record.get("answer"):
                answer_text = record["answer"]
            elif record.get("law"):
                answer_text = record["law"]
            elif "messages" in record:
                for msg in record["messages"]:
                    if msg.get("role") == "assistant":
                        answer_text += msg.get("content", "") + " "
            elif record.get("output"):
                answer_text = record["output"]

            if not answer_text or not answer_text.strip():
                continue

            chunks = parse_and_chunk(answer_text)
            all_chunks.extend(chunks)

    if not all_chunks:
        logger.info(f"  {source_label}: no chunks extracted")
        return 0

    logger.info(f"  {source_label}: {len(all_chunks)} chunks to encode & add...")
    added = add_chunks_to_db(all_chunks, source=source_label, namespace=NAMESPACE)
    logger.info(f"  {source_label}: added {added} chunks")
    return added


def main():
    logger.info("=== Re-indexing all training data ===")

    collection = _get_collection()
    before = collection.count()
    logger.info(f"Current collection size: {before}")

    logger.info(f"Deleting all existing data...")
    all_ids = collection.get()['ids']
    if all_ids:
        collection.delete(ids=all_ids)
    after_delete = collection.count()
    logger.info(f"After delete: {after_delete}")

    grand_total = 0
    for filepath, source_label in DATA_FILES:
        logger.info(f"Processing {filepath.name} ({source_label})...")
        added = process_file_batched(filepath, source_label)
        grand_total += added

    final = collection.count()
    logger.info(f"\n=== Complete ===")
    logger.info(f"Total chunks added: {grand_total}")
    logger.info(f"Final collection size: {final}")


if __name__ == "__main__":
    main()
