# CodeRenew Test Infrastructure & Setup

## Overview
Complete setup guide for test infrastructure, database configuration, fixtures, mocking services, and CI/CD integration.

---

## 1. Backend Test Infrastructure

### 1.1 Dependencies Installation

Add to `/backend/requirements.txt`:

```
# Testing Framework
pytest>=7.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
pytest-timeout>=2.2.0
pytest-xdist>=3.5.0

# Test Data & Factories
factory-boy>=3.3.0
faker>=20.0.0

# Database Testing
pytest-postgresql>=5.0.0
sqlalchemy-utils>=0.41.0

# Time Mocking
freezegun>=1.4.0

# HTTP Mocking
responses>=0.23.0
pytest-httpx>=0.26.0
```

**Installation:**
```bash
pip install -r requirements.txt
```

---

### 1.2 Test Database Setup

#### PostgreSQL Test Instance Configuration

**Option 1: Docker (Recommended)**

```bash
# Start PostgreSQL test container
docker run --name coderenew-test-db \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=test_coderenew \
  -p 5433:5432 \
  -d postgres:15
```

**Option 2: pytest-postgresql Plugin**

```python
# conftest.py
import pytest
from pytest_postgresql import factories

db = factories.postgresql_db("postgresql", scope="session")

@pytest.fixture(scope="session")
def test_database_url(db):
    """Provides test database URL"""
    return f"postgresql://postgres:postgres@localhost:5433/test_coderenew"
```

#### Migration Setup

```python
# conftest.py - Session Fixture
from alembic import command
from alembic.config import Config

@pytest.fixture(scope="session", autouse=True)
def apply_migrations(test_database_url):
    """Apply all database migrations before tests"""
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", test_database_url)

    # Upgrade to head
    command.upgrade(alembic_config, "head")

    yield

    # Downgrade (optional, for cleanup)
    # command.downgrade(alembic_config, "base")
```

---

### 1.3 pytest Configuration

**File:** `/backend/pytest.ini`

```ini
[pytest]
# Test discovery
testpaths = backend/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
python_variables = test_*

# Async support
asyncio_mode = auto

# Markers for test categorization
markers =
    critical: Critical path tests (P0)
    high: High priority tests (P1)
    medium: Medium priority tests (P2)
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests (> 1 second)
    database: Tests requiring database
    security: Security-related tests
    auth: Authentication tests

# Timeout configuration
timeout = 300
timeout_method = thread

# Logging
log_cli = false
log_cli_level = INFO
log_level = DEBUG

# Coverage options
addopts =
    --strict-markers
    --strict-config
    --verbose
    -v

# Database fixture
postgresql_processes_count = 1
```

---

### 1.4 Test Database Session Fixture

**File:** `/backend/tests/conftest.py`

```python
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Set environment before imports
os.environ["ALLOWED_ORIGINS"] = '["http://localhost:3000"]'
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["ANTHROPIC_API_KEY"] = "sk-test-123456789"
os.environ["STRIPE_SECRET_KEY"] = "sk_test_123456789"
os.environ["RESEND_API_KEY"] = "test-resend-key"

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from fastapi.testclient import TestClient

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///:memory:"  # Use in-memory for speed
)

@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine"""
    if "sqlite" in TEST_DATABASE_URL:
        # SQLite in-memory
        engine = create_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        # PostgreSQL
        engine = create_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db_engine) -> Session:
    """
    Provides test database session with transaction rollback.
    Each test gets a fresh session that rolls back after completion.
    """
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session):
    """FastAPI test client with database override"""
    return TestClient(app)


@pytest.fixture
def authenticated_client(client: TestClient, db_session: Session):
    """Test client with authenticated user"""
    from app.core.security import get_password_hash
    from app.models.user import User

    # Create test user
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        name="Test User",
        is_verified=True,
        onboarding_completed=True
    )
    db_session.add(user)
    db_session.commit()

    # Create token
    from app.core.security import create_access_token
    token = create_access_token(user_id=user.id)

    # Add to client headers
    client.headers.update({"Authorization": f"Bearer {token}"})
    client.user = user  # Add user reference for tests

    return client


# Import fixtures from submodules
from tests.fixtures.factory import *
from tests.fixtures.mock_services import *
```

---

### 1.5 Factory Boy Factories

**File:** `/backend/tests/fixtures/factory.py`

```python
import factory
from factory.sqlalchemy import SQLAlchemyModelFactory
from faker import Faker
from datetime import datetime, timedelta

from app.models.user import User
from app.models.site import Site
from app.models.scan import Scan, ScanStatus
from app.models.scan_result import ScanResult
from app.core.security import get_password_hash

fake = Faker()


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = None  # Set in fixture

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    hashed_password = factory.LazyFunction(
        lambda: get_password_hash("DefaultPassword123!")
    )
    name = factory.Faker("name")
    company = factory.Faker("company")
    is_verified = True
    onboarding_completed = False
    failed_login_attempts = 0
    locked_until = None

    @classmethod
    def unverified(cls, **kwargs):
        """Create unverified user"""
        return cls.create(is_verified=False, **kwargs)

    @classmethod
    def locked(cls, **kwargs):
        """Create locked user"""
        return cls.create(
            locked_until=datetime.utcnow() + timedelta(minutes=30),
            failed_login_attempts=5,
            **kwargs
        )

    @classmethod
    def with_password(cls, password: str, **kwargs):
        """Create user with specific password"""
        return cls.create(
            hashed_password=get_password_hash(password),
            **kwargs
        )


class SiteFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Site
        sqlalchemy_session = None

    user = factory.SubFactory(UserFactory)
    name = factory.Faker("domain_name")
    url = factory.Faker("url")
    wordpress_version = "6.0"
    theme_name = factory.Faker("word")
    plugin_count = factory.Faker("random_int", min=0, max=50)


class ScanFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Scan
        sqlalchemy_session = None

    user = factory.SubFactory(UserFactory)
    site = factory.SubFactory(SiteFactory, user=factory.SelfAttribute("..user"))
    status = ScanStatus.COMPLETED
    version_from = "5.9"
    version_to = "6.4"

    @classmethod
    def pending(cls, **kwargs):
        """Create pending scan"""
        return cls.create(status=ScanStatus.PENDING, **kwargs)

    @classmethod
    def processing(cls, **kwargs):
        """Create processing scan"""
        return cls.create(status=ScanStatus.PROCESSING, **kwargs)


class ScanResultFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ScanResult
        sqlalchemy_session = None

    scan = factory.SubFactory(ScanFactory)
    issue_type = "deprecated_function"
    severity = "warning"
    function_name = factory.Faker("word")
    description = factory.Faker("sentence")
    solution = factory.Faker("sentence")
    documentation_url = factory.Faker("url")
    line_number = factory.Faker("random_int", min=1, max=1000)

    @classmethod
    def critical(cls, **kwargs):
        """Create critical severity result"""
        return cls.create(severity="critical", **kwargs)

    @classmethod
    def safe_scan(cls, **kwargs):
        """Create scan with no issues"""
        return cls.create(severity="info", **kwargs)
```

---

### 1.6 Mocking Services

**File:** `/backend/tests/fixtures/mock_services.py`

```python
import pytest
from unittest.mock import patch, MagicMock
from anthropic import Anthropic


@pytest.fixture
def mock_claude():
    """Mock Anthropic Claude API"""
    with patch("app.services.claude.client.anthropic.Anthropic") as mock:
        mock_instance = MagicMock(spec=Anthropic)
        mock_instance.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Analysis complete. Found 3 deprecated functions.")]
        )
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_stripe():
    """Mock Stripe API"""
    with patch("stripe.PaymentIntent.create") as mock:
        mock.return_value = {
            "id": "pi_test_" + "x" * 20,
            "client_secret": "pi_test_secret_" + "x" * 20,
            "status": "succeeded",
            "amount": 2999,
            "currency": "usd"
        }
        yield mock


@pytest.fixture
def mock_email():
    """Mock email service"""
    with patch("app.services.email.send_email") as mock:
        mock.return_value = {"MessageId": "test-message-id"}
        yield mock


@pytest.fixture
def mock_file_storage():
    """Mock file storage operations"""
    with patch("app.services.file_storage.save_file") as save_mock:
        with patch("app.services.file_storage.delete_file") as delete_mock:
            save_mock.return_value = "/uploads/test/file.zip"
            yield {"save": save_mock, "delete": delete_mock}
```

---

### 1.7 HTTP Client for FastAPI Testing

**File:** `/backend/tests/conftest.py` (Addition)

```python
@pytest.fixture
def http_client(client):
    """Extended HTTP client with helper methods"""
    class HTTPClient:
        def __init__(self, fastapi_client):
            self.client = fastapi_client

        def post_auth(self, endpoint: str, json=None, headers=None):
            """POST with authentication"""
            if headers is None:
                headers = {}
            if "Authorization" not in headers:
                # Use authenticated client if available
                if hasattr(self.client, "headers"):
                    return self.client.post(endpoint, json=json)
            return self.client.post(endpoint, json=json, headers=headers)

        # Add more helper methods as needed

    return HTTPClient(client)
```

---

## 2. Frontend Test Infrastructure

### 2.1 Node Dependencies

Add to `/frontend/package.json`:

```json
{
  "devDependencies": {
    "vitest": "^1.0.0",
    "vitest-environment-jsdom": "^1.0.0",
    "@testing-library/react": "^14.1.0",
    "@testing-library/user-event": "^14.5.0",
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/dom": "^9.3.4",
    "msw": "^2.0.0",
    "@playwright/test": "^1.40.0",
    "@vitest/ui": "^1.0.0",
    "jsdom": "^23.0.0"
  }
}
```

**Installation:**
```bash
npm install
npx playwright install
```

---

### 2.2 Vitest Configuration

**File:** `/frontend/vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.{test,spec}.{ts,tsx}'],
    exclude: ['node_modules', 'dist', '.idea', '.git', '.cache'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.test.ts',
        '**/*.spec.ts',
        '**/index.ts',
        '**/*.d.ts',
      ],
      lines: 70,
      functions: 70,
      branches: 70,
      statements: 70,
    },
    testTimeout: 10000,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

---

### 2.3 Playwright Configuration

**File:** `/frontend/playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  testMatch: '**/*.spec.ts',

  // Execution
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  timeout: 30 * 1000,
  expect: {
    timeout: 5000,
  },

  // Reporting
  reporter: [
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'junit.xml' }],
  ],

  // Global settings
  use: {
    baseURL: process.env.PLAYWRIGHT_TEST_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
  },

  // Projects (browsers)
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Web server
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },

  // Global setup/teardown
  globalSetup: require.resolve('./tests/e2e/global-setup.ts'),
  globalTeardown: require.resolve('./tests/e2e/global-teardown.ts'),
})
```

---

### 2.4 Test Setup

**File:** `/frontend/tests/setup.ts`

```typescript
import { expect, beforeEach, afterEach, vi } from 'vitest'
import { cleanup } from 'vitest-browser-react'
import '@testing-library/jest-dom/vitest'

// Cleanup after each test
afterEach(() => {
  cleanup()
  localStorage.clear()
  sessionStorage.clear()
  vi.clearAllMocks()
})

// Mock window APIs
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
})) as any

// Setup MSW
import { setupServer } from 'msw/browser'
import { handlers } from './mocks/handlers'

export const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

---

### 2.5 MSW Handlers

**File:** `/frontend/tests/mocks/handlers.ts`

```typescript
import { http, HttpResponse } from 'msw'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export const handlers = [
  // Authentication
  http.post(`${API_BASE}/auth/register`, async ({ request }) => {
    const body = (await request.json()) as any
    return HttpResponse.json(
      {
        access_token: `token_${Date.now()}`,
        user: {
          id: 1,
          email: body.email,
          name: body.name,
          is_verified: false,
        },
      },
      { status: 201 }
    )
  }),

  http.post(`${API_BASE}/auth/login`, async ({ request }) => {
    const body = (await request.json()) as any
    if (body.email === 'error@example.com') {
      return HttpResponse.json(
        { detail: 'Invalid credentials' },
        { status: 401 }
      )
    }
    return HttpResponse.json({
      access_token: `token_${Date.now()}`,
      user: {
        id: 1,
        email: body.email,
        name: 'Test User',
        is_verified: true,
      },
    })
  }),

  // Scans
  http.get(`${API_BASE}/scans`, () => {
    return HttpResponse.json([
      {
        id: 1,
        status: 'completed',
        created_at: new Date().toISOString(),
      },
    ])
  }),

  http.post(`${API_BASE}/scans/upload`, () => {
    return HttpResponse.json(
      { scan_id: Math.floor(Math.random() * 10000) },
      { status: 202 }
    )
  }),
]
```

---

### 2.6 E2E Global Setup

**File:** `/frontend/tests/e2e/global-setup.ts`

```typescript
import { chromium, FullConfig } from '@playwright/test'

async function globalSetup(config: FullConfig) {
  const { baseURL } = config.use

  // Check if server is running
  const browser = await chromium.launch()
  const page = await browser.newPage()

  try {
    await page.goto(baseURL + '/', { waitUntil: 'domcontentloaded' })
  } catch (error) {
    console.error('Failed to connect to server at', baseURL)
    process.exit(1)
  }

  await browser.close()
}

export default globalSetup
```

---

## 3. CI/CD Integration

### 3.1 GitHub Actions Workflow

**File:** `/.github/workflows/tests.yml`

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: test_coderenew
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5433:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt

      - name: Run unit tests
        env:
          TEST_DATABASE_URL: postgresql://postgres:testpass@localhost:5433/test_coderenew
        run: |
          pytest backend/tests/unit -v --cov=app --cov-report=xml --cov-report=term-missing

      - name: Run integration tests
        env:
          TEST_DATABASE_URL: postgresql://postgres:testpass@localhost:5433/test_coderenew
        run: |
          pytest backend/tests/integration -v

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: backend
          name: backend-coverage

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: './frontend/package-lock.json'

      - name: Install dependencies
        run: npm install
        working-directory: ./frontend

      - name: Run unit tests
        run: npm run test:unit -- --coverage
        working-directory: ./frontend

      - name: Run integration tests
        run: npm run test:integration
        working-directory: ./frontend

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/coverage-final.json
          flags: frontend
          name: frontend-coverage

  e2e-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: './frontend/package-lock.json'

      - name: Install dependencies
        run: npm install
        working-directory: ./frontend

      - name: Install Playwright browsers
        run: npx playwright install --with-deps
        working-directory: ./frontend

      - name: Start backend (mock or test)
        run: |
          # Start test backend or use mock API
          npm run dev &
          sleep 5
        working-directory: ./frontend

      - name: Run E2E tests
        run: npm run test:e2e
        working-directory: ./frontend

      - name: Upload Playwright report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/

  quality-gates:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests, e2e-tests]
    if: always()

    steps:
      - name: Check test results
        run: |
          if [ "${{ needs.backend-tests.result }}" = "failure" ]; then
            echo "Backend tests failed"
            exit 1
          fi
          if [ "${{ needs.frontend-tests.result }}" = "failure" ]; then
            echo "Frontend tests failed"
            exit 1
          fi
          if [ "${{ needs.e2e-tests.result }}" = "failure" ]; then
            echo "E2E tests failed"
            exit 1
          fi
          echo "All tests passed"
```

---

## 4. Local Development Setup

### 4.1 Backend Test Commands

```bash
# Run all backend tests
pytest backend/tests -v

# Run specific test file
pytest backend/tests/unit/core/test_security.py -v

# Run tests matching pattern
pytest backend/tests -k "test_login" -v

# Run with coverage
pytest backend/tests --cov=app --cov-report=html

# Run tests in parallel
pytest backend/tests -n auto

# Run with markers
pytest backend/tests -m critical -v
pytest backend/tests -m "critical or high" -v

# Debug mode (pdb on failure)
pytest backend/tests -x -v -s --pdb

# Run with detailed output
pytest backend/tests -vv -s
```

### 4.2 Frontend Test Commands

```bash
# Run all unit tests
npm run test:unit

# Run in watch mode
npm run test:unit:watch

# Run E2E tests
npm run test:e2e

# Run E2E with browser visible
npm run test:e2e:headed

# Run specific test file
npm run test:unit -- LoginForm.test.tsx

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:unit -- --ui

# Debug tests
npm run test:unit -- --inspect-brk
```

---

## 5. Environment Variables

### 5.1 Backend Test Environment

Create `/backend/.env.test`:

```
DATABASE_URL=sqlite:///./test.db
ALLOWED_ORIGINS=["http://localhost:3000"]
SECRET_KEY=test_secret_key_very_secret
ANTHROPIC_API_KEY=sk-test-1234567890
STRIPE_SECRET_KEY=sk_test_1234567890
RESEND_API_KEY=test_resend_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
MAX_FAILED_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION_MINUTES=30
DEBUG=False
```

### 5.2 Frontend Test Environment

Create `/frontend/.env.test`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_STRIPE_KEY=pk_test_123456789
NODE_ENV=test
```

---

## 6. Coverage Reporting

### 6.1 Backend Coverage

```bash
# Generate HTML report
pytest backend/tests --cov=app --cov-report=html
open htmlcov/index.html

# Generate LCOV for IDE integration
pytest backend/tests --cov=app --cov-report=lcov

# Show coverage in terminal with missing lines
pytest backend/tests --cov=app --cov-report=term-missing
```

### 6.2 Frontend Coverage

```bash
# Generate coverage report
npm run test:coverage

# View HTML report
open frontend/coverage/index.html
```

---

## 7. Troubleshooting

### Common Issues

**Database Locked (SQLite)**
```bash
# Solution: Remove lock file
rm test.db-shm
rm test.db-wal
```

**Port Already in Use**
```bash
# Find and kill process on port 3000
lsof -i :3000
kill -9 <PID>
```

**Flaky Tests**
```bash
# Run test multiple times
for i in {1..5}; do pytest tests/unit/test_flaky.py -v; done
```

**Clear Caches**
```bash
# Backend
rm -rf .pytest_cache __pycache__

# Frontend
rm -rf node_modules/.vite
npm cache clean --force
```

---

## 8. Performance Optimization

### Backend

- Use pytest-xdist for parallel execution
- Disable database transactions for unit tests
- Mock external services

### Frontend

- Use Vitest instead of Jest for speed
- Parallelize E2E tests across browsers
- Cache node_modules in CI

---

**Document Version:** 1.0
**Last Updated:** 2024-11-20
**Status:** Ready for Implementation
