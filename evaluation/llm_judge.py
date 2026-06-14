"""
evaluation/llm_judge.py
LLM-as-a-Judge harness.

Evaluates generated answers on two dimensions using a deterministic LLM call
(temperature=0.0, strict JSON output schema):

  1. Faithfulness / Groundedness (1-5): Is the answer strictly inferred from
     the retrieved context without hallucination?
  2. Answer Relevance (1-5): Does the answer directly address the user query?

Exponential backoff is built in to handle rate limits.
"""

import json
import logging
import os
import sys
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Maximum retries for LLM judge calls
MAX_RETRIES = 5
BASE_DELAY_SEC = 2.0

# ── judge prompt template ──────────────────────────────────────────────────

JUDGE_SYSTEM_PROMPT = """You are an expert evaluation judge for a legal AI assistant.
Your task is to score the quality of generated answers on two dimensions.

Rate STRICTLY on a 1-to-5 integer scale:

1. **Faithfulness / Groundedness** — Is the generated answer strictly supported by the provided context?
   - 5 = All claims are directly supported by the context; no hallucination.
   - 4 = Most claims are supported; minor unsupported elaboration.
   - 3 = Some claims supported; noticeable unsupported content.
   - 2 = Many claims unsupported; significant hallucination.
   - 1 = Answer is completely unsupported or contradicts the context.

2. **Answer Relevance** — Does the answer directly address the user's question?
   - 5 = Direct, complete, and concise answer to the query.
   - 4 = Mostly relevant; minor tangential content.
   - 3 = Partially relevant; some parts address the query.
   - 2 = Loosely related; most of the answer is off-topic.
   - 1 = Completely irrelevant to the query.

You MUST output valid JSON only, with no other text, in this exact format:
{"faithfulness": <int>, "relevance": <int>, "reasoning": "<brief explanation>"}"""


def _build_judge_user_prompt(
    query: str,
    context: str,
    generated_answer: str,
) -> str:
    return f"""Please evaluate the following legal Q&A pair.

USER QUERY:
{query}

RETRIEVED CONTEXT:
{context}

GENERATED ANSWER:
{generated_answer}

Score the generated answer on Faithfulness (1-5) and Relevance (1-5).
Output JSON only: {{"faithfulness": <int>, "relevance": <int>, "reasoning": "<brief explanation>"}}"""


# ── LLM judge call with backoff ─────────────────────────────────────────────


def _call_judge_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.0,
) -> Optional[str]:
    """
    Calls the LLM (same Gemini/Ollama backend as the production system)
    with exponential backoff for rate-limit handling.
    """
    # Import here to avoid circular imports and allow clean fallback
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
        from local_llm import generate_with_context
    except ImportError:
        logger.error("Could not import generate_with_context from backend")
        return None

    last_exception = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = generate_with_context(
                system_prompt, user_prompt, temperature=temperature,
            )
            if response and not response.startswith("Error"):
                return response

            logger.warning(
                f"Judge LLM returned error-like response (attempt {attempt}): {response[:80]}"
            )
        except Exception as e:
            last_exception = e
            logger.warning(
                f"Judge LLM call failed (attempt {attempt}/{MAX_RETRIES}): {e}"
            )

        if attempt < MAX_RETRIES:
            delay = BASE_DELAY_SEC * (2 ** (attempt - 1))
            logger.info(f"Retrying in {delay:.1f}s...")
            time.sleep(delay)

    logger.error(f"All {MAX_RETRIES} judge LLM attempts failed.")
    return None


def _parse_judge_response(response_text: str) -> Optional[Dict]:
    """Parse JSON from the LLM response with lenient fallback."""
    if not response_text:
        return None

    # Try direct JSON parse first
    try:
        parsed = json.loads(response_text.strip())
        if isinstance(parsed, dict) and "faithfulness" in parsed and "relevance" in parsed:
            return parsed
    except json.JSONDecodeError:
        pass

    # Fallback: try to extract JSON from markdown ```json ... ```
    import re
    json_match = re.search(r"```(?:json)?\s*\n?({.*?})\s*\n?```", response_text, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    # Last resort: try to find any JSON-like dict
    json_match = re.search(r"\{[^{}]*\"faithfulness\"[^{}]*\"relevance\"[^{}]*\}", response_text, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(0))
            return parsed
        except json.JSONDecodeError:
            pass

    return None


# ── public API ──────────────────────────────────────────────────────────────


def judge_answer(
    query: str,
    context: str,
    generated_answer: str,
) -> Dict:
    """
    Evaluate a generated answer using LLM-as-a-Judge.

    Returns:
    {
        "faithfulness": int (1-5) or 0 if evaluation failed,
        "relevance": int (1-5) or 0 if evaluation failed,
        "reasoning": str,
        "judge_success": bool,
    }
    """
    default_result = {
        "faithfulness": 0,
        "relevance": 0,
        "reasoning": "Evaluation failed",
        "judge_success": False,
    }

    user_prompt = _build_judge_user_prompt(query, context, generated_answer)
    raw = _call_judge_llm(JUDGE_SYSTEM_PROMPT, user_prompt, temperature=0.0)

    if not raw:
        return default_result

    parsed = _parse_judge_response(raw)
    if parsed is None:
        logger.warning(f"Could not parse judge response: {raw[:200]}")
        return {**default_result, "reasoning": f"Parse failure. Raw: {raw[:100]}"}

    faithfulness = parsed.get("faithfulness", 0)
    relevance = parsed.get("relevance", 0)

    # Clamp values to 1-5
    faithfulness = max(1, min(5, int(faithfulness))) if isinstance(faithfulness, (int, float)) else 0
    relevance = max(1, min(5, int(relevance))) if isinstance(relevance, (int, float)) else 0

    return {
        "faithfulness": faithfulness,
        "relevance": relevance,
        "reasoning": parsed.get("reasoning", "")[:300],
        "judge_success": True,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Self-test
    result = judge_answer(
        query="What is the punishment for murder under BNS?",
        context="Section 103 BNS prescribes death or life imprisonment for murder.",
        generated_answer="The punishment for murder under BNS is death or life imprisonment.",
    )
    print(json.dumps(result, indent=2))
