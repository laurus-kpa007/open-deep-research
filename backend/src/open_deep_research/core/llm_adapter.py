"""LLM Adapter for seamless integration with research workflow."""

import os
import logging
from typing import Optional
from .llm_providers import LLMFactory, BaseLLMClient

logger = logging.getLogger(__name__)


def get_llm_client(
    provider: Optional[str] = None,
    **kwargs
) -> BaseLLMClient:
    """
    Get an LLM client based on configuration.

    This function provides a simple interface for the research workflow
    to get the appropriate LLM client without knowing the implementation details.

    Args:
        provider: Optional provider override. If None, uses LLM_PROVIDER env var.
        **kwargs: Additional arguments for the client.

    Returns:
        BaseLLMClient: The configured LLM client.
    """
    try:
        # Get provider from environment if not specified
        provider = provider or os.getenv("LLM_PROVIDER", "ollama")
        logger.info(f"Initializing LLM client with provider: {provider}")

        # Create and return the client
        client = LLMFactory.create_client(provider, **kwargs)

        # Log successful initialization
        logger.info(f"Successfully initialized {provider} LLM client")

        return client

    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        # Fallback to Ollama if specified provider fails
        if provider != "ollama":
            logger.warning("Falling back to Ollama provider")
            return LLMFactory.create_client("ollama", **kwargs)
        raise


# For backward compatibility
def get_ollama_client(**kwargs) -> BaseLLMClient:
    """
    Get an Ollama client for backward compatibility.

    This function is deprecated. Use get_llm_client() instead.
    """
    logger.warning("get_ollama_client() is deprecated. Use get_llm_client() instead.")
    return get_llm_client(provider="ollama", **kwargs)