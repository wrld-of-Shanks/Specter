"""
Doc QA Service — Per-document Q&A using ChromaDB namespaces.
Each uploaded document is chunked, embedded, and stored under a unique namespace.
Users can then ask questions scoped to that document.
"""

import logging
from typing import Dict, List, Optional
from doc_parser import parse_and_chunk
from embed_store import add_chunks_to_db, search_chunks, delete_namespace
from local_llm import generate_with_context

logger = logging.getLogger(__name__)

DOC_QA_SYSTEM_PROMPT = """You are SPECTER, an AI legal assistant specialized in Indian law.
You are answering a question about a specific document the user has uploaded.
Answer ONLY based on the document content provided in the context below.
If the document does not contain the information needed, say so clearly — do not use external knowledge.
Cite relevant sections or clauses from the document when possible."""


def index_document(text: str, doc_namespace: str, source_label: str = "uploaded_doc") -> int:
    chunks = parse_and_chunk(text)
    if not chunks:
        logger.warning(f"No chunks generated for document in namespace '{doc_namespace}'")
        return 0
    count = add_chunks_to_db(chunks, source=source_label, namespace=doc_namespace)
    logger.info(f"Indexed {count} chunks for doc namespace '{doc_namespace}'")
    return count


def answer_doc_question(
    question: str,
    doc_namespace: str,
    top_k: int = 5,
    similarity_threshold: float = 0.40,
) -> Dict:
    try:
        chunks = search_chunks(question, top_k=top_k, namespace=doc_namespace)
        if not chunks:
            return {
                "answer": "I could not find any relevant content in this document for your question.",
                "sources": [],
                "confidence": 0.0,
                "matched_chunks": [],
                "low_confidence": True,
            }

        confident_chunks = [c for c in chunks if c["score"] >= similarity_threshold]
        if not confident_chunks:
            confident_chunks = chunks[:2]

        context_parts = []
        for i, chunk in enumerate(confident_chunks, 1):
            context_parts.append(
                f"[Chunk {i} | relevance {chunk['score']:.0%}]\n{chunk['text']}"
            )
        context_block = "\n\n---\n\n".join(context_parts)

        user_prompt = (
            f"Document context:\n\n{context_block}\n\n"
            f"---\n\nUser question about this document: {question}"
        )

        answer = generate_with_context(DOC_QA_SYSTEM_PROMPT, user_prompt, temperature=0.15)

        avg_confidence = (
            sum(c["score"] for c in confident_chunks) / len(confident_chunks)
            if confident_chunks else 0.0
        )

        return {
            "answer": answer,
            "sources": [c["source"] for c in confident_chunks],
            "confidence": round(avg_confidence, 3),
            "matched_chunks": [
                {"source": c["source"], "score": c["score"], "preview": c["text"][:150]}
                for c in confident_chunks
            ],
            "low_confidence": len(confident_chunks) == 0 or avg_confidence < similarity_threshold,
        }
    except Exception as e:
        logger.error(f"[DocQA] Error: {e}", exc_info=True)
        return {
            "answer": "I encountered an error processing your question. Please try again.",
            "sources": [],
            "confidence": 0.0,
            "matched_chunks": [],
            "low_confidence": True,
        }


def remove_document_index(doc_namespace: str):
    delete_namespace(doc_namespace)
    logger.info(f"Removed document index for namespace '{doc_namespace}'")
