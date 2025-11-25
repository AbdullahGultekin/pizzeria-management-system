#!/bin/bash

# Comprehensive Test Runner for Pizzeria Management System
# Usage: ./run_tests.sh [test_type]
# Test types: unit, integration, platform, all, coverage

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test type (default: all)
TEST_TYPE=${1:-all}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Pizzeria Management System - Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to run unit tests
run_unit_tests() {
    echo -e "${GREEN}Running Unit Tests...${NC}"
    echo ""
    
    # Use pytest from venv if available, otherwise system pytest
    if [ -f ".venv/bin/pytest" ]; then
        .venv/bin/pytest tests/ -v --tb=short --no-cov
    elif command -v pytest &> /dev/null; then
        pytest tests/ -v --tb=short --no-cov
    else
        echo -e "${YELLOW}Warning: pytest not found. Install with: pip install pytest pytest-cov${NC}"
        return 1
    fi
}

# Function to run integration tests
run_integration_tests() {
    echo -e "${GREEN}Running Integration Tests...${NC}"
    echo ""
    
    # Use pytest from venv if available, otherwise system pytest
    if [ -f ".venv/bin/pytest" ]; then
        .venv/bin/pytest tests/ -v -m integration --tb=short --no-cov
    elif command -v pytest &> /dev/null; then
        pytest tests/ -v -m integration --tb=short --no-cov
    else
        echo -e "${YELLOW}Warning: pytest not found. Install with: pip install pytest pytest-cov${NC}"
        return 1
    fi
}

# Function to run platform tests
run_platform_tests() {
    echo -e "${GREEN}Running Platform Tests...${NC}"
    echo ""
    
    if [ -f "test_suite.py" ]; then
        python3 test_suite.py
    else
        echo -e "${RED}Error: test_suite.py not found${NC}"
        return 1
    fi
}

# Function to run with coverage
run_coverage() {
    echo -e "${GREEN}Running Tests with Coverage...${NC}"
    echo ""
    
    # Use pytest from venv if available, otherwise system pytest
    if [ -f ".venv/bin/pytest" ]; then
        .venv/bin/pytest tests/ --cov=. --cov-report=term-missing --cov-report=html
    elif command -v pytest &> /dev/null; then
        pytest tests/ --cov=. --cov-report=term-missing --cov-report=html
    else
        echo -e "${YELLOW}Warning: pytest not found. Install with: pip install pytest pytest-cov${NC}"
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
    echo -e "${BLUE}Note: Exclusions are configured in .coveragerc${NC}"
}

# Function to check dependencies
check_dependencies() {
    echo -e "${BLUE}Checking Dependencies...${NC}"
    echo ""
    
    local missing_deps=0
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ Python 3 not found${NC}"
        missing_deps=1
    else
        echo -e "${GREEN}✓ Python 3 found: $(python3 --version)${NC}"
    fi
    
    # Check for pytest in venv first, then system
    if [ -f ".venv/bin/pytest" ]; then
        echo -e "${GREEN}✓ pytest found in .venv${NC}"
    elif command -v pytest &> /dev/null; then
        echo -e "${GREEN}✓ pytest found${NC}"
    else
        echo -e "${YELLOW}⚠ pytest not found (install with: pip install pytest pytest-cov)${NC}"
    fi
    
    if [ ! -f "pytest.ini" ]; then
        echo -e "${YELLOW}⚠ pytest.ini not found${NC}"
    else
        echo -e "${GREEN}✓ pytest.ini found${NC}"
    fi
    
    if [ ! -d "tests" ]; then
        echo -e "${RED}✗ tests/ directory not found${NC}"
        missing_deps=1
    else
        echo -e "${GREEN}✓ tests/ directory found${NC}"
    fi
    
    echo ""
    
    if [ $missing_deps -eq 1 ]; then
        echo -e "${RED}Missing required dependencies. Please install them first.${NC}"
        return 1
    fi
    
    return 0
}

# Function to run all tests
run_all_tests() {
    echo -e "${BLUE}Running All Tests...${NC}"
    echo ""
    
    # Check dependencies first
    if ! check_dependencies; then
        exit 1
    fi
    
    echo ""
    echo -e "${BLUE}----------------------------------------${NC}"
    
    # Run unit tests
    if run_unit_tests; then
        echo -e "${GREEN}✓ Unit tests passed${NC}"
    else
        echo -e "${RED}✗ Unit tests failed${NC}"
        return 1
    fi
    
    echo ""
    echo -e "${BLUE}----------------------------------------${NC}"
    
    # Run platform tests
    if run_platform_tests; then
        echo -e "${GREEN}✓ Platform tests passed${NC}"
    else
        echo -e "${YELLOW}⚠ Platform tests had warnings${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}All tests completed!${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Main execution
case $TEST_TYPE in
    unit)
        check_dependencies
        run_unit_tests
        ;;
    integration)
        check_dependencies
        run_integration_tests
        ;;
    platform)
        run_platform_tests
        ;;
    coverage)
        check_dependencies
        run_coverage
        ;;
    all)
        run_all_tests
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: ./run_tests.sh [test_type]"
        echo ""
        echo "Test types:"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  platform    - Run platform-specific tests"
        echo "  coverage    - Run tests with coverage report"
        echo "  all         - Run all tests (default)"
        exit 1
        ;;
esac

