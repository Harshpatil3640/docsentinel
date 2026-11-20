"""Pick the language model from settings in .env."""

import os

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel


def get_llm() -> BaseChatModel:
    """Return a chat model for LLM_PROVIDER: groq (default) or ollama."""
    load_dotenv()
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    if provider == "groq":
        from langchain_groq import ChatGroq

        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        return ChatGroq(model=model, temperature=0, max_retries=2)
    if provider == "ollama":
        from langchain_ollama import ChatOllama

        model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        return ChatOllama(model=model, temperature=0)
    raise ValueError(f"Unknown LLM_PROVIDER '{provider}'. Use groq or ollama.")