"""Ollama client for LLM integration."""

import os
from typing import Optional, Dict, Any, AsyncGenerator
import aiohttp
import json
import logging
from langchain_ollama import OllamaLLM
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama LLM server."""
    
    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        timeout: int = 300
    ):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "gemma3:12b")
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