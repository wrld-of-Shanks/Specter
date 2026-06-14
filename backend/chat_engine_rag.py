"""
Specter 2.0 — Semantic RAG Chat Engine
Async version with Redis cache support.
Uses ChromaDB vector search + Gemini for answer generation.
"""

import logging
from typing import Dict, List, Optional

from embed_store import search_chunks
from local_llm import generate_with_context
from cache_service import get_cached_answer, set_cached_answer

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.45
MAX_CONTEXT_CHUNKS = 4
MAX_HISTORY_TURNS = 6


SYSTEM_PROMPT = """You are SPECTER, an AI legal assistant specialized in Indian law.
You help ordinary Indian citizens understand their legal rights and obligations.

Rules you must follow:
1. Answer ONLY based on the provided legal context and your knowledge of Indian statutes.
2. If the context does not contain enough information, say so clearly — do not hallucinate.
3. Always cite the specific law, section, or act when you reference it (e.g. "Section 498A IPC", "Section 9 of The Hindu Marriage Act 1955").
4. Use simple, plain English. Avoid legal jargon unless you immediately explain it.
5. If the user's question implies an emergency (arrest, domestic violence, eviction), lead with the most urgent actionable advice.
6. Never provide advice that requires a licensed advocate — always recommend consulting one for serious matters.
7. Keep answers concise: under 300 words unless the question requires more detail."""


def build_rag_prompt(
    query: str,
    context_chunks: List[Dict],
    chat_history: Optional[List[Dict]] = None
) -> List[Dict]:
    if context_chunks:
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['source']} | confidence {chunk['score']:.0%}]\n{chunk['text']}"
            )
        context_block = "\n\n---\n\n".join(context_parts)
    else:
        context_block = "No specific legal context retrieved. Answer from general Indian law knowledge."

    user_message = (
        f"Legal context retrieved:\n\n{context_block}\n\n"
        f"---\n\nUser question: {query}"
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if chat_history:
        messages.extend(chat_history[-MAX_HISTORY_TURNS:])

    messages.append({"role": "user", "content": user_message})
    return messages


async def answer_query_with_rag(
    query: str,
    user_id: str = None,
    chat_history: Optional[List[Dict]] = None,
    namespace: str = "global",
    mode: str = "default"
) -> Dict:
    try:
        logger.info(f"[RAG] Processing query for user={user_id}: {query[:80]}")

        cached = await get_cached_answer(query, namespace)
        if cached:
            logger.info(f"[RAG] Cache hit for query in namespace '{namespace}'")
            return cached

        chunks = search_chunks(query, top_k=MAX_CONTEXT_CHUNKS, namespace=namespace)

        confident_chunks = [c for c in chunks if c["score"] >= SIMILARITY_THRESHOLD]
        low_confidence = len(confident_chunks) == 0

        if low_confidence:
            logger.info(f"[RAG] No chunks above threshold {SIMILARITY_THRESHOLD}. Using low-confidence context.")
            confident_chunks = chunks[:2]

        messages = build_rag_prompt(query, confident_chunks, chat_history)

        system_msg = messages[0]["content"]
        user_parts = []
        for msg in messages[1:]:
            prefix = "User" if msg["role"] == "user" else "Assistant"
            user_parts.append(f"{prefix}: {msg['content']}")
        full_user_prompt = "\n\n".join(user_parts)

        answer = generate_with_context(system_msg, full_user_prompt, temperature=0.2)

        sources = list({c["source"] for c in confident_chunks}) if confident_chunks else []
        avg_confidence = (
            sum(c["score"] for c in confident_chunks) / len(confident_chunks)
            if confident_chunks else 0.0
        )

        result = {
            "answer": answer,
            "sources": sources,
            "confidence": round(avg_confidence, 3),
            "matched_chunks": [
                {"source": c["source"], "score": c["score"], "preview": c["text"][:120]}
                for c in confident_chunks
            ],
            "low_confidence": low_confidence,
        }

        await set_cached_answer(query, result, namespace)
        return result

    except Exception as e:
        logger.error(f"[RAG] Error: {e}", exc_info=True)
        return {
            "answer": "I encountered an error processing your query. Please try again.",
            "sources": [],
            "confidence": 0.0,
            "matched_chunks": [],
            "low_confidence": True,
        }
