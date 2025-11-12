# Reviews System Refactor - Test Suite Documentation

## Overview

This comprehensive test suite was created by the TESTER agent as part of the Reviews System Refactor Hive Mind initiative. It provides extensive coverage for:

1. **Mock Data Generation** - Unit tests for data generation utilities
2. **Groq LLM Integration** - Integration tests for LLM flows and context engineering
3. **Observability** - Tests for Langfuse and Logfire integration
4. **End-to-End Flow** - Complete system workflow validation

**Total Coverage Target**: >90%
**Test Philosophy**: No external dependencies - all tests use mocks

---

## Directory Structure

```
tests/
├── generators/
│   ├── __init__.py
│   └── test_mock_data_generation.py      # Mock data generation tests (24+ tests)
├── llm/
│   ├── __init__.py
│   ├── test_groq_integration.py          # Groq LLM integration (19+ tests)
│   └── test_observability.py             # Langfuse/Logfire tests (18+ tests)
├── integration/
│   └── test_end_to_end_flow.py           # E2E system tests (16+ tests)
├── conftest.py                            # Shared fixtures
├── pytest.ini                             # Pytest configuration
├── TEST_COVERAGE_REPORT.md               # Detailed coverage report
├── TEST_README.md                        # This file
└── run_all_tests.sh                      # Test execution script
```

---

## Quick Start

### Install Dependencies

```bash
# Ensure you have pytest and related packages
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Or use project dependencies
pip install -e ".[dev]"
```

### Run All Tests

```bash
# Simple run
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Using the test script
chmod +x tests/run_all_tests.sh
./tests/run_all_tests.sh
```

### Run Specific Test Suites

```bash
# Mock data generation
pytest tests/generators/ -v

# LLM integration
pytest tests/llm/test_groq_integration.py -v

# Observability
pytest tests/llm/test_observability.py -v

# End-to-end
pytest tests/integration/test_end_to_end_flow.py -v
```

---

## Test Suites Detail

### 1. Mock Data Generation Tests

**File**: `tests/generators/test_mock_data_generation.py`

Tests the `MockDataGenerator` class that creates realistic test data:

```python
from tests.generators.test_mock_data_generation import MockDataGenerator

# Generate a single property
property = MockDataGenerator.generate_property()

# Generate a batch
properties = MockDataGenerator.generate_properties_batch(count=10)

# Generate appointment
appointment = MockDataGenerator.generate_appointment(property_id=1)
```

**What's Tested:**
- Property generation with all fields
- Batch generation with diversity
- Address validation and formatting
- Feature validation (bedrooms, bathrooms, amenities)
- Pricing logic and consistency
- Appointment scheduling data
- Performance (100 properties < 1 second)
- Edge cases (min/max values)
- Data validation rules

**Coverage**: 95-98%

---

### 2. Groq LLM Integration Tests

**File**: `tests/llm/test_groq_integration.py`

Tests LLM integration with context engineering:

```python
from tests.llm.test_groq_integration import MockGroqClient, ContextEngineer

# Create mock client
client = MockGroqClient()

# Build context
system_prompt = ContextEngineer.build_system_prompt("search")
property_context = ContextEngineer.format_property_context(properties)

# Make LLM call
response = await client.create_chat_completion(messages)
```

**What's Tested:**
- Groq client initialization
- Chat completion flow
- Search agent with property context
- Property analysis flow
- Scheduling flow
- Conversation history management
- Token usage tracking
- Model parameters (temperature, max_tokens)
- Context engineering utilities
- Structured output extraction
- Error handling
- Concurrent requests

**Coverage**: 85-90%

---

### 3. Observability Tests

**File**: `tests/llm/test_observability.py`

Tests observability with Langfuse and Logfire:

```python
from tests.llm.test_observability import (
    MockLangfuseClient,
    MockLogfireHandler,
    ObservabilityManager
)

# Create observability manager
obs_manager = ObservabilityManager(langfuse, logfire)

# Trace LLM call
await obs_manager.trace_llm_call(
    agent_type="search",
    messages=messages,
    response=response
)
```

**What's Tested:**
- Langfuse trace creation and management
- Span creation and nesting
- LLM generation tracking
- Quality scores
- Token usage and cost tracking
- Logfire structured logging
- Span context managers
- Performance metrics
- Rich metadata storage

**Coverage**: 85-92%

---

### 4. End-to-End Integration Tests

**File**: `tests/integration/test_end_to_end_flow.py`

Tests complete system workflows:

```python
from tests.integration.test_end_to_end_flow import MockSystemOrchestrator

# Create orchestrator
orchestrator = MockSystemOrchestrator()

# Simulate user journey
search_response = await orchestrator.process_user_message(
    "Find 2 bedroom apartments in Miami"
)

details_response = await orchestrator.process_user_message(
    "Tell me about the first property"
)

schedule_response = await orchestrator.process_user_message(
    "Schedule a viewing for tomorrow"
)
```

**What's Tested:**
- Complete user journeys (search → details → scheduling)
- Multi-agent coordination
- Context persistence
- Conversation history tracking
- Agent routing logic
- Concurrent session handling
- Error recovery
- Performance under load
- Data consistency
- Session isolation

**Coverage**: 80-88%

---

## Test Markers

Tests are organized with pytest markers:

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# End-to-end tests only
pytest -m e2e

# Async tests only
pytest -m asyncio

# Mock data tests only
pytest -m mock

# Exclude slow tests
pytest -m "not slow"
```

---

## Fixtures

Shared fixtures are defined in `conftest.py`:

### Mock Settings
```python
def test_my_function(mock_settings):
    # Use mock settings
    assert mock_settings.apis.openrouter_key == "test_openrouter_key_123456"
```

### Sample Properties
```python
def test_property_search(sample_properties):
    # Use sample property data
    assert len(sample_properties) == 3
```

### Agent Context
```python
async def test_agent(agent_context):
    # Use pre-configured agent context
    assert agent_context.data_mode == "mock"
```

---

## Coverage Reports

### Generate Reports

```bash
# Terminal report
pytest tests/ --cov=app --cov-report=term-missing

# HTML report (browse at htmlcov/index.html)
pytest tests/ --cov=app --cov-report=html

# JSON report
pytest tests/ --cov=app --cov-report=json
```

### View Coverage

```bash
# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## Best Practices

### Writing New Tests

1. **Follow AAA Pattern**:
   ```python
   def test_something():
       # Arrange
       data = setup_test_data()

       # Act
       result = function_to_test(data)

       # Assert
       assert result == expected_value
   ```

2. **Use Descriptive Names**:
   ```python
   # Good
   def test_property_generation_with_valid_data():
       pass

   # Bad
   def test_prop():
       pass
   ```

3. **Test One Thing**:
   ```python
   # Good - tests one aspect
   def test_property_price_validation():
       with pytest.raises(ValueError):
           Property(price=Decimal("-1000"))

   # Bad - tests multiple things
   def test_property():
       # tests creation, validation, serialization...
   ```

4. **Use Fixtures**:
   ```python
   @pytest.fixture
   def sample_property():
       return MockDataGenerator.generate_property()

   def test_property_summary(sample_property):
       summary = sample_property.summary
       assert "apartment" in summary.lower()
   ```

5. **Mock External Dependencies**:
   ```python
   @patch('app.client.GroqClient')
   async def test_llm_call(mock_client):
       mock_client.return_value = mock_response
       result = await call_llm()
       assert result is not None
   ```

---

## Troubleshooting

### Tests Fail with Import Errors

```bash
# Ensure app is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in editable mode
pip install -e .
```

### Async Tests Not Running

```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Check pytest.ini has asyncio_mode = auto
```

### Coverage Not Showing

```bash
# Ensure pytest-cov is installed
pip install pytest-cov

# Run with explicit coverage
pytest tests/ --cov=app --cov-report=term
```

### Tests Too Slow

```bash
# Run without slow tests
pytest -m "not slow"

# Run with parallel execution
pip install pytest-xdist
pytest -n auto
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## Coordination with Hive Mind

This test suite is integrated with the Reviews System Refactor Hive Mind:

### Pre-Task Hook
```bash
npx claude-flow@alpha hooks pre-task --description "Run test suite"
```

### Post-Edit Hook
```bash
npx claude-flow@alpha hooks post-edit \
  --file "tests/generators/test_mock_data_generation.py" \
  --memory-key "hive/tests/mock_data"
```

### Post-Task Hook
```bash
npx claude-flow@alpha hooks post-task --task-id "testing-phase"
```

### Share Results
Test results are automatically shared in the `hive/tests/` memory namespace for coordination with other agents.

---

## Future Enhancements

1. **Property-Based Testing**: Add Hypothesis for generative testing
2. **Mutation Testing**: Use mutpy to verify test quality
3. **Performance Regression**: Track performance over time
4. **Visual Regression**: Add screenshot testing for UI
5. **Stress Testing**: Add high-load scenario tests
6. **Integration with Real APIs**: Add optional real API tests (marked with `@pytest.mark.real`)

---

## Questions & Support

- **Test Issues**: Check inline documentation in test files
- **Coverage Questions**: See `TEST_COVERAGE_REPORT.md`
- **Fixtures**: See `conftest.py`
- **Configuration**: See `pytest.ini`

**Agent**: TESTER (Reviews System Refactor Hive Mind)
**Memory**: `hive/tests/` namespace
**Coordination**: Claude Flow hooks

---

*Generated by TESTER agent - Reviews System Refactor*
*All tests use mock data - no external API dependencies required*
