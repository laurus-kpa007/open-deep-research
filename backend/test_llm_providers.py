"""Test script for LLM providers."""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from open_deep_research.core.llm_providers import LLMFactory, LLMProvider
from open_deep_research.core.llm_adapter import get_llm_client


async def test_ollama_client():
    """Test Ollama client."""
    print("\n=== Testing Ollama Client ===")
    try:
        client = LLMFactory.create_client("ollama")

        # Test health check
        print("Checking Ollama health...")
        is_healthy = await client.health_check()
        print(f"Ollama health check: {'✓ Healthy' if is_healthy else '✗ Not available'}")

        if is_healthy:
            # Test generation
            print("\nTesting generation...")
            response = await client.generate(
                "Say 'Hello from Ollama' in one sentence.",
                stage="research"
            )
            print(f"Response: {response[:100]}...")

            # Test streaming
            print("\nTesting streaming...")
            print("Stream response: ", end="")
            async for chunk in client.stream_generate(
                "Count from 1 to 5.",
                stage="research"
            ):
                print(chunk, end="", flush=True)
            print("\n✓ Ollama tests completed")
        else:
            print("⚠ Skipping Ollama tests - server not available")

    except Exception as e:
        print(f"✗ Ollama test failed: {e}")


async def test_vllm_client():
    """Test vLLM client."""
    print("\n=== Testing vLLM Client ===")
    try:
        # Test with optional API key
        api_key = os.getenv("VLLM_API_KEY", "dummy")
        client = LLMFactory.create_client(
            "vllm",
            api_key=api_key  # Can be "dummy" for local vLLM or actual key
        )

        # Test health check
        print("Checking vLLM health...")
        is_healthy = await client.health_check()
        print(f"vLLM health check: {'✓ Healthy' if is_healthy else '✗ Not available'}")

        if is_healthy:
            # Test generation
            print("\nTesting generation...")
            response = await client.generate(
                "Say 'Hello from vLLM' in one sentence.",
                stage="research"
            )
            print(f"Response: {response[:100]}...")

            # Test streaming
            print("\nTesting streaming...")
            print("Stream response: ", end="")
            async for chunk in client.stream_generate(
                "Count from 1 to 5.",
                stage="research"
            ):
                print(chunk, end="", flush=True)
            print("\n✓ vLLM tests completed")
        else:
            print("⚠ Skipping vLLM tests - server not available")

    except Exception as e:
        print(f"✗ vLLM test failed: {e}")


async def test_adapter():
    """Test the LLM adapter."""
    print("\n=== Testing LLM Adapter ===")
    try:
        # Test getting client from environment
        current_provider = os.getenv("LLM_PROVIDER", "ollama")
        print(f"Current provider from env: {current_provider}")

        client = get_llm_client()
        print(f"✓ Got {current_provider} client from adapter")

        # Test health check
        is_healthy = await client.health_check()
        print(f"Health check: {'✓ Healthy' if is_healthy else '✗ Not available'}")

    except Exception as e:
        print(f"✗ Adapter test failed: {e}")


async def test_hybrid_mode():
    """Test hybrid mode with different providers for different stages."""
    print("\n=== Testing Hybrid Mode ===")
    try:
        # Create hybrid client configuration
        stage_providers = {
            "summarization": "ollama",
            "research": "ollama",  # Change to "vllm" if vLLM is available
            "compression": "ollama",
            "final_report": "ollama",
        }

        clients = LLMFactory.create_hybrid_client(stage_providers)
        print(f"✓ Created hybrid clients for {len(clients)} stages")

        # Test each client
        for stage, client in clients.items():
            is_healthy = await client.health_check()
            provider_type = type(client).__name__
            print(f"  {stage}: {provider_type} - {'✓ Healthy' if is_healthy else '✗ Not available'}")

    except Exception as e:
        print(f"✗ Hybrid mode test failed: {e}")


async def main():
    """Run all tests."""
    print("=" * 50)
    print("LLM Provider Test Suite")
    print("=" * 50)

    # Show current configuration
    print("\nCurrent Configuration:")
    print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'ollama')}")
    print(f"  OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
    print(f"  OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'gemma3:4b')}")
    print(f"  VLLM_BASE_URL: {os.getenv('VLLM_BASE_URL', 'http://localhost:8000')}")
    print(f"  VLLM_MODEL: {os.getenv('VLLM_MODEL', 'meta-llama/Llama-3-8b')}")
    print(f"  VLLM_API_KEY: {'***' if os.getenv('VLLM_API_KEY') else 'Not set (will use dummy)'}")

    # Run tests
    await test_ollama_client()
    await test_vllm_client()
    await test_adapter()
    await test_hybrid_mode()

    print("\n" + "=" * 50)
    print("Test suite completed")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())