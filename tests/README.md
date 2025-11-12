# Test Suite for AgenticRealEstateSystem

Comprehensive test suite for the hybrid LangGraph-Swarm + PydanticAI system.

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and configuration
├── orchestration/
│   └── test_unified_swarm.py       # Hybrid swarm orchestration tests
├── agents/
│   └── test_routing.py             # Intent detection and routing tests
├── data/
│   └── test_data_manager.py        # Data mode and service tests
├── integration/
│   └── test_full_conversation.py   # End-to-end conversation tests
└── README.md                        # This file
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests only
pytest -m integration

# Tests with mock data only
pytest -m mock

# Async tests only
pytest -m asyncio

# Skip slow tests
pytest -m "not slow"
```

### Run specific test files
```bash
# Orchestration tests
pytest tests/orchestration/test_unified_swarm.py

# Routing tests
pytest tests/agents/test_routing.py

# Data manager tests
pytest tests/data/test_data_manager.py

# Integration tests
pytest tests/integration/test_full_conversation.py
```

### Run with coverage
```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run in parallel
```bash
# Use multiple CPU cores
pytest -n auto
```

## Test Markers

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Integration tests with multiple components
- `@pytest.mark.asyncio` - Asynchronous tests
- `@pytest.mark.slow` - Slow running tests (>5 seconds)
- `@pytest.mark.mock` - Tests using mock data
- `@pytest.mark.real` - Tests requiring real API connections (skipped by default)

## Test Fixtures

Available in `conftest.py`:

- `mock_settings` - Mock configuration settings
- `sample_properties` - Sample property data
- `sample_appointments` - Sample appointment data
- `agent_context` - Basic agent context
- `agent_context_with_property` - Context with property data
- `agent_context_with_search` - Context with search results
- `mock_orchestrator` - Mocked hybrid swarm orchestrator
- `mock_search_response` - Mock search agent response
- `mock_property_response` - Mock property agent response
- `mock_scheduling_response` - Mock scheduling agent response

## Writing Tests

### Unit Test Example
```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_agent_initialization(mock_settings):
    """Test that agent initializes correctly."""
    agent = MyAgent(mock_settings)
    assert agent is not None
```

### Integration Test Example
```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_search_to_property_flow(mock_orchestrator):
    """Test complete search to property flow."""
    # Search
    search_result = await orchestrator.process_message(search_msg)
    
    # Get property details
    property_result = await orchestrator.process_message(property_msg)
    
    assert property_result is not None
```

## Coverage Goals

- Overall coverage: >80%
- Unit tests: >85%
- Integration tests: >75%
- Critical paths: >90%

## Test Data

All test data is defined in `conftest.py` fixtures:

- **Properties**: 3 sample properties with different types
- **Appointments**: 2 sample appointments with confirmed status
- **Contexts**: Various agent contexts for different scenarios

## Continuous Integration

Tests run automatically on:
- Pull requests
- Push to main branch
- Nightly builds

## Debugging Tests

### Verbose output
```bash
pytest -vv
```

### Show print statements
```bash
pytest -s
```

### Run specific test
```bash
pytest tests/orchestration/test_unified_swarm.py::TestHybridSwarmOrchestrator::test_orchestrator_initialization
```

### Debug with pdb
```bash
pytest --pdb
```

## Common Issues

### AsyncIO Event Loop Errors
If you see event loop errors on Windows, ensure `conftest.py` has:
```python
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

### Import Errors
Make sure you're running tests from the project root:
```bash
cd /path/to/AgenticRealEstateSystem
pytest
```

### Mock API Keys
Tests use mock API keys. For real API tests, use:
```bash
pytest -m real --api-key=YOUR_KEY
```

## Contributing

When adding new tests:
1. Add appropriate markers
2. Use fixtures from conftest.py
3. Follow existing naming conventions
4. Include docstrings
5. Test both success and error cases
6. Maintain >80% coverage
