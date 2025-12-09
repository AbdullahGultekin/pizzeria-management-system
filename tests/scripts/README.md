# Test Scripts

Deze map bevat test scripts en test rapporten.

## Bestanden

- `test_suite.py` - Hoofd test suite
- `test_macos.sh` - Test script voor macOS
- `test_windows.bat` - Test script voor Windows
- `run_tests.sh` - Test runner voor Unix/Linux
- `run_tests.bat` - Test runner voor Windows
- `test_report_*.txt` - Test rapporten

## Gebruik

### macOS/Linux:
```bash
./tests/scripts/run_tests.sh
```

### Windows:
```cmd
tests\scripts\run_tests.bat
```

## Opmerking

De eigenlijke test code staat in `/tests/` (unit tests, integration tests, etc.)

