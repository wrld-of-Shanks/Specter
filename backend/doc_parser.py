import re
from typing import List

def parse_and_chunk(text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
    if not text or not text.strip():
        return []

    text = re.sub(r'\s+', ' ', text).strip()

    sentences = re.split(r'(?<=[.?!])\s+(?=[A-Z\u0900-\u097F])', text)

    chunks = []
    current_words = []
    current_count = 0

    for sentence in sentences:
        words = sentence.split()
        if current_count + len(words) > chunk_size and current_words:
            chunks.append(' '.join(current_words))
            current_words = current_words[-overlap:] if overlap else []
            current_count = len(current_words)
        current_words.extend(words)
        current_count += len(words)

    if current_words:
        chunks.append(' '.join(current_words))

    return [c for c in chunks if len(c.strip()) > 30]
