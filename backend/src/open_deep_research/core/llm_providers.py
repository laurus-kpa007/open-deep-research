"""LLM Provider abstraction for supporting multiple LLM backends."""

import os
import json
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any, AsyncGenerator
import aiohttp
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseLLM

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    VLLM = "vllm"
    OPENAI = "openai"  # For future extension


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(self, prompt: str, stage: str = "research", **kwargs) -> str:
        """Generate response from LLM."""
        pass

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        stage: str = "research",
        callback: Optional[callable] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response generation."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if LLM service is available."""
        pass

    @abstractmethod
    def get_llm_for_stage(self, stage: str) -> BaseLLM:
        """Get appropriate LLM instance for research stage."""
        pass


class OllamaLLMClient(BaseLLMClient):
    """Ollama LLM client implementation."""

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        timeout: int = 300
    ):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "gemma3:4b")
        self.timeout = timeout

        # Initialize different LLM instances for different tasks
        self.summarization_llm = OllamaLLM(
            base_url=self.base_url,
            model=self.model,
            temperature=0.1,  # More focused for summarization
            timeout=timeout
        )

        self.research_llm = OllamaLLM(
            base_url=self.base_url,
            model=self.model,
            temperature=0.3,  # Balanced for research
            timeout=timeout
        )

        self.compression_llm = OllamaLLM(
            base_url=self.base_url,
            model=self.model,
            temperature=0.2,  # Focused for compression
            timeout=timeout
        )

        self.final_report_llm = OllamaLLM(
            base_url=self.base_url,
            model=self.model,
            temperature=0.4,  # More creative for final report
            timeout=timeout
        )

    def get_llm_for_stage(self, stage: str) -> BaseLLM:
        """Get appropriate LLM instance for research stage."""
        llm_map = {
            "summarization": self.summarization_llm,
            "research": self.research_llm,
            "compression": self.compression_llm,
            "final_report": self.final_report_llm,
            "clarification": self.research_llm,
            "brief": self.research_llm,
            "supervisor": self.research_llm
        }
        return llm_map.get(stage, self.research_llm)

    async def generate(
        self,
        prompt: str,
        stage: str = "research",
        **kwargs
    ) -> str:
        """Generate response using appropriate LLM for the stage."""
        try:
            llm = self.get_llm_for_stage(stage)
            response = await llm.ainvoke(prompt, **kwargs)
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    async def stream_generate(
        self,
        prompt: str,
        stage: str = "research",
        callback: Optional[callable] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response generation with optional callback for real-time updates."""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": self._get_options_for_stage(stage)
                }

                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {error_text}")

                    buffer = ""
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                if 'response' in data:
                                    chunk = data['response']
                                    buffer += chunk

                                    if callback:
                                        await callback(chunk, data.get('done', False))

                                    yield chunk

                                if data.get('done', False):
                                    break

                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"Error in stream generation: {e}")
            raise

    def _get_options_for_stage(self, stage: str) -> Dict[str, Any]:
        """Get Ollama options based on research stage."""
        stage_options = {
            "summarization": {"temperature": 0.1, "top_p": 0.9},
            "research": {"temperature": 0.3, "top_p": 0.95},
            "compression": {"temperature": 0.2, "top_p": 0.9},
            "final_report": {"temperature": 0.4, "top_p": 0.95},
        }
        return stage_options.get(stage, {"temperature": 0.3, "top_p": 0.95})

    async def health_check(self) -> bool:
        """Check if Ollama server is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Check if our model is available
                        models = [model['name'] for model in data.get('models', [])]
                        return self.model in models
                    return False
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False

    async def pull_model(self) -> bool:
        """Pull the required model if not available."""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"name": self.model}
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=1800)  # 30 minutes for model pull
                ) as response:
                    if response.status == 200:
                        # Stream the pull progress
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    logger.info(f"Model pull progress: {data.get('status', 'Unknown')}")
                                except json.JSONDecodeError:
                                    continue
                        return True
                    return False
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False


class VLLMClient(BaseLLMClient):
    """vLLM client implementation (OpenAI API compatible)."""

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        api_key: Optional[str] = None,
        timeout: int = 300
    ):
        self.base_url = base_url or os.getenv("VLLM_BASE_URL", "http://localhost:8000")
        self.model = model or os.getenv("VLLM_MODEL", "meta-llama/Llama-3-8b")
        # Use provided API key, or get from env, or use "dummy" for local vLLM
        # If VLLM_API_KEY is empty string, use "dummy"
        env_key = os.getenv("VLLM_API_KEY", "dummy")
        self.api_key = api_key or (env_key if env_key else "dummy")
        self.timeout = timeout

        # Initialize different ChatOpenAI instances for different tasks
        self.summarization_llm = ChatOpenAI(
            base_url=f"{self.base_url}/v1",
            api_key=self.api_key,
            model=self.model,
            temperature=0.1,
            timeout=timeout,
            max_retries=2
        )

        self.research_llm = ChatOpenAI(
            base_url=f"{self.base_url}/v1",
            api_key=self.api_key,
            model=self.model,
            temperature=0.3,
            timeout=timeout,
            max_retries=2
        )

        self.compression_llm = ChatOpenAI(
            base_url=f"{self.base_url}/v1",
            api_key=self.api_key,
            model=self.model,
            temperature=0.2,
            timeout=timeout,
            max_retries=2
        )

        self.final_report_llm = ChatOpenAI(
            base_url=f"{self.base_url}/v1",
            api_key=self.api_key,
            model=self.model,
            temperature=0.4,
            timeout=timeout,
            max_retries=2
        )

    def get_llm_for_stage(self, stage: str) -> BaseLLM:
        """Get appropriate LLM instance for research stage."""
        llm_map = {
            "summarization": self.summarization_llm,
            "research": self.research_llm,
            "compression": self.compression_llm,
            "final_report": self.final_report_llm,
            "clarification": self.research_llm,
            "brief": self.research_llm,
            "supervisor": self.research_llm
        }
        return llm_map.get(stage, self.research_llm)

    async def generate(
        self,
        prompt: str,
        stage: str = "research",
        **kwargs
    ) -> str:
        """Generate response using appropriate LLM for the stage."""
        try:
            llm = self.get_llm_for_stage(stage)
            response = await llm.ainvoke(prompt, **kwargs)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"Error generating response from vLLM: {e}")
            raise

    async def stream_generate(
        self,
        prompt: str,
        stage: str = "research",
        callback: Optional[callable] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response generation with optional callback."""
        try:
            llm = self.get_llm_for_stage(stage)

            # Use astream for streaming responses
            async for chunk in llm.astream(prompt):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)

                if callback:
                    await callback(content, False)

                yield content

            if callback:
                await callback("", True)  # Signal completion

        except Exception as e:
            logger.error(f"Error in vLLM stream generation: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if vLLM server is available."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.api_key and self.api_key != "dummy":
                    headers["Authorization"] = f"Bearer {self.api_key}"

                async with session.get(
                    f"{self.base_url}/v1/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Check if our model is available
                        models = [model['id'] for model in data.get('data', [])]
                        return any(self.model in model for model in models)
                    return False
        except Exception as e:
            logger.error(f"vLLM health check failed: {e}")
            return False


class LLMFactory:
    """Factory for creating LLM clients based on provider."""

    @staticmethod
    def create_client(
        provider: Optional[str] = None,
        **kwargs
    ) -> BaseLLMClient:
        """
        Create an LLM client based on the provider.

        Args:
            provider: The LLM provider to use. If None, uses LLM_PROVIDER env var.
            **kwargs: Additional arguments to pass to the client constructor.

        Returns:
            BaseLLMClient: The created LLM client.
        """
        provider = provider or os.getenv("LLM_PROVIDER", "ollama")
        provider = provider.lower()

        if provider == "ollama":
            return OllamaLLMClient(**kwargs)
        elif provider == "vllm":
            return VLLMClient(**kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @staticmethod
    def create_hybrid_client(
        stage_providers: Optional[Dict[str, str]] = None
    ) -> Dict[str, BaseLLMClient]:
        """
        Create multiple LLM clients for different stages.

        Args:
            stage_providers: Mapping of stage to provider.
                           If None, uses environment variables.

        Returns:
            Dict[str, BaseLLMClient]: Mapping of stage to LLM client.
        """
        if stage_providers is None:
            # Read from environment variables
            stage_providers = {
                "summarization": os.getenv("SUMMARIZATION_PROVIDER", "ollama"),
                "research": os.getenv("RESEARCH_PROVIDER", "ollama"),
                "compression": os.getenv("COMPRESSION_PROVIDER", "ollama"),
                "final_report": os.getenv("FINAL_REPORT_PROVIDER", "ollama"),
            }

        clients = {}
        for stage, provider in stage_providers.items():
            clients[stage] = LLMFactory.create_client(provider)

        return clients


# Backward compatibility - keep the original OllamaClient name
OllamaClient = OllamaLLMClient