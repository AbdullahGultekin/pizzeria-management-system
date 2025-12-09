# Test Strategie - Pizzeria Management System

## Overzicht

Deze document beschrijft een complete teststrategie voor het Pizzeria Management System, inclusief desktop applicatie en web applicatie. Het doel is om bugs en fouten systematisch te vinden en te voorkomen.

## Test Niveaus

### 1. Unit Tests (Pytest)
**Doel**: Test individuele functies en classes in isolatie

**Locatie**: `tests/` directory

**Huidige Coverage**:
- ✅ Repository tests (`test_repositories/`)
- ✅ Service tests (`test_services/`)
- ✅ Validation tests (`test_validation/`)
- ✅ Database tests (`test_database/`)

**Te Testen Componenten**:
```python
# Voorbeelden van unit tests die nodig zijn:

# Business Logic
- CustomerService.create_customer()
- CustomerService.find_customer_by_phone()
- OrderService.calculate_total()
- OrderService.create_order()

# Repositories
- CustomerRepository.create()
- CustomerRepository.find_by_phone()
- OrderRepository.create()
- OrderRepository.get_by_status()

# Validation
- PhoneValidator.validate()
- AddressValidator.validate()
- OrderValidator.validate()

# Utils
- MenuUtils.load_menu()
- PrintUtils.format_receipt()
- AddressUtils.suggest_address()
```

**Run Commands**:
```bash
# Alle tests
pytest

# Met coverage
pytest --cov=. --cov-report=html

# Specifieke test file
pytest tests/test_services/test_customer_service.py

# Met verbose output
pytest -v

# Alleen failed tests
pytest --lf
```

### 2. Integration Tests
**Doel**: Test interactie tussen componenten

**Te Testen Integraties**:
- Database ↔ Repository ↔ Service
- API Endpoints ↔ Services
- WebSocket ↔ Backend
- Frontend ↔ Backend API
- Printer ↔ Order Service

**Voorbeelden**:
```python
# Test complete order flow
def test_order_creation_flow():
    # 1. Create customer
    # 2. Create order
    # 3. Verify in database
    # 4. Check order items
    pass

# Test API endpoint
def test_create_order_endpoint():
    # POST /api/v1/orders
    # Verify response
    # Verify database state
    pass
```

### 3. E2E Tests (End-to-End)
**Doel**: Test complete user flows

**Desktop Applicatie**:
- Kassa flow: Klant zoeken → Product toevoegen → Bestelling plaatsen → Print
- Admin flow: Login → Menu beheren → Rapportage genereren
- Koerier flow: Bestellingen toewijzen → Status updaten

**Web Applicatie**:
- Publieke bestelling: Menu bekijken → Winkelwagen → Checkout → Order plaatsen
- Admin dashboard: Login → Bestellingen beheren → Status updaten
- Kassa interface: Login → Bestellingen plaatsen → Print

**Tools**:
- Desktop: Handmatig + `test_suite.py`
- Web: Playwright / Cypress (toekomstig)

### 4. Platform-Specifieke Tests
**Doel**: Test platform verschillen (Windows vs macOS)

**Tool**: `test_suite.py`

**Te Testen**:
- ✅ Printer support (Windows vs macOS)
- ✅ Geluid notificaties
- ✅ Path handling
- ✅ Encoding (UTF-8 vs CP858)
- ✅ Clipboard monitor
- ✅ File system operaties

**Run**:
```bash
# macOS
python3 test_suite.py

# Windows
python test_suite.py
```

### 5. Performance Tests
**Doel**: Test performance en responsiviteit

**Te Testen**:
- Koeriers toewijzing: < 1 seconde voor 10 bestellingen
- Tab switching: < 0.5 seconden
- Menu laden: < 1 seconde
- Database queries: < 200ms
- API response times: < 200ms

**Tools**:
- Python: `cProfile`, `timeit`
- Browser: Chrome DevTools Performance tab

### 6. Security Tests
**Doel**: Test beveiliging

**Te Testen**:
- ✅ JWT token validatie
- ✅ Password hashing (bcrypt)
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CORS configuratie
- ✅ Rate limiting
- ✅ Input validation
- ✅ Authorization checks

### 7. UI/UX Tests
**Doel**: Test gebruikersinterface

**Desktop**:
- Tkinter widgets renderen correct
- Keyboard shortcuts werken
- Responsive layout
- Error messages zijn duidelijk

**Web**:
- React components renderen
- Material-UI theming
- Responsive design
- Loading states
- Error boundaries

## Test Workflow

### Dagelijkse Tests
```bash
# 1. Run unit tests
pytest

# 2. Run platform tests
python3 test_suite.py  # macOS
python test_suite.py   # Windows

# 3. Check coverage
pytest --cov=. --cov-report=term-missing
```

### Pre-Commit Tests
```bash
# Run quick tests before commit
pytest -x  # Stop bij eerste failure
pytest --lf  # Run alleen failed tests
```

### Pre-Release Tests
1. ✅ Alle unit tests passen
2. ✅ Integration tests passen
3. ✅ Platform tests passen op beide OS
4. ✅ Manual testing checklist voltooid
5. ✅ Performance tests binnen limits
6. ✅ Security tests passen
7. ✅ Code coverage > 70%

## Test Data Management

### Test Database
- Gebruik `temp_db` fixture voor unit tests
- Isolated test database per test run
- Cleanup na elke test

### Test Fixtures
```python
# In conftest.py
@pytest.fixture
def sample_customer_data():
    return {
        "telefoon": "0123456789",
        "naam": "Test Klant",
        ...
    }

@pytest.fixture
def sample_order_items():
    return [...]
```

### Mock Data
- Gebruik factories voor test data
- Seed database met test data voor integration tests
- Cleanup na tests

## Bug Tracking

### Bug Report Template
```markdown
**Platform**: Windows / macOS / Linux
**Versie**: x.y.z
**Severity**: Critical / High / Medium / Low

**Beschrijving**:
[Wat gebeurt er?]

**Stappen om te reproduceren**:
1. ...
2. ...
3. ...

**Verwacht gedrag**:
[Wat zou moeten gebeuren?]

**Actueel gedrag**:
[Wat gebeurt er nu?]

**Screenshots/Logs**:
[Voeg toe indien relevant]

**Test Resultaten**:
[Relevante test output]
```

### Bug Prioriteiten
1. **Critical**: App crasht, data verlies
2. **High**: Belangrijke functionaliteit werkt niet
3. **Medium**: Feature werkt gedeeltelijk
4. **Low**: Cosmetische issues, kleine verbeteringen

## Test Automatisering

### CI/CD Pipeline (Toekomstig)
```yaml
# GitHub Actions example
- Run unit tests
- Run integration tests
- Run platform tests (Windows + macOS)
- Check code coverage
- Run security scans
- Build executables
```

### Test Scheduling
- Unit tests: Bij elke commit
- Integration tests: Bij elke PR
- E2E tests: Dagelijks
- Performance tests: Wekelijks
- Security tests: Maandelijks

## Test Coverage Doelen

### Minimum Coverage
- **Overall**: 70%
- **Critical paths**: 100%
- **Business logic**: 80%
- **Services**: 80%
- **Repositories**: 90%

### Coverage Report
```bash
# Generate HTML report
pytest --cov=. --cov-report=html

# Open report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

## Manual Testing Checklist

Zie `TEST_CHECKLIST.md` voor uitgebreide manual testing checklist.

**Belangrijkste Gebieden**:
- [ ] Applicatie start zonder errors
- [ ] Alle tabs werken
- [ ] Database operaties werken
- [ ] Print functionaliteit werkt
- [ ] Keyboard shortcuts werken
- [ ] Error handling werkt
- [ ] Performance is acceptabel

## Web Applicatie Tests

### Backend API Tests
```bash
cd pizzeria-web/backend

# Test endpoints met curl
curl http://localhost:8000/api/v1/menu
curl http://localhost:8000/api/v1/orders
```

### Frontend Tests
```bash
cd pizzeria-web/frontend

# Run development server
npm run dev

# Test in browser
# - Open http://localhost:3000
# - Check browser console
# - Test alle flows
```

### WebSocket Tests
- Test real-time updates
- Test reconnection logic
- Test multiple clients

## Test Tools & Libraries

### Python
- **pytest**: Test framework
- **pytest-cov**: Coverage
- **pytest-mock**: Mocking
- **pytest-asyncio**: Async tests
- **faker**: Test data generation

### Web
- **Jest**: Frontend unit tests (toekomstig)
- **React Testing Library**: Component tests (toekomstig)
- **Playwright**: E2E tests (toekomstig)
- **Postman/Insomnia**: API testing

### Performance
- **cProfile**: Python profiling
- **Chrome DevTools**: Browser profiling
- **Apache Bench**: Load testing (toekomstig)

## Test Best Practices

### 1. Test Naming
```python
def test_customer_service_create_customer_success():
    """Test successful customer creation"""
    pass

def test_customer_service_create_customer_duplicate_phone():
    """Test customer creation with duplicate phone fails"""
    pass
```

### 2. Test Organization
- One test per scenario
- Clear test names
- Arrange-Act-Assert pattern
- Use fixtures for setup

### 3. Test Independence
- Tests should not depend on each other
- Clean up after tests
- Use isolated test data

### 4. Test Maintainability
- Keep tests simple
- Avoid test duplication
- Use helper functions
- Document complex tests

## Troubleshooting Tests

### Tests Failen
1. Check test output voor errors
2. Check test data
3. Check database state
4. Check dependencies
5. Run tests in isolation

### Performance Issues
1. Profile slow tests
2. Check database queries
3. Check for N+1 problems
4. Use test data efficiently

### Flaky Tests
1. Check for race conditions
2. Check for timing issues
3. Check for external dependencies
4. Add retries if needed

## Test Metrics

### Track
- Test execution time
- Test pass rate
- Code coverage percentage
- Bug detection rate
- Test maintenance time

### Report
- Weekly test summary
- Coverage trends
- Bug trends
- Performance trends

## Conclusie

Een goede teststrategie is essentieel voor kwaliteit en betrouwbaarheid. Deze strategie dekt:

1. ✅ Unit tests voor business logic
2. ✅ Integration tests voor component interactie
3. ✅ E2E tests voor user flows
4. ✅ Platform-specifieke tests
5. ✅ Performance tests
6. ✅ Security tests
7. ✅ Manual testing procedures

**Volgende Stappen**:
1. Verhoog test coverage naar 70%+
2. Voeg meer integration tests toe
3. Automatiseer E2E tests
4. Setup CI/CD pipeline
5. Regelmatig test reviews


