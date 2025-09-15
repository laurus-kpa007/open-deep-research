# vLLM Integration Guide

## Overview

This project now supports vLLM as an alternative LLM provider alongside Ollama. vLLM provides OpenAI API compatibility and is optimized for high-throughput serving of large language models.

## Features

- **Multiple LLM Providers**: Support for Ollama, vLLM, and future OpenAI integration
- **Optional API Key**: vLLM can work with or without authentication
- **Hybrid Mode**: Use different providers for different research stages
- **Automatic Fallback**: Falls back to Ollama if vLLM is unavailable

## Configuration

### Basic Setup

1. **Choose your provider** in `.env`:
```env
# Select your LLM provider
LLM_PROVIDER=vllm  # or "ollama" (default)
```

2. **Configure vLLM settings**:
```env
# vLLM server endpoint
VLLM_BASE_URL=http://localhost:8000

# Model name as registered in vLLM
VLLM_MODEL=meta-llama/Llama-3-8b

# Optional: API key (use "dummy" for local vLLM)
VLLM_API_KEY=your-api-key-here  # or "dummy" for no auth
```

### Starting vLLM Server

#### Local vLLM (No Authentication)
```bash
# Install vLLM
pip install vllm

# Start vLLM server with a model
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-8b \
    --port 8000 \
    --host 0.0.0.0
```

#### vLLM with API Key Authentication
```bash
# Start with API key verification
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-8b \
    --port 8000 \
    --host 0.0.0.0 \
    --api-key your-secret-key
```

#### Cloud-hosted vLLM
```env
# For cloud services (e.g., Anyscale, Together AI)
VLLM_BASE_URL=https://api.together.xyz
VLLM_MODEL=meta-llama/Llama-3-70b
VLLM_API_KEY=your-actual-api-key
```

## Hybrid Mode

Use different providers for different research stages:

```env
# In .env
LLM_PROVIDER=hybrid

# Stage-specific providers
SUMMARIZATION_PROVIDER=ollama      # Fast, local
RESEARCH_PROVIDER=vllm            # Powerful model
COMPRESSION_PROVIDER=ollama       # Fast, local
FINAL_REPORT_PROVIDER=vllm       # High quality output
```

## Testing

Run the test script to verify your configuration:

```bash
cd backend
python test_llm_providers.py
```

This will test:
- Ollama connectivity and generation
- vLLM connectivity and generation
- API key authentication (if configured)
- Hybrid mode configuration
- Automatic fallback mechanism

## Supported Models

### vLLM Models
- **Meta Llama 3**: `meta-llama/Llama-3-8b`, `meta-llama/Llama-3-70b`
- **Mistral**: `mistralai/Mistral-7B-v0.1`, `mistralai/Mixtral-8x7B`
- **Qwen**: `Qwen/Qwen2-7B`, `Qwen/Qwen2-72B`
- **DeepSeek**: `deepseek-ai/deepseek-llm-7b-base`
- Any HuggingFace model supported by vLLM

### Performance Comparison

| Provider | Latency | Throughput | Memory Usage | Best For |
|----------|---------|------------|--------------|----------|
| Ollama | Low | Medium | Low | Local development, quick responses |
| vLLM | Medium | High | High | Production, batch processing |

## Troubleshooting

### vLLM Server Not Found
```bash
# Check if vLLM is running
curl http://localhost:8000/v1/models

# Response should list available models
```

### API Key Issues
- For local vLLM without auth: Use `VLLM_API_KEY=dummy`
- For cloud services: Use your actual API key
- Check server logs for authentication errors

### Model Not Available
```bash
# List available models
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer your-api-key"
```

### Fallback to Ollama
If vLLM fails, the system automatically falls back to Ollama. Check logs:
```
WARNING: Falling back to Ollama provider
```

## Advanced Configuration

### Custom Temperature per Stage
The system automatically adjusts temperature based on the research stage:
- **Summarization**: 0.1 (focused)
- **Research**: 0.3 (balanced)
- **Compression**: 0.2 (focused)
- **Final Report**: 0.4 (creative)

### Streaming Support
Both Ollama and vLLM support streaming responses for real-time updates:
```python
async for chunk in client.stream_generate(prompt):
    print(chunk, end="", flush=True)
```

## API Compatibility

vLLM implements the OpenAI API specification, making it compatible with:
- OpenAI Python SDK
- LangChain
- Any OpenAI-compatible client

## Security Considerations

1. **API Keys**: Store sensitive keys in `.env` file (never commit to git)
2. **Network**: Use HTTPS for production vLLM endpoints
3. **CORS**: Configure CORS_ORIGINS appropriately
4. **Rate Limiting**: Implement rate limiting for public endpoints

## Future Enhancements

- [ ] OpenAI GPT models support
- [ ] Anthropic Claude support via API
- [ ] Load balancing between multiple vLLM instances
- [ ] Cost tracking and optimization
- [ ] Model performance benchmarking
- [ ] Automatic model selection based on task complexity