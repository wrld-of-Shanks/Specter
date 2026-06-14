"""
Expand Specter training data to 50k+ records by:
1. Converting comprehensive_legal_faq.txt → JSONL
2. Downloading MeeraR/legal-qa-dataset from Hugging Face
3. Downloading mratanusarkar/Indian-Laws from Hugging Face
4. Converting the Indian Constitution PDF to training data
5. Saving all to data/processed/ for re-indexing
"""

import json
import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA_RAW = BASE / "data" / "raw_laws"
DATA_PROCESSED = BASE / "data" / "processed"
BACKEND = BASE / "backend"

SYSTEM_PROMPT = "You are an AI legal assistant for Indian law. Answer questions accurately and concisely based on the provided information."


def save_jsonl(records: list, filename: str):
    path = DATA_PROCESSED / filename
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  Wrote {len(records)} records to {path}")


def convert_faq_to_jsonl() -> list:
    """Parse comprehensive_legal_faq.txt into JSONL format"""
    path = DATA_RAW / "comprehensive_legal_faq.txt"
    if not path.exists():
        print("  FAQ file not found, skipping.")
        return []

    records = []
    current_q = None
    current_a = []

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("Q:") or line.startswith("Q "):
            if current_q and current_a:
                records.append({
                    "prompt": f"Question: {current_q}",
                    "response": " ".join(current_a).strip(),
                    "system": SYSTEM_PROMPT,
                })
            current_q = line.split(":", 1)[1].strip() if ":" in line else ""
            current_a = []
        elif line.startswith("A:") or line.startswith("A "):
            ans = line.split(":", 1)[1].strip() if ":" in line else ""
            current_a.append(ans)
        elif current_a:
            current_a.append(line)

    if current_q and current_a:
        records.append({
            "prompt": f"Question: {current_q}",
            "response": " ".join(current_a).strip(),
            "system": SYSTEM_PROMPT,
        })

    print(f"  Converted {len(records)} FAQ entries")
    return records


def download_meera_qa() -> list:
    """Download MeeraR/legal-qa-dataset from Hugging Face"""
    try:
        from datasets import load_dataset
    except ImportError:
        print("  datasets library not installed, skipping MeeraR.")
        return []

    try:
        ds = load_dataset("MeeraR/legal-qa-dataset", split="train", trust_remote_code=True)
        print(f"  Loaded MeeraR dataset: {len(ds)} rows")
    except Exception as e:
        print(f"  Failed to load MeeraR dataset: {e}")
        return []

    records = []
    skipped = 0
    for item in ds:
        q = (item.get("question") or "").strip()
        a = (item.get("answer") or "").strip()
        if not q or not a:
            skipped += 1
            continue
        if len(a) < 5:
            skipped += 1
            continue
        records.append({
            "prompt": f"Question: {q}",
            "response": a,
            "system": SYSTEM_PROMPT,
        })
    print(f"  MeeraR: {len(records)} usable, {skipped} skipped (empty/questionable)")
    return records


def download_mratan_indian_laws() -> list:
    """Download mratanusarkar/Indian-Laws from Hugging Face"""
    try:
        from datasets import load_dataset
    except ImportError:
        print("  datasets library not installed, skipping Indian-Laws.")
        return []

    try:
        ds = load_dataset("mratanusarkar/Indian-Laws", split="train", trust_remote_code=True)
        print(f"  Loaded Indian-Laws dataset: {len(ds)} rows")
    except Exception as e:
        print(f"  Failed to load Indian-Laws dataset: {e}")
        return []

    records = []
    for item in ds:
        act = (item.get("act_title") or "").strip()
        section = str(item.get("section") or "").strip()
        law = (item.get("law") or "").strip()
        if not law:
            continue

        q_prompt = f"Question: What does Section {section} of the {act} say?" if section and act else f"Question: What does {act} contain?"
        answer_text = law[:2000] if len(law) > 2000 else law
        records.append({
            "prompt": q_prompt,
            "response": answer_text,
            "system": SYSTEM_PROMPT,
        })
    print(f"  Indian-Laws: {len(records)} usable")
    return records


def download_prarabdha_dataset() -> list:
    """Download Prarabdha/indian-legal-supervised-fine-tuning-data from Hugging Face"""
    try:
        from datasets import load_dataset
    except ImportError:
        print("  datasets library not installed, skipping Prarabdha.")
        return []

    try:
        ds = load_dataset("Prarabdha/indian-legal-supervised-fine-tuning-data", split="train", trust_remote_code=True)
        print(f"  Loaded Prarabdha dataset: {len(ds)} rows")
    except Exception as e:
        print(f"  Failed to load Prarabdha dataset: {e}")
        return []

    records = []
    for item in ds:
        q = (item.get("question") or "").strip()
        r = (item.get("response") or "").strip()
        if not q or not r:
            continue
        records.append({
            "prompt": q,
            "response": r,
            "system": SYSTEM_PROMPT,
        })
    print(f"  Prarabdha: {len(records)} usable")
    return records


def main():
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    print("=== Step 1: Converting FAQ to JSONL ===")
    faq_records = convert_faq_to_jsonl()
    if faq_records:
        save_jsonl(faq_records, "faq_training_data.jsonl")

    print("\n=== Step 2: Downloading MeeraR QA dataset ===")
    meera_records = download_meera_qa()
    if meera_records:
        save_jsonl(meera_records, "meera_legal_qa.jsonl")

    print("\n=== Step 3: Downloading Indian Laws dataset ===")
    laws_records = download_mratan_indian_laws()
    if laws_records:
        save_jsonl(laws_records, "indian_laws_training.jsonl")

    print("\n=== Step 4: Downloading Prarabdha dataset ===")
    prarabdha_records = download_prarabdha_dataset()
    if prarabdha_records:
        save_jsonl(prarabdha_records, "prarabdha_legal_qa.jsonl")

    total_new = len(faq_records) + len(meera_records) + len(laws_records) + len(prarabdha_records)
    print(f"\n=== Summary ===")
    print(f"  FAQ:           {len(faq_records)}")
    print(f"  MeeraR:        {len(meera_records)}")
    print(f"  Indian Laws:   {len(laws_records)}")
    print(f"  Prarabdha:     {len(prarabdha_records)}")
    print(f"  Total new:     {total_new}")

    existing = 23157
    print(f"  Existing:      {existing}")
    print(f"  Grand total:   {existing + total_new}")
    print(f"\n  Files saved to: {DATA_PROCESSED}/")


if __name__ == "__main__":
    main()
