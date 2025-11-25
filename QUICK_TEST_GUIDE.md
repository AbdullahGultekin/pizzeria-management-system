# Quick Test Guide - Pizzeria Management System

## 🚀 Snelle Start

### 1. Basis Tests Uitvoeren

```bash
# Alle tests (unit + platform)
./run_tests.sh

# Alleen unit tests
./run_tests.sh unit

# Met coverage report
./run_tests.sh coverage

# Platform-specifieke tests
./run_tests.sh platform
```

### 2. Handmatige Tests

```bash
# Desktop applicatie starten
python3 app.py  # macOS
python app.py   # Windows

# Test suite uitvoeren
python3 test_suite.py  # macOS
python test_suite.py   # Windows
```

### 3. Web Applicatie Tests

```bash
# Backend starten
cd pizzeria-web/backend
python run.py

# Frontend starten (nieuwe terminal)
cd pizzeria-web/frontend
npm run dev

# Test in browser: http://localhost:3000
```

## 📋 Test Checklist (5 Minuten)

### Desktop Applicatie
- [ ] App start zonder errors
- [ ] Kassa modus werkt
- [ ] Admin modus werkt
- [ ] Bestelling plaatsen werkt
- [ ] Print functionaliteit werkt

### Web Applicatie
- [ ] Login werkt (admin/kassa)
- [ ] Menu wordt geladen
- [ ] Bestellingen kunnen worden geplaatst
- [ ] Admin dashboard werkt
- [ ] Real-time updates werken

## 🔍 Bug Zoeken

### 1. Bekende Probleemgebieden

#### Performance Issues
```bash
# Test koeriers toewijzing performance
# - Selecteer 10 bestellingen
# - Wijs toe aan koerier
# - Moet < 1 seconde duren
```

#### Platform Verschillen
```bash
# Run platform tests op beide OS
python3 test_suite.py  # macOS
python test_suite.py   # Windows

# Vergelijk test reports
```

#### Database Issues
```bash
# Test database operaties
pytest tests/test_database/ -v

# Check database schema
sqlite3 pizzeria.db ".schema"
```

### 2. Common Bugs

#### Bug: App crasht bij start
**Check**:
- Python versie (3.8+)
- Dependencies geïnstalleerd (`pip install -r requirements.txt`)
- Database bestaat
- JSON bestanden zijn geldig

#### Bug: Print werkt niet
**Windows**: Check `win32print` installatie
```bash
pip install pywin32
```

**macOS**: Print preview werkt, geen fysieke printer

#### Bug: Menu laadt niet (Web)
**Check**:
- Backend draait op port 8000
- Database heeft menu items
- API endpoint werkt: `curl http://localhost:8000/api/v1/menu`
- Browser console voor errors

#### Bug: Performance problemen
**Check**:
- Database indexes aanwezig
- Geen N+1 query problemen
- Tab switching is asynchroon
- Koeriers toewijzing is geoptimaliseerd

### 3. Debug Commands

```bash
# Check Python versie
python3 --version

# Check dependencies
pip list | grep -E "pytest|fastapi|react"

# Check database
sqlite3 pizzeria.db "SELECT COUNT(*) FROM bestellingen;"

# Check logs
tail -f app.log
tail -f app_errors.log

# Test API endpoints
curl http://localhost:8000/api/v1/menu
curl http://localhost:8000/api/v1/orders
```

## 🧪 Test Types

### Unit Tests
```bash
# Run alle unit tests
pytest tests/ -v

# Run specifieke test file
pytest tests/test_services/test_customer_service.py -v

# Run met output
pytest tests/ -v -s

# Run alleen failed tests
pytest --lf
```

### Integration Tests
```bash
# Run integration tests
pytest tests/ -v -m integration

# Test API endpoints
pytest tests/test_api/ -v
```

### Coverage Report
```bash
# Generate coverage
pytest --cov=. --cov-report=html

# Open report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

## 📊 Test Resultaten Interpreteren

### Test Suite Output
```
✓ Passed: 15
✗ Failed: 2
⚠ Warnings: 3
⊘ Skipped: 1
```

**Actie**:
- **Failed**: Fix bugs, check test output
- **Warnings**: Optionele features, kan worden genegeerd
- **Skipped**: Platform-specifieke tests (normaal)

### Pytest Output
```
FAILED tests/test_services/test_customer_service.py::test_create_customer
AssertionError: Expected '0123456789', got '0123456788'
```

**Actie**: Check test data, check business logic

## 🐛 Bug Report Template

```markdown
**Platform**: macOS / Windows
**Versie**: 1.0.0
**Severity**: High

**Beschrijving**:
App crasht bij koeriers toewijzing

**Stappen**:
1. Open Admin modus
2. Ga naar Koeriers tab
3. Selecteer 10 bestellingen
4. Wijs toe aan koerier
5. App crasht

**Verwacht**: Toewijzing werkt, geen crash
**Actueel**: App crasht met error

**Error Log**:
[Paste error hier]
```

## ✅ Pre-Release Checklist

- [ ] Alle unit tests passen
- [ ] Platform tests passen op beide OS
- [ ] Manual testing checklist voltooid
- [ ] Code coverage > 70%
- [ ] Geen critical bugs
- [ ] Performance tests binnen limits
- [ ] Security tests passen
- [ ] Documentation up-to-date

## 🔧 Troubleshooting

### Tests Failen
1. Check Python versie
2. Check dependencies: `pip install -r requirements.txt`
3. Check test data
4. Run tests in isolation: `pytest tests/test_file.py::test_function -v`

### Coverage Laag
1. Check welke files niet getest zijn
2. Voeg tests toe voor belangrijke functies
3. Focus op business logic eerst

### Performance Tests Falen
1. Check database indexes
2. Profile slow queries
3. Check voor memory leaks
4. Optimize database queries

## 📚 Meer Informatie

- **Test Strategie**: Zie `TEST_STRATEGY.md`
- **Testing Guide**: Zie `TESTING_GUIDE.md`
- **Test Checklist**: Zie `TEST_CHECKLIST.md`
- **Web Tests**: Zie `pizzeria-web/FRONTEND_TEST_INSTRUCTIONS.md`

## 💡 Tips

1. **Run tests regelmatig**: Bij elke wijziging
2. **Fix bugs direct**: Voorkom accumulatie
3. **Test edge cases**: Lege velden, lange strings, speciale tekens
4. **Test op beide platforms**: Windows en macOS
5. **Document bugs**: Gebruik bug report template
6. **Monitor coverage**: Streef naar 70%+

## 🎯 Quick Wins

1. **Run test suite**: `./run_tests.sh`
2. **Check coverage**: `pytest --cov=. --cov-report=term-missing`
3. **Fix failed tests**: `pytest --lf` (run alleen failed)
4. **Test platform verschillen**: Run op beide OS
5. **Manual test**: Volg `TEST_CHECKLIST.md`


