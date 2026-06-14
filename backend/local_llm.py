import os
import logging
from typing import List, Dict, Optional
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger(__name__)

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "lawman-legal")
def _build_ollama_url(path: str) -> str:
    base = OLLAMA_BASE_URL.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return base + path

def get_google_api_key():
    """Dynamically fetch the Google API key from environment variables."""
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")

def chat_with_gemini(messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
    """Call Google Gemini API"""
    try:
        api_key = get_google_api_key()
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is missing")
            
        genai.configure(api_key=api_key)
        
        # Try different model names in case one is not available in the region/key
        model_names = ['gemini-1.5-flash', 'gemini-flash-latest', 'gemini-2.0-flash', 'gemini-pro-latest', 'gemini-pro']
        last_err = None
        
        # Convert messages to Gemini format
        system_instruction = ""
        last_user_msg = ""
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                last_user_msg = msg["content"]

        if not last_user_msg:
            return "Error: No user message provided."

        for model_name in model_names:
            try:
                logger.info(f"Trying Gemini model: {model_name}")
                if system_instruction:
                    model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
                else:
                    model = genai.GenerativeModel(model_name)
                
                response = model.generate_content(
                    last_user_msg,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                    )
                )
                return response.text
            except Exception as e:
                last_err = e
                logger.warning(f"Model {model_name} failed: {e}")
                continue
        
        raise last_err or Exception("All Gemini models failed")
        
    except Exception as e:
        logger.error(f"Gemini API request failed: {e}")
        raise e

def chat_with_ollama(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """Call local Ollama chat API"""
    payload = {
        "model": model or OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    try:
        resp = requests.post(
            _build_ollama_url("/api/chat"), json=payload, timeout=120
        )
        resp.raise_for_status()
        data = resp.json()
        message = data.get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        return ""
    except Exception as e:
        logger.error(f"Ollama chat request failed: {e}")
        raise e

def generate_with_context(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """Convenience wrapper for single-turn question answering."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    
    api_key = get_google_api_key()
    
    # 1. Try Gemini first if API key is present
    if api_key:
        try:
            return chat_with_gemini(messages, temperature=temperature)
        except Exception as e:
            logger.warning(f"Gemini failed: {e}. Falling back to Ollama...")
    
    # 2. Fallback to Ollama
    try:
        logger.info(f"Attempting to use Ollama at {OLLAMA_BASE_URL}...")
        return chat_with_ollama(messages, temperature=temperature)
    except Exception as e:
        logger.error(f"All LLM providers failed. Last error: {e}")
        if not api_key:
            return "Error: GOOGLE_API_KEY is not set. Please check your .env file (local) or Render Dashboard (production)."
        return f"Error: LLM service unavailable (Gemini & Ollama both failed). Details: {str(e)}"

