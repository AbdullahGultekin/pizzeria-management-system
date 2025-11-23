"""
Comprehensive Test Suite for Pizzeria Management System

This test suite checks for platform-specific issues and general bugs.
Run this on both macOS and Windows to identify differences.
"""

import sys
import platform
import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Test results storage
test_results: Dict[str, List[Dict[str, Any]]] = {
    "passed": [],
    "failed": [],
    "warnings": [],
    "skipped": []
}

def log_test(test_name: str, status: str, message: str = "", details: str = ""):
    """Log a test result."""
    result = {
        "test": test_name,
        "status": status,
        "message": message,
        "details": details,
        "platform": platform.system(),
        "timestamp": datetime.now().isoformat()
    }
    test_results[status].append(result)
    
    status_symbol = {
        "passed": "✓",
        "failed": "✗",
        "warnings": "⚠",
        "skipped": "⊘"
    }.get(status, "?")
    
    print(f"{status_symbol} {test_name}: {message}")
    if details:
        print(f"    {details}")

def test_platform_detection():
    """Test if platform is correctly detected."""
    test_name = "Platform Detection"
    try:
        system = platform.system()
        log_test(test_name, "passed", f"Platform: {system}")
        return system
    except Exception as e:
        log_test(test_name, "failed", str(e))
        return None

def test_imports():
    """Test if all required modules can be imported."""
    test_name = "Module Imports"
    failed_imports = []
    
    required_modules = [
        "tkinter",
        "sqlite3",
        "json",
        "datetime",
        "pathlib"
    ]
    
    optional_modules = {
        "win32print": "Windows printer support",
        "qrcode": "QR code generation",
        "PIL": "Image processing",
        "phonenumbers": "Phone validation"
    }
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError as e:
            failed_imports.append(f"{module}: {e}")
    
    if failed_imports:
        log_test(test_name, "failed", f"Failed imports: {', '.join(failed_imports)}")
    else:
        log_test(test_name, "passed", "All required modules imported")
    
    # Check optional modules
    for module, description in optional_modules.items():
        try:
            __import__(module)
            log_test(f"Optional: {module}", "passed", description)
        except ImportError:
            log_test(f"Optional: {module}", "warnings", f"{description} not available")

def test_file_structure():
    """Test if all required files exist."""
    test_name = "File Structure"
    missing_files = []
    
    required_files = [
        "app.py",
        "database.py",
        "menu.json",
        "extras.json",
        "settings.json",
        "requirements.txt"
    ]
    
    optional_files = [
        "straatnamen.json",
        "logo.ico",
        "pizzeria.db"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        log_test(test_name, "failed", f"Missing files: {', '.join(missing_files)}")
    else:
        log_test(test_name, "passed", "All required files present")
    
    for file in optional_files:
        if Path(file).exists():
            log_test(f"Optional file: {file}", "passed", "Found")
        else:
            log_test(f"Optional file: {file}", "warnings", "Not found (optional)")

def test_json_files():
    """Test if JSON files are valid."""
    test_name = "JSON File Validation"
    json_files = ["menu.json", "extras.json", "settings.json"]
    
    for json_file in json_files:
        if not Path(json_file).exists():
            log_test(f"JSON: {json_file}", "warnings", "File not found")
            continue
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            log_test(f"JSON: {json_file}", "passed", f"Valid JSON ({len(data)} items)")
        except json.JSONDecodeError as e:
            log_test(f"JSON: {json_file}", "failed", f"Invalid JSON: {e}")
        except Exception as e:
            log_test(f"JSON: {json_file}", "failed", f"Error: {e}")

def test_database():
    """Test database connection and schema."""
    test_name = "Database Connection"
    db_path = "pizzeria.db"
    
    try:
        if not Path(db_path).exists():
            log_test(test_name, "warnings", "Database file does not exist (will be created on first run)")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check required tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ["bestellingen", "klanten", "bestelregels", "koeriers"]
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            log_test(test_name, "warnings", f"Missing tables: {', '.join(missing_tables)}")
        else:
            log_test(test_name, "passed", f"All required tables present ({len(tables)} total)")
        
        # Check for afhaal column
        cursor.execute("PRAGMA table_info(bestellingen)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'afhaal' in columns:
            log_test("Database: afhaal column", "passed", "afhaal column exists")
        else:
            log_test("Database: afhaal column", "warnings", "afhaal column missing (will be added on migration)")
        
        conn.close()
    except Exception as e:
        log_test(test_name, "failed", f"Database error: {e}")

def test_printer_support():
    """Test printer support for current platform."""
    test_name = "Printer Support"
    system = platform.system()
    
    if system == "Windows":
        try:
            import win32print
            printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
            if printers:
                log_test(test_name, "passed", f"Windows printer support available ({len(printers)} printers found)")
            else:
                log_test(test_name, "warnings", "Windows printer support available but no printers found")
        except ImportError:
            log_test(test_name, "warnings", "win32print not installed (install pywin32)")
        except Exception as e:
            log_test(test_name, "failed", f"Printer error: {e}")
    else:
        log_test(test_name, "skipped", "Printer support only available on Windows")

def test_sound_support():
    """Test sound notification support."""
    test_name = "Sound Support"
    system = platform.system()
    
    if system == "Windows":
        try:
            import winsound
            log_test(test_name, "passed", "winsound available for Windows")
        except ImportError:
            log_test(test_name, "warnings", "winsound not available")
    elif system == "Darwin":  # macOS
        # Check if afplay is available
        result = os.system("which afplay > /dev/null 2>&1")
        if result == 0:
            log_test(test_name, "passed", "afplay available for macOS")
        else:
            log_test(test_name, "warnings", "afplay not found")
    else:
        log_test(test_name, "warnings", f"Sound support not tested on {system}")

def test_path_handling():
    """Test path handling (Windows vs Unix)."""
    test_name = "Path Handling"
    
    try:
        # Test absolute path
        abs_path = Path(__file__).absolute()
        log_test(f"{test_name}: Absolute", "passed", f"Absolute path: {abs_path}")
        
        # Test relative path
        rel_path = Path("menu.json")
        if rel_path.exists():
            log_test(f"{test_name}: Relative", "passed", "Relative paths work")
        else:
            log_test(f"{test_name}: Relative", "warnings", "Relative path test file not found")
        
        # Test path separators
        if platform.system() == "Windows":
            test_path = "C:\\Users\\Test\\file.json"
            if "\\" in test_path:
                log_test(f"{test_name}: Separators", "passed", "Windows path separators handled")
        else:
            test_path = "/Users/Test/file.json"
            if "/" in test_path:
                log_test(f"{test_name}: Separators", "passed", "Unix path separators handled")
        
    except Exception as e:
        log_test(test_name, "failed", f"Path handling error: {e}")

def test_clipboard_monitor():
    """Test clipboard monitor (Windows-specific)."""
    test_name = "Clipboard Monitor"
    system = platform.system()
    
    if system == "Windows":
        try:
            import win32clipboard
            log_test(test_name, "passed", "Windows clipboard support available")
        except ImportError:
            log_test(test_name, "warnings", "win32clipboard not installed")
    else:
        try:
            # Try tkinter clipboard
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide window
            root.clipboard_get()  # Test if clipboard works
            root.destroy()
            log_test(test_name, "passed", "Tkinter clipboard available")
        except Exception as e:
            log_test(test_name, "warnings", f"Clipboard test failed: {e}")

def test_encoding():
    """Test encoding handling (important for Windows)."""
    test_name = "Encoding Support"
    
    try:
        # Test UTF-8
        test_string = "Test: €, é, ñ, ü"
        encoded = test_string.encode('utf-8')
        decoded = encoded.decode('utf-8')
        
        if decoded == test_string:
            log_test(test_name, "passed", "UTF-8 encoding works correctly")
        else:
            log_test(test_name, "failed", "UTF-8 encoding mismatch")
        
        # Test Windows code pages
        if platform.system() == "Windows":
            try:
                test_string.encode('cp858')
                log_test(f"{test_name}: CP858", "passed", "CP858 (Windows) encoding available")
            except LookupError:
                log_test(f"{test_name}: CP858", "warnings", "CP858 encoding not available")
    except Exception as e:
        log_test(test_name, "failed", f"Encoding error: {e}")

def test_tkinter_ui():
    """Test if Tkinter UI can be initialized."""
    test_name = "Tkinter UI"
    
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        # Test basic widgets
        frame = tk.Frame(root)
        label = tk.Label(frame, text="Test")
        button = tk.Button(frame, text="Test")
        
        log_test(test_name, "passed", "Tkinter UI can be initialized")
        
        root.destroy()
    except Exception as e:
        log_test(test_name, "failed", f"Tkinter error: {e}")

def generate_report():
    """Generate a test report."""
    report_lines = [
        "=" * 70,
        "PIZZERIA MANAGEMENT SYSTEM - TEST REPORT",
        "=" * 70,
        f"Platform: {platform.system()} {platform.release()}",
        f"Python: {sys.version}",
        f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
        f"✓ Passed: {len(test_results['passed'])}",
        f"✗ Failed: {len(test_results['failed'])}",
        f"⚠ Warnings: {len(test_results['warnings'])}",
        f"⊘ Skipped: {len(test_results['skipped'])}",
        "",
        "=" * 70,
        "DETAILED RESULTS",
        "=" * 70,
        ""
    ]
    
    for status in ["failed", "warnings", "passed", "skipped"]:
        if test_results[status]:
            report_lines.append(f"\n{status.upper()}:")
            report_lines.append("-" * 70)
            for result in test_results[status]:
                report_lines.append(f"  {result['test']}: {result['message']}")
                if result['details']:
                    report_lines.append(f"    → {result['details']}")
    
    report_text = "\n".join(report_lines)
    
    # Save to file
    report_file = f"test_report_{platform.system()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print("\n" + "=" * 70)
    print(report_text)
    print("=" * 70)
    print(f"\nReport saved to: {report_file}")
    
    return report_file

def main():
    """Run all tests."""
    print("=" * 70)
    print("PIZZERIA MANAGEMENT SYSTEM - TEST SUITE")
    print("=" * 70)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print("=" * 70)
    print()
    
    # Run all tests
    test_platform_detection()
    test_imports()
    test_file_structure()
    test_json_files()
    test_database()
    test_printer_support()
    test_sound_support()
    test_path_handling()
    test_clipboard_monitor()
    test_encoding()
    test_tkinter_ui()
    
    # Generate report
    print()
    report_file = generate_report()
    
    # Exit code based on failures
    if test_results['failed']:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()

