@echo off
REM Windows Test Script for Pizzeria Management System
REM This script runs tests and generates a report

echo ========================================
echo PIZZERIA MANAGEMENT SYSTEM - WINDOWS TEST
echo ========================================
echo.

REM Check Python installation
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Running test suite...
echo.

REM Run test suite
python test_suite.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo TESTS FAILED - Check test report
    echo ========================================
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo ALL TESTS PASSED
    echo ========================================
    pause
    exit /b 0
)

