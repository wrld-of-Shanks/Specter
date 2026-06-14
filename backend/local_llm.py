"""
local_llm.py — Stub retained for import compatibility.

All LLM integration (Gemini, Ollama) has been removed since the
system now runs in retrieval-only mode exclusively.
"""

import logging

logger = logging.getLogger(__name__)


def generate_with_context(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    logger.warning("LLM integration is disabled. System runs in retrieval-only mode.")
    return "Error: LLM integration is disabled. The system operates in retrieval-only mode."
