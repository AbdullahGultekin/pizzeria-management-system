#!/bin/bash
# macOS Test Script for Pizzeria Management System
# This script runs tests and generates a report

echo "========================================"
echo "PIZZERIA MANAGEMENT SYSTEM - macOS TEST"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

python3 --version
echo ""
echo "Running test suite..."
echo ""

# Run test suite
python3 test_suite.py

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "TESTS FAILED - Check test report"
    echo "========================================"
    exit 1
else
    echo ""
    echo "========================================"
    echo "ALL TESTS PASSED"
    echo "========================================"
    exit 0
fi

