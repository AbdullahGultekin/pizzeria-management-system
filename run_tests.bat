@echo off
REM Comprehensive Test Runner for Pizzeria Management System (Windows)
REM Usage: run_tests.bat [test_type]
REM Test types: unit, integration, platform, all, coverage

setlocal enabledelayedexpansion

set TEST_TYPE=%1
if "%TEST_TYPE%"=="" set TEST_TYPE=all

echo ========================================
echo Pizzeria Management System - Test Runner
echo ========================================
echo.

if "%TEST_TYPE%"=="unit" goto :unit
if "%TEST_TYPE%"=="integration" goto :integration
if "%TEST_TYPE%"=="platform" goto :platform
if "%TEST_TYPE%"=="coverage" goto :coverage
if "%TEST_TYPE%"=="all" goto :all
goto :usage

:unit
echo Running Unit Tests...
echo.
pytest tests/ -v --tb=short --no-cov
goto :end

:integration
echo Running Integration Tests...
echo.
pytest tests/ -v -m integration --tb=short --no-cov
goto :end

:platform
echo Running Platform Tests...
echo.
python test_suite.py
goto :end

:coverage
echo Running Tests with Coverage...
echo.
pytest tests/ --cov=. --cov-report=term-missing --cov-report=html
echo.
echo Coverage report generated in htmlcov\index.html
echo Note: Exclusions are configured in .coveragerc
goto :end

:all
echo Running All Tests...
echo.
echo Checking Dependencies...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    exit /b 1
) else (
    python --version
)

pytest --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: pytest not found. Install with: pip install pytest pytest-cov
) else (
    echo OK: pytest found
)

if not exist "tests\" (
    echo ERROR: tests\ directory not found
    exit /b 1
) else (
    echo OK: tests\ directory found
)

echo.
echo ----------------------------------------
echo Running Unit Tests...
echo ----------------------------------------
pytest tests/ -v --tb=short --no-cov
if errorlevel 1 (
    echo Unit tests failed
    exit /b 1
)

echo.
echo ----------------------------------------
echo Running Platform Tests...
echo ----------------------------------------
python test_suite.py

echo.
echo ========================================
echo All tests completed!
echo ========================================
goto :end

:usage
echo Unknown test type: %TEST_TYPE%
echo.
echo Usage: run_tests.bat [test_type]
echo.
echo Test types:
echo   unit        - Run unit tests only
echo   integration - Run integration tests only
echo   platform    - Run platform-specific tests
echo   coverage    - Run tests with coverage report
echo   all         - Run all tests (default)
exit /b 1

:end
endlocal

