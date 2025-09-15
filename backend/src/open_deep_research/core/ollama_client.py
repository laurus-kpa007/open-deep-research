"""Ollama client for LLM integration - backward compatibility wrapper."""

import logging
from .llm_providers import OllamaLLMClient, LLMFactory

logger = logging.getLogger(__name__)

# For backward compatibility, expose OllamaLLMClient as OllamaClient
OllamaClient = OllamaLLMClient

# Also expose the factory for convenience
__all__ = ['OllamaClient', 'LLMFactory']