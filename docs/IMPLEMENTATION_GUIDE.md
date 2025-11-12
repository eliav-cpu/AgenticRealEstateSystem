# Implementation Guide - Reviews System Components

## Overview

This document describes the implementation of the Reviews System components including mock data generation, Groq LLM integration, context engineering, and observability tools.

## Components Implemented

### 1. Mock Property Data Generator (`src/generators/mock_property_generator.py`)

**Purpose**: Generate 10,000 realistic house entries for testing and development.

**Features**:
- Generates realistic property data with 27 attributes
- Supports multiple property types (Single Family, Condo, Townhouse, etc.)
- Realistic pricing based on location, size, and features
- Geographic distribution across 5 states
- Reproducible with seed support
- Exports to JSON and DuckDB

**Usage**:
```python
from src.generators import MockPropertyGenerator

# Initialize generator
generator = MockPropertyGenerator(seed=42)

# Generate 10,000 properties
properties = generator.generate_batch(10000)

# Save to JSON
generator.save_to_json(properties, "data/mock_properties.json")

# Save to DuckDB
generator.save_to_duckdb(properties, "data/properties.duckdb")
```

**Command Line**:
```bash
python scripts/generate_mock_data.py --count 10000 --output data/mock_properties.json
```

### 2. Groq LLM Client (`src/llm/groq_client.py`)

**Purpose**: Integrate Groq API with moonshotai/kimi-k2-instruct-0905 model.

**Features**:
- Synchronous and asynchronous clients
- Streaming support
- Configuration management
- Type-safe message handling
- Token tracking

**Usage**:
```python
from src.llm import create_client, LLMMessage

# Create client
client = create_client(async_mode=False)

# Send chat completion
messages = [
    LLMMessage(role="system", content="You are a real estate assistant"),
    LLMMessage(role="user", content="Find 3-bedroom houses")
]

response = client.chat(messages)
print(response.content)
print(f"Tokens used: {response.tokens_used}")
```

**Async Usage**:
```python
import asyncio
from src.llm import create_client

async def main():
    client = create_client(async_mode=True)
    response = await client.complete("Find properties in Austin")
    print(response.content)

asyncio.run(main())
```

### 3. Context Engineering (`src/llm/context_engineering.py`)

**Purpose**: Optimize prompts and manage context for better LLM performance.

**Components**:
- **PromptOptimizer**: Create optimized prompts for different tasks
- **ContextRetriever**: Retrieve relevant context and properties
- **TokenManager**: Manage token usage and optimize data

**Usage**:
```python
from src.llm import PromptOptimizer, ContextRetriever, TokenManager

# Optimize prompts
optimizer = PromptOptimizer()
prompt = optimizer.create_real_estate_prompt(
    query="Find family homes",
    property_data=property_dict
)

# Retrieve relevant properties
retriever = ContextRetriever()
relevant = retriever.retrieve_relevant_properties(
    query="pool family home",
    properties=all_properties,
    top_k=5
)

# Manage tokens
token_mgr = TokenManager()
estimated = token_mgr.estimate_tokens(prompt)
optimized_data = token_mgr.optimize_property_data(property_dict)
```

### 4. Langfuse Integration (`src/observability/langfuse_integration.py`)

**Purpose**: Track LLM prompts, completions, traces, and performance metrics.

**Features**:
- Trace LLM calls
- Track generations with token usage
- Score generations for quality
- Session and user tracking

**Usage**:
```python
from src.observability import create_langfuse_observer

# Create observer
observer = create_langfuse_observer(enabled=True)

# Trace LLM call
observer.trace_generation(
    name="property_search",
    model="moonshotai/kimi-k2-instruct-0905",
    prompt="Find properties...",
    completion="Here are properties...",
    tokens_input=50,
    tokens_output=200,
    metadata={"user_id": "123"}
)

# Flush traces
observer.flush()
```

**Environment Variables**:
```bash
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 5. Logfire Integration (`src/observability/logfire_integration.py`)

**Purpose**: Structured logging, metrics, and application traces.

**Features**:
- Structured logging (info, warning, error)
- Performance tracing
- Metrics collection
- Operation tracking

**Usage**:
```python
from src.observability import create_logfire_observer, PerformanceTracer

# Create observer
observer = create_logfire_observer(enabled=True)

# Log messages
observer.log_info("Application started", version="1.0.0")

# Trace operations
with PerformanceTracer(observer, "property_search", query="homes"):
    # Perform search
    results = search_properties(query)
    observer.log_info("Search completed", result_count=len(results))

# Log LLM requests
observer.log_llm_request(
    model="moonshotai/kimi-k2-instruct-0905",
    prompt="Find properties",
    response="Here are properties...",
    tokens=150,
    duration=0.5
)
```

**Environment Variables**:
```bash
LOGFIRE_TOKEN=your_token
```

### 6. Configuration Manager (`src/config/config_manager.py`)

**Purpose**: Centralized configuration management with environment variable support.

**Features**:
- Type-safe configuration classes
- Environment variable loading from .env
- Configuration validation
- Global configuration access

**Usage**:
```python
from src.config import get_config

# Get configuration
config = get_config()

# Access settings
print(config.llm.api_key)
print(config.llm.default_model)
print(config.data.mode)
print(config.observability.langfuse_enabled)

# Validate configuration
config_manager = ConfigManager()
is_valid = config_manager.validate()
```

## Installation

### Install Dependencies

```bash
# Core dependencies
pip install groq duckdb

# Observability (optional)
pip install langfuse logfire

# Testing
pip install pytest pytest-asyncio
```

### Environment Setup

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Configure required variables in `.env`:
```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional observability
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LOGFIRE_TOKEN=your_token
```

## Quick Start

### 1. Generate Mock Data

```bash
python scripts/generate_mock_data.py --count 10000
```

### 2. Test LLM Integration

```python
from src.llm import create_client, LLMMessage
from src.config import get_config

config = get_config()

client = create_client()
messages = [
    LLMMessage(role="system", content="You are a real estate assistant"),
    LLMMessage(role="user", content="What are key factors when buying a house?")
]

response = client.chat(messages)
print(response.content)
```

### 3. Test Observability

```python
from src.observability import create_langfuse_observer, create_logfire_observer

# Langfuse
langfuse = create_langfuse_observer(enabled=True)
langfuse.trace_generation(
    name="test",
    model="moonshotai/kimi-k2-instruct-0905",
    prompt="Test",
    completion="Response",
    tokens_input=10,
    tokens_output=20
)

# Logfire
logfire = create_logfire_observer(enabled=True)
logfire.log_info("Test message", component="test")
```

## Testing

Run tests:
```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/generators/test_mock_generator.py -v
pytest tests/llm/test_groq_client.py -v
```

## Architecture

### Directory Structure

```
src/
├── __init__.py
├── generators/
│   ├── __init__.py
│   └── mock_property_generator.py
├── llm/
│   ├── __init__.py
│   ├── groq_client.py
│   └── context_engineering.py
├── observability/
│   ├── __init__.py
│   ├── langfuse_integration.py
│   └── logfire_integration.py
└── config/
    ├── __init__.py
    └── config_manager.py

tests/
├── generators/
│   └── test_mock_generator.py
└── llm/
    └── test_groq_client.py

scripts/
└── generate_mock_data.py

docs/
└── IMPLEMENTATION_GUIDE.md
```

### Component Interactions

```
Configuration Manager
    ↓
    ├── LLM Client ←→ Context Engineering
    │       ↓
    │   Observability (Langfuse + Logfire)
    │
    └── Mock Generator → DuckDB / JSON
```

## Best Practices

### 1. Environment Management

- Never commit `.env` files
- Use `.env.example` for documentation
- Validate configuration on startup

### 2. Error Handling

```python
try:
    response = client.chat(messages)
except Exception as e:
    observer.log_error("LLM request failed", error=e)
    raise
```

### 3. Token Optimization

```python
# Estimate tokens before sending
tokens = TokenManager.estimate_tokens(prompt)
if tokens > max_tokens:
    prompt = TokenManager.truncate_to_tokens(prompt, max_tokens)
```

### 4. Observability

- Always trace LLM calls in production
- Log performance metrics
- Track errors with context

### 5. Testing

- Use seed for reproducible test data
- Mock external API calls
- Test error scenarios

## Integration Examples

### Real Estate Agent with Full Stack

```python
from src.generators import MockPropertyGenerator
from src.llm import create_client, PromptOptimizer
from src.observability import create_langfuse_observer, PerformanceTracer

# Setup
generator = MockPropertyGenerator(seed=42)
properties = generator.generate_batch(100)
client = create_client()
optimizer = PromptOptimizer()
observer = create_langfuse_observer(enabled=True)

# Search properties
query = "Find family homes with pools"

with PerformanceTracer(observer, "property_search", query=query):
    # Retrieve relevant properties
    from src.llm import ContextRetriever
    retriever = ContextRetriever()
    relevant = retriever.retrieve_relevant_properties(query, properties, top_k=5)

    # Create optimized prompt
    prompt = optimizer.create_search_prompt(query)

    # Get LLM response
    messages = [{"role": "user", "content": prompt}]
    response = client.chat(messages)

    # Log to Langfuse
    observer.trace_generation(
        name="property_search",
        model=response.model,
        prompt=prompt,
        completion=response.content,
        tokens_input=response.tokens_used // 2,
        tokens_output=response.tokens_used // 2
    )

    print(response.content)
```

## Troubleshooting

### Issue: Groq API Key Not Working

**Solution**:
```bash
# Verify key is set
echo $GROQ_API_KEY

# Or check in .env
grep GROQ_API_KEY .env
```

### Issue: Langfuse Not Tracking

**Solution**:
```python
# Check if enabled
observer = create_langfuse_observer(enabled=True)
if not observer.enabled:
    print("Langfuse not configured. Check environment variables.")

# Always flush at end
observer.flush()
```

### Issue: DuckDB Permission Error

**Solution**:
```bash
# Check directory exists and is writable
mkdir -p data
chmod 755 data
```

## Performance Considerations

### Mock Data Generation

- Generates ~1000 properties/second
- Memory usage: ~100MB for 10,000 properties
- JSON file size: ~50MB for 10,000 properties

### LLM Calls

- Average latency: 0.5-2 seconds
- Token limits: 2000 tokens default
- Use streaming for long responses

### Context Retrieval

- Semantic search: O(n) complexity
- Optimize with caching for repeated queries
- Use top_k to limit results

## Next Steps

1. **Integration with Existing Agents**: Integrate LLM client with search, property, and scheduling agents
2. **Caching Layer**: Add Redis caching for LLM responses
3. **Vector Search**: Implement vector embeddings for semantic search
4. **Rate Limiting**: Add rate limiting for API calls
5. **Monitoring Dashboard**: Create dashboard for observability metrics

## Support

For issues or questions:
- Check configuration with `ConfigManager().validate()`
- Review logs in `logs/` directory
- Run tests with `pytest tests/ -v`
- Check environment variables are properly set
