#!/bin/bash
# Run all test suites with comprehensive reporting
# Reviews System Refactor - Test Execution Script

set -e  # Exit on error

echo "=================================="
echo "Reviews System Refactor Test Suite"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo -e "${BLUE}Running Mock Data Generation Tests...${NC}"
pytest tests/generators/test_mock_data_generation.py -v --tb=short
MOCK_RESULT=$?

echo ""
echo -e "${BLUE}Running Groq LLM Integration Tests...${NC}"
pytest tests/llm/test_groq_integration.py -v --tb=short
GROQ_RESULT=$?

echo ""
echo -e "${BLUE}Running Observability Tests...${NC}"
pytest tests/llm/test_observability.py -v --tb=short
OBS_RESULT=$?

echo ""
echo -e "${BLUE}Running End-to-End Integration Tests...${NC}"
pytest tests/integration/test_end_to_end_flow.py -v --tb=short
E2E_RESULT=$?

echo ""
echo "=================================="
echo "Generating Coverage Reports..."
echo "=================================="

# Generate comprehensive coverage report
pytest tests/generators/ tests/llm/ tests/integration/ \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-report=json:coverage.json \
    --tb=short

echo ""
echo "=================================="
echo "Test Results Summary"
echo "=================================="

if [ $MOCK_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Mock Data Generation Tests: PASSED"
else
    echo -e "${RED}✗${NC} Mock Data Generation Tests: FAILED"
fi

if [ $GROQ_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Groq LLM Integration Tests: PASSED"
else
    echo -e "${RED}✗${NC} Groq LLM Integration Tests: FAILED"
fi

if [ $OBS_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Observability Tests: PASSED"
else
    echo -e "${RED}✗${NC} Observability Tests: FAILED"
fi

if [ $E2E_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓${NC} End-to-End Tests: PASSED"
else
    echo -e "${RED}✗${NC} End-to-End Tests: FAILED"
fi

echo ""
echo "=================================="
echo "Coverage Report Location:"
echo "  HTML: htmlcov/index.html"
echo "  JSON: coverage.json"
echo "=================================="

# Check if all tests passed
if [ $MOCK_RESULT -eq 0 ] && [ $GROQ_RESULT -eq 0 ] && [ $OBS_RESULT -eq 0 ] && [ $E2E_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    exit 1
fi
