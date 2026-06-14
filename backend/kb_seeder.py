import json
import logging
from pathlib import Path
from doc_parser import parse_and_chunk
from embed_store import add_chunks_to_db, _get_collection

logger = logging.getLogger(__name__)

SEED_FILES = [
    ("../data/processed/kb_seed.jsonl", "kb_seed"),
    ("./optimized_legal_train.jsonl", "optimized_train"),
]


def seed_kb_if_empty():
    collection = _get_collection()
    count = collection.count()
    if count > 0:
        logger.info(f"ChromaDB already has {count} chunks. Skipping seed.")
        return

    logger.info("ChromaDB is empty. Seeding legal knowledge base...")
    total = 0

    for file_path, source_label in SEED_FILES:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Seed file not found: {file_path}")
            continue

        with open(path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                answer_text = ""
                record_id = record.get("id") or f"{source_label}_{idx}"
                source_name = record.get("title") or record.get("domain") or record_id

                if record.get("chunk_text"):
                    answer_text = record["chunk_text"]
                elif record.get("text_summary"):
                    answer_text = record["text_summary"]
                elif record.get("response"):
                    answer_text = record["response"]
                elif "answer" in record:
                    answer_text = record["answer"]
                elif "messages" in record:
                    for msg in record["messages"]:
                        if msg.get("role") == "assistant":
                            answer_text += msg.get("content", "") + " "
                elif "output" in record:
                    answer_text = record["output"]

                if not answer_text.strip():
                    continue

                chunks = parse_and_chunk(answer_text)
                added = add_chunks_to_db(chunks, source=source_name, namespace="global")
                total += added
                if added > 0 and source_label == "kb_seed":
                    logger.info(f"  Added {added} chunks from '{source_name}'")

                if idx % 100 == 0 and idx > 0:
                    logger.info(f"  Processed {idx} records from {source_label}...")

    logger.info(f"Seeding complete. Added {total} chunks to ChromaDB.")
