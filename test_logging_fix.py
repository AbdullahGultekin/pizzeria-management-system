"""Test logging fix voor EXE vanuit System32"""
import os
import sys
from pathlib import Path

# Simuleer EXE omgeving
sys.frozen = True
sys.executable = r"C:\Users\abdul\Cursor projects\pizzeria-management-system\dist\PizzeriaBestelformulier.exe"

# Simuleer verkeerde working directory (zoals System32)
original_cwd = os.getcwd()
print(f"Original CWD: {original_cwd}")

# Test de logging configuratie
print("\nTesting logging configuration...")
try:
    from logging_config import get_safe_log_directory, setup_logging
    
    log_dir = get_safe_log_directory()
    print(f"Safe log directory: {log_dir}")
    print(f"Is absolute: {log_dir.is_absolute()}")
    print(f"Can write: {log_dir.exists() and os.access(log_dir, os.W_OK)}")
    
    # Test setup_logging
    logger = setup_logging()
    print(f"\nLogger created successfully!")
    print(f"Handlers: {len(logger.handlers)}")
    
    # Test logging
    logger.info("Test log message")
    logger.error("Test error message")
    print("\nLogging test completed successfully!")
    
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
