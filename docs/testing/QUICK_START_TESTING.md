# Quick Start - Testing Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
cd /mnt/c/Users/DaviCastroSamora/Documents/SamoraDC/AgenticRealEstateSystem
pip install -r requirements-test.txt
```

### Step 2: Run Tests
```bash
# Run all tests
pytest tests/ -v

# Or run by category
pytest tests/ -m unit -v              # Fast unit tests
pytest tests/ -m integration -v       # Integration tests
```

### Step 3: Check Coverage
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 📊 Test Overview

```
78 Total Tests
├── 19 Orchestration Tests (test_unified_swarm.py)
├── 21 Routing Tests (test_routing.py)
├── 19 Data Manager Tests (test_data_manager.py)
└── 19 Integration Tests (test_full_conversation.py)
```

---

## 🎯 Common Test Commands

### By Category
```bash
pytest tests/ -m unit                 # Unit tests only
pytest tests/ -m integration          # Integration tests only
pytest tests/ -m asyncio              # Async tests only
pytest tests/ -m "unit and asyncio"   # Combined markers
```

### By File
```bash
pytest tests/orchestration/test_unified_swarm.py
pytest tests/agents/test_routing.py
pytest tests/data/test_data_manager.py
pytest tests/integration/test_full_conversation.py
```

### By Test Name
```bash
pytest tests/ -k "test_orchestrator_initialization"
pytest tests/ -k "handoff"
pytest tests/ -k "error"
```

### With Options
```bash
pytest tests/ -v                      # Verbose output
pytest tests/ -s                      # Show print statements
pytest tests/ -x                      # Stop on first failure
pytest tests/ --maxfail=3             # Stop after 3 failures
pytest tests/ -n auto                 # Parallel execution
pytest tests/ --durations=10          # Show 10 slowest tests
```

---

## 📁 Test Structure

```
tests/
├── conftest.py                     # Shared fixtures
│   ├── mock_settings
│   ├── sample_properties
│   ├── sample_appointments
│   ├── agent_context
│   ├── mock_orchestrator
│   └── async helpers
│
├── orchestration/
│   └── test_unified_swarm.py      # 19 orchestration tests
│
├── agents/
│   └── test_routing.py            # 21 routing tests
│
├── data/
│   └── test_data_manager.py       # 19 data tests
│
└── integration/
    └── test_full_conversation.py  # 19 integration tests
```

---

## 🧪 Sample Test Runs

### Quick Validation (2-3 minutes)
```bash
# Run only fast unit tests
pytest tests/ -m unit -v
```

### Full Test Suite (5-10 minutes)
```bash
# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=term
```

### Specific Component Testing
```bash
# Test only orchestration
pytest tests/orchestration/ -v

# Test only routing
pytest tests/agents/ -v

# Test only data layer
pytest tests/data/ -v

# Test only integration
pytest tests/integration/ -v
```

---

## 📊 Expected Output

### Successful Run
```
tests/orchestration/test_unified_swarm.py::TestHybridSwarmOrchestrator::test_orchestrator_initialization PASSED
tests/orchestration/test_unified_swarm.py::TestPydanticAIWrapper::test_wrapper_initialization PASSED
...
================================ 78 passed in 45.23s ================================
```

### Coverage Report
```
Name                                      Stmts   Miss  Cover
-------------------------------------------------------------
app/orchestration/swarm_hybrid.py           245     15    94%
app/agents/hybrid_search.py                 180     12    93%
app/agents/hybrid_property.py               175     14    92%
app/agents/hybrid_scheduling.py             165     18    89%
app/utils/container.py                       80      8    90%
-------------------------------------------------------------
TOTAL                                       845     67    92%
```

---

## 🔧 Troubleshooting

### Issue: "No module named pytest"
```bash
pip install pytest pytest-asyncio
```

### Issue: "Event loop errors on Windows"
Already handled in `conftest.py`:
```python
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

### Issue: "Import errors"
Run from project root:
```bash
cd /path/to/AgenticRealEstateSystem
pytest tests/
```

### Issue: "Slow tests"
Run tests in parallel:
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

---

## 📝 Test Fixtures Available

Use these in your tests:

```python
def test_example(
    mock_settings,              # Mock settings
    sample_properties,          # 3 sample properties
    sample_appointments,        # 2 sample appointments
    agent_context,              # Basic agent context
    agent_context_with_property,  # Context with property
    agent_context_with_search,    # Context with search results
    mock_orchestrator,          # Mocked orchestrator
    mock_search_response,       # Mock search response
    mock_property_response,     # Mock property response
    mock_scheduling_response    # Mock scheduling response
):
    # Your test code here
    pass
```

---

## 🎯 Testing Workflow

### 1. Before Making Changes
```bash
# Ensure all tests pass
pytest tests/ -v
```

### 2. During Development
```bash
# Run related tests
pytest tests/orchestration/ -v -k "your_feature"
```

### 3. After Changes
```bash
# Run full suite with coverage
pytest tests/ -v --cov=app --cov-report=html
```

### 4. Before Committing
```bash
# Run all tests one final time
pytest tests/ -v --maxfail=1
```

---

## 📚 Test Documentation

- **tests/README.md** - Comprehensive testing guide
- **docs/testing/test_results.md** - Detailed results
- **docs/testing/TEST_SUITE_SUMMARY.md** - Overview
- **This File** - Quick start guide

---

## 🎓 Test Examples

### Unit Test
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_initialization(mock_settings):
    """Test agent initializes correctly."""
    agent = MyAgent(mock_settings)
    assert agent is not None
```

### Integration Test
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_flow(mock_orchestrator, sample_properties):
    """Test search to property flow."""
    result = await orchestrator.process_message({
        "messages": [HumanMessage(content="Find apartments")]
    })
    assert result is not None
```

---

## ✅ Quick Checklist

Before running tests:
- [ ] Installed test dependencies
- [ ] In project root directory
- [ ] Python 3.11+ active

To run tests:
- [ ] Run unit tests: `pytest tests/ -m unit -v`
- [ ] Run integration tests: `pytest tests/ -m integration -v`
- [ ] Check coverage: `pytest tests/ --cov=app`

For development:
- [ ] Tests pass before changes
- [ ] Tests pass after changes
- [ ] Coverage maintained >80%
- [ ] New tests added for new features

---

## 🚀 Ready to Test!

You now have everything needed to run the comprehensive test suite. Start with:

```bash
pytest tests/ -v
```

Happy testing! 🎉
