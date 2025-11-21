# CodeRenew Comprehensive Testing Strategy

## Executive Summary

CodeRenew is a WordPress compatibility scanner SaaS application with critical security features, payment processing, and AI-powered analysis. This document outlines a comprehensive testing strategy to achieve production-grade quality across the full stack (FastAPI backend, Next.js frontend).

**Current State:** Limited test coverage (~5% of codebase). Only WordPress analyzer and Claude tools have unit tests. No integration, E2E, or frontend tests exist.

**Target Coverage:** 80%+ backend, 70%+ frontend by Phase 1 completion.

**Risk Level:** HIGH - Security features (authentication, rate limiting, account lockout), payment processing, and user workflows are untested.

---

## 1. Testing Philosophy & Principles

### Core Philosophy
- **Security First:** Test all authentication, authorization, and account protection mechanisms
- **User-Centric:** Test complete user workflows, not just isolated functions
- **Reliability:** Prevent defects from reaching production through comprehensive coverage
- **Maintainability:** Organize tests logically with clear dependencies and fixtures
- **Performance:** Fast feedback loop (unit tests <2min, integration <5min, E2E <10min)

### Quality Gates
- All new code requires tests before merge
- Minimum 80% coverage for modified files
- No flaky tests allowed (run 3x consecutively)
- Critical security paths require integration + E2E tests
- Performance regression monitoring in CI/CD

---

## 2. Test Pyramid Strategy

### Distribution Target
```
Layer              Coverage    Execution Time    Tools
─────────────────────────────────────────────────────────
Unit Tests         60%         ~2 min            pytest + plugins
Integration Tests  25%         ~5 min            pytest + real DB
E2E Tests          15%         ~10 min           Playwright
─────────────────────────────────────────────────────────
TOTAL              100%        ~17 min           pytest + Node.js
```

### Test Types Breakdown

#### Unit Tests (60%)
- Individual functions and methods
- No external dependencies (all mocked)
- Fast execution (< 100ms each)
- Database queries: None (mocked)
- External API calls: All mocked
- Examples:
  - Password hashing verification
  - Email validation
  - Token generation/validation
  - Data transformation functions
  - Rate limiter configuration
  - Pydantic schema validation

#### Integration Tests (25%)
- API endpoint workflows
- Real database operations
- External services mocked (Claude, Stripe, Email)
- Middleware chain execution
- Fast execution (< 1s each)
- Database state isolated (transaction rollback)
- Examples:
  - Register → Verify → Login workflow
  - File upload → Scan processing → Results retrieval
  - Rate limiting enforcement
  - Account lockout mechanism
  - Payment intent creation

#### E2E Tests (15%)
- Complete user journeys through browser
- Real API calls (test environment)
- Real database (test instance)
- Slow execution (< 30s each)
- Full authentication flow
- Visual regression (optional)
- Examples:
  - Complete registration to first scan
  - Payment flow with webhook handling
  - Password reset with email link
  - Account recovery after lockout

---

## 3. Backend Testing Strategy

### 3.1 Testing Framework: pytest

**Why pytest:**
- Already in requirements.txt
- Mature, widely-used framework (94.8 benchmark score)
- Excellent fixture system for test data management
- Native async support (pytest-asyncio)
- Rich plugin ecosystem
- Clear, Pythonic syntax

**Essential pytest plugins:**
```
pytest>=7.0
pytest-asyncio>=0.21.0          # Async function testing
pytest-cov>=4.1.0               # Coverage reporting
pytest-mock>=3.12.0             # Enhanced mocking
factory-boy>=3.3.0              # Test data factories
faker>=20.0.0                   # Random test data
freezegun>=1.4.0                # Time mocking
pytest-postgresql>=5.0          # PostgreSQL test fixtures
pytest-timeout>=2.2.0           # Prevent hanging tests
pytest-xdist>=3.5.0             # Parallel execution
httpx>=0.26.0                   # (Already in requirements)
```

### 3.2 Backend Module Test Plan

#### 3.2.1 Authentication Module (Priority: CRITICAL)
**File:** `/backend/app/api/v1/endpoints/auth.py`

**Tests to implement:**
- User registration (success, validation errors, duplicate email, rate limiting)
- User login (success, wrong password, non-existent user, locked account)
- Token generation/validation (JWT structure, expiration, tampering)
- Password reset flow (token generation, expiration, single-use enforcement)
- Account lockout (max attempts, duration, automatic unlock)
- Email verification (token creation, validation, re-send)
- Rate limiting per endpoint (register: 5/hour, login: 10/hour, reset: 3/hour)

**Test file:** `/backend/tests/unit/core/test_security.py`
**Test file:** `/backend/tests/integration/test_auth_flows.py`

#### 3.2.2 Security & Rate Limiting (Priority: CRITICAL)
**Files:**
- `/backend/app/core/security.py`
- `/backend/app/core/rate_limiting.py`

**Tests to implement:**
- Password hashing: bcrypt verification, salt generation
- Password validation: length, complexity, blacklist
- Rate limiting per IP/user ID
- Account lockout: increment counter, lock account, reset on successful login
- CORS configuration verification
- JWT token expiration and refresh

**Test files:**
- `/backend/tests/unit/core/test_security.py`
- `/backend/tests/unit/core/test_rate_limiting.py`

#### 3.2.3 Database Models (Priority: HIGH)
**Files:**
- `/backend/app/models/user.py`
- `/backend/app/models/site.py`
- `/backend/app/models/scan.py`
- `/backend/app/models/scan_result.py`
- `/backend/app/models/order.py`

**Tests to implement:**
- Model instantiation with required/optional fields
- Field validation and constraints
- Relationships (User → Sites, User → Scans)
- Cascade delete behavior
- Timestamp handling (created_at, updated_at)
- Unique constraints (email)
- Index verification

**Test file:** `/backend/tests/unit/models/`

#### 3.2.4 API Endpoints (Priority: HIGH)
**Files:**
- `/backend/app/api/v1/endpoints/auth.py`
- `/backend/app/api/v1/endpoints/scans.py`
- `/backend/app/api/v1/endpoints/sites.py`
- `/backend/app/api/v1/endpoints/orders.py`
- `/backend/app/api/v1/endpoints/health.py`

**Tests to implement:**
- Request validation (required fields, type validation)
- Response schema compliance
- Status codes (200, 201, 400, 401, 403, 404, 422, 429, 500)
- Authentication headers required
- Authorization (users can only access own data)
- Error message clarity
- Pagination (if applicable)

**Test files:** `/backend/tests/integration/test_*_endpoints.py`

#### 3.2.5 Schemas & Validation (Priority: HIGH)
**Files:** `/backend/app/schemas/*.py`

**Tests to implement:**
- Valid data passes validation
- Invalid data rejected with clear errors
- Type coercion working correctly
- Optional vs required fields
- Password confirmation matching
- Email format validation
- Enum values validation

**Test file:** `/backend/tests/unit/schemas/test_*.py`

#### 3.2.6 Service Layer (Priority: MEDIUM)
**Files:**
- `/backend/app/services/wordpress/scanner.py`
- `/backend/app/services/wordpress/analyzer.py` (existing - expand)
- `/backend/app/services/claude/client.py`
- `/backend/app/services/email.py`

**Tests to implement:**
- WordPress scanner file processing
- Claude API integration (mocked)
- Error handling and retries
- Email sending with proper recipients
- Token estimation accuracy
- Scan status transitions
- Result parsing and validation

**Test files:**
- `/backend/tests/unit/services/wordpress/` (expand existing)
- `/backend/tests/unit/services/claude/test_client.py`
- `/backend/tests/unit/services/test_email.py`
- `/backend/tests/integration/test_scan_processing.py`

#### 3.2.7 Middleware & Dependencies (Priority: HIGH)
**Files:**
- `/backend/app/api/dependencies.py`
- Rate limiting middleware
- CORS middleware
- Error handling middleware

**Tests to implement:**
- JWT extraction from headers
- Current user identification
- 401 responses for missing auth
- Middleware execution order
- Error formatting
- Rate limiting response codes

**Test file:** `/backend/tests/integration/test_middleware.py`

---

## 4. Frontend Testing Strategy

### 4.1 Testing Framework: Vitest + Testing Library

**Why Vitest over Jest:**
- Vite-native (faster, native ESM)
- Better Next.js 14+ integration
- Lower memory overhead
- Jest compatibility (easier migration)
- Benchmark score: 93.5/100
- 1200+ code examples in Context7

**Frontend testing stack:**
```json
{
  "devDependencies": {
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.1.0",
    "@testing-library/user-event": "^14.5.0",
    "@testing-library/jest-dom": "^6.1.5",
    "msw": "^2.0.0",
    "@playwright/test": "^1.40.0",
    "vitest-environment-jsdom": "^1.0.0"
  }
}
```

### 4.2 Frontend Component Test Plan

#### 4.2.1 Authentication Components (Priority: CRITICAL)
**Files:**
- `/frontend/src/components/auth/ProtectedRoute.tsx`
- `/frontend/src/app/auth/login/page.tsx`
- `/frontend/src/app/auth/register/page.tsx`
- `/frontend/src/app/auth/forgot-password/page.tsx`
- `/frontend/src/app/auth/reset-password/page.tsx`

**Tests to implement:**
- **ProtectedRoute:**
  - Allows authenticated users
  - Redirects unauthenticated users
  - Preserves redirect location

- **Login Page:**
  - Form renders correctly
  - Input validation (empty fields)
  - Password visibility toggle
  - Submit button disabled during loading
  - Error messages display
  - Successful login redirects to dashboard
  - Links to register and forgot password

- **Register Page:**
  - Form renders with all fields
  - Email validation
  - Password strength indicator
  - Confirm password matching
  - Terms acceptance required
  - Successful registration auto-logs in
  - Duplicate email error

- **Password Reset Pages:**
  - Request form with email
  - Reset form with token validation
  - Success message after reset
  - Invalid token error handling
  - Rate limit feedback

**Test files:** `/frontend/tests/unit/components/auth/*.test.tsx`

#### 4.2.2 Form Components (Priority: HIGH)
**Files:**
- `/frontend/src/components/forms/OnboardingForm.tsx`
- `/frontend/src/components/forms/PasswordChangeForm.tsx`
- `/frontend/src/components/forms/ProfileForm.tsx`

**Tests to implement:**
- **OnboardingForm:**
  - All fields render
  - Multi-step navigation works
  - Validation at each step
  - Data persistence across steps
  - Success submission
  - Error handling

- **PasswordChangeForm:**
  - Current password validation
  - New password strength
  - Confirm password matching
  - Success confirmation
  - Error messages

- **ProfileForm:**
  - Field pre-population
  - Submission updates user
  - File upload preview
  - Error recovery

**Test files:** `/frontend/tests/unit/components/forms/*.test.tsx`

#### 4.2.3 Dashboard Components (Priority: HIGH)
**Files:**
- `/frontend/src/app/dashboard/page.tsx`
- `/frontend/src/components/layouts/DashboardLayout.tsx`

**Tests to implement:**
- Dashboard renders after login
- Scan list displays
- Scan upload functionality
- Results display
- Navigation between sections
- User menu/logout
- Responsive layout

**Test files:** `/frontend/tests/unit/components/layouts/*.test.tsx`

#### 4.2.4 API Integration (Priority: HIGH)
**Files:** `/frontend/src/lib/api/`

**Tests to implement:**
- Auth API calls (login, register, logout)
- Scan API calls (upload, list, get results)
- Token management (store, retrieve, refresh)
- Error handling (401, 403, 500)
- Request headers (Authorization)
- Retry logic

**Test files:** `/frontend/tests/unit/lib/api.test.ts`

---

## 5. Critical E2E Test Scenarios

### 5.1 User Registration & Onboarding (CRITICAL)
**Scenario ID:** E2E-001
**Priority:** P0
**Browsers:** Chrome, Firefox, Safari

**Steps:**
1. Navigate to registration page
2. Fill form with valid data
3. Submit form
4. Verify auto-login and redirect to onboarding
5. Complete onboarding questionnaire
6. Verify redirect to dashboard
7. Verify user data in profile

**Expected Results:**
- User created in database
- Auto-login token set
- Onboarding state updated
- Dashboard accessible
- Profile shows correct user data

**Acceptance Criteria:**
- Execution time < 15 seconds
- No console errors
- Responsive on mobile viewport

### 5.2 WordPress Scan Upload & Processing (CRITICAL)
**Scenario ID:** E2E-002
**Priority:** P0

**Steps:**
1. Login as existing user
2. Navigate to scan page
3. Upload WordPress theme/plugin ZIP file
4. Monitor processing status (polling)
5. Wait for completion
6. View detailed results
7. Download report (if available)

**Expected Results:**
- File uploaded successfully
- Scan record created
- Processing starts automatically
- Results populated
- Issues displayed with details

**Acceptance Criteria:**
- Upload shows progress
- Status updates in real-time
- Results load within 30 seconds
- Export functionality works

### 5.3 Payment Flow with Stripe (CRITICAL)
**Scenario ID:** E2E-003
**Priority:** P0

**Steps:**
1. Login as user
2. Navigate to pricing/upgrade
3. Select plan
4. Initiate payment
5. Complete Stripe payment (test card)
6. Verify webhook processing
7. Confirm subscription activated
8. Verify premium features unlocked

**Expected Results:**
- Payment intent created
- Stripe checkout loads
- Payment succeeds
- Webhook updates order
- Subscription active in database
- User sees premium features

**Acceptance Criteria:**
- Payment completes < 10 seconds
- Webhook processed within 5 seconds
- Features available immediately
- Confirmation email sent

### 5.4 Account Lockout & Recovery (CRITICAL)
**Scenario ID:** E2E-004
**Priority:** P0

**Steps:**
1. Attempt login 5 times with wrong password
2. Verify account locked message
3. Initiate password reset
4. Complete reset flow
5. Login with new password
6. Verify account unlocked

**Expected Results:**
- Failed attempts counted
- Account locked after 5 attempts
- Reset token sent
- Password reset succeeds
- Login works with new password
- Account no longer locked

**Acceptance Criteria:**
- Lockout message is clear (not "invalid password")
- Reset email arrives < 5 seconds
- New password works immediately

### 5.5 Password Reset Flow (HIGH)
**Scenario ID:** E2E-005
**Priority:** P1

**Steps:**
1. Request password reset
2. Check reset email
3. Click reset link
4. Enter new password
5. Login with new password
6. Try reset link again (should fail)
7. Try with expired token (should fail)

**Expected Results:**
- Reset token sent
- Link is valid
- Password updated
- Old password no longer works
- Token single-use
- Expiration enforced

**Acceptance Criteria:**
- Email arrives < 5 seconds
- Reset link works 24 hours
- Token cannot be reused

---

## 6. Test Data & Fixtures Strategy

### 6.1 Factory Boy Factories

**Location:** `/backend/tests/fixtures/factory.py`

```python
class UserFactory:
    """Factory for test users"""
    - normal_user() - verified, not locked
    - unverified_user() - pending verification
    - locked_user() - account locked
    - admin_user() - elevated privileges
    - with_password(pwd) - custom password

class SiteFactory:
    """Factory for test sites"""
    - wordpress_site() - WordPress installation
    - with_version(from, to) - custom versions
    - with_plugins(count) - N plugins

class ScanFactory:
    """Factory for test scans"""
    - pending_scan() - not yet processed
    - processing_scan() - in progress
    - completed_scan() - with results
    - with_status(status) - custom status

class ScanResultFactory:
    """Factory for scan results"""
    - with_issues(count, severity) - custom issues
    - safe_scan() - no issues
    - critical_scan() - with critical issues
```

### 6.2 Test File Fixtures

**Location:** `/backend/tests/fixtures/`

```
test_files/
├── wordpress_themes/
│   ├── old_theme.zip        # WordPress 5.0 theme
│   ├── new_theme.zip        # WordPress 6.0 theme
│   └── vulnerable_theme.zip # With deprecated functions
├── sample_code/
│   ├── deprecated_functions.php
│   ├── security_issues.php
│   ├── safe_code.php
│   └── wordpress_versions.json
└── responses/
    ├── claude_analysis.json  # Mock Claude responses
    └── stripe_webhook.json   # Mock Stripe webhooks
```

### 6.3 Test Database Setup

**Approach:** Transaction rollback for test isolation

```python
# conftest.py fixture
@pytest.fixture
def db_session(db):
    """Transactional database fixture"""
    transaction = db.begin_nested()
    yield db
    transaction.rollback()
```

**Advantages:**
- Fast (no truncate/cleanup)
- Atomic operations
- Foreign key constraints enforced
- Connection pooling disabled

### 6.4 Mocking Strategy

#### Claude API Mocking
```python
@pytest.fixture
def mock_claude():
    with patch('anthropic.Anthropic') as mock:
        mock.return_value.messages.create.return_value = {
            'content': [{'text': 'Analysis results...'}]
        }
        yield mock
```

#### Stripe Mocking
```python
# Use Stripe test mode keys + stripe-mock library
@pytest.fixture
def mock_stripe():
    with patch('stripe.PaymentIntent.create') as mock:
        mock.return_value = {
            'id': 'pi_test_123',
            'status': 'succeeded',
            'client_secret': 'secret'
        }
        yield mock
```

#### Email Mocking
```python
@pytest.fixture
def mock_email():
    with patch('app.services.email.send_email') as mock:
        yield mock
```

#### MSW for Frontend API Mocking
```typescript
// tests/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.post('/api/v1/auth/login', async () => {
    return HttpResponse.json({
      access_token: 'test_token',
      user: { id: 1, email: 'test@example.com' }
    })
  }),
  // ... more handlers
]
```

---

## 7. CI/CD Integration

### 7.1 Test Execution Pipeline

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest backend/tests/unit --cov=app --cov-report=xml
      - run: pytest backend/tests/integration
      - uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run test:unit
      - run: npm run test:integration
      - uses: codecov/codecov-action@v3

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npx playwright install
      - run: npm run test:e2e
```

### 7.2 Quality Gates

- [ ] Tests pass on all pushes
- [ ] Coverage > 80% for modified files
- [ ] No flaky tests (run 3x)
- [ ] Performance: unit < 2min, integration < 5min, E2E < 10min
- [ ] All critical security paths tested
- [ ] Blocking on PR merge if tests fail

---

## 8. Test Metrics & Reporting

### 8.1 Coverage Targets

| Module              | Unit | Integration | E2E | Total |
|---------------------|------|-------------|-----|-------|
| Authentication      | 90%  | 85%         | 80% | 85%   |
| Security Features   | 90%  | 80%         | -   | 90%   |
| API Endpoints       | 80%  | 85%         | 75% | 80%   |
| Database Models     | 85%  | -           | -   | 85%   |
| Services            | 75%  | 80%         | 70% | 75%   |
| Frontend Components | -    | -           | 70% | 70%   |
| **Overall**         | 60%  | 25%         | 15% | 80%   |

### 8.2 Reporting

**Coverage Reports:**
- HTML: `htmlcov/index.html`
- LCOV: `coverage.lcov` (IDE integration)
- XML: `coverage.xml` (CI/CD parsing)
- Trends: Tracked weekly

**Performance Reports:**
- Test execution time by module
- Slowest tests highlighted
- Flaky test detection

**Quality Dashboard:**
- Coverage trend
- Test count by type
- Flakiness ratio
- Build time trend

---

## 9. Test Organization & File Structure

```
backend/
├── tests/
│   ├── conftest.py                          # Shared fixtures
│   ├── pytest.ini                           # pytest configuration
│   ├── fixtures/
│   │   ├── factory.py                       # Factory Boy factories
│   │   ├── test_files.py                    # File fixtures
│   │   └── test_data.py                     # Static test data
│   ├── unit/
│   │   ├── core/
│   │   │   ├── test_security.py
│   │   │   ├── test_rate_limiting.py
│   │   │   └── test_config.py
│   │   ├── models/
│   │   │   ├── test_user.py
│   │   │   ├── test_site.py
│   │   │   ├── test_scan.py
│   │   │   └── test_scan_result.py
│   │   ├── schemas/
│   │   │   ├── test_user_schemas.py
│   │   │   └── test_scan_schemas.py
│   │   └── services/
│   │       ├── wordpress/
│   │       │   ├── test_analyzer.py         # Existing - expand
│   │       │   ├── test_scanner.py
│   │       │   └── test_token_optimizer.py
│   │       ├── claude/
│   │       │   ├── test_client.py
│   │       │   └── test_validation_tools.py # Existing - update
│   │       └── test_email.py
│   ├── integration/
│   │   ├── test_auth_flows.py
│   │   ├── test_scan_workflows.py
│   │   ├── test_payment_flows.py
│   │   ├── test_database_operations.py
│   │   ├── test_middleware.py
│   │   ├── test_rate_limiting.py
│   │   └── test_account_lockout.py
│   └── e2e/
│       ├── conftest.py                      # E2E-specific fixtures
│       ├── test_registration_to_scan.py
│       ├── test_payment_flow.py
│       ├── test_password_reset.py
│       └── test_account_security.py

frontend/
├── tests/
│   ├── vitest.config.ts
│   ├── setup.ts                             # Test environment setup
│   ├── mocks/
│   │   ├── handlers.ts                      # MSW handlers
│   │   └── data.ts                          # Mock data
│   ├── unit/
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.test.tsx
│   │   │   │   ├── RegisterForm.test.tsx
│   │   │   │   └── ProtectedRoute.test.tsx
│   │   │   ├── forms/
│   │   │   │   ├── OnboardingForm.test.tsx
│   │   │   │   ├── PasswordChangeForm.test.tsx
│   │   │   │   └── ProfileForm.test.tsx
│   │   │   └── layouts/
│   │   │       └── DashboardLayout.test.tsx
│   │   └── lib/
│   │       ├── api.test.ts
│   │       └── hooks.test.ts
│   ├── integration/
│   │   ├── auth.test.tsx
│   │   ├── dashboard.test.tsx
│   │   ├── scan-workflow.test.tsx
│   │   └── forms.test.tsx
│   └── e2e/
│       ├── playwright.config.ts
│       ├── auth.spec.ts
│       ├── scan.spec.ts
│       ├── payment.spec.ts
│       └── password-reset.spec.ts
```

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up pytest + plugins
- [ ] Create test fixtures and factories
- [ ] Write unit tests for security module
- [ ] Write integration tests for auth flow
- [ ] Achieve 70% backend test coverage

### Phase 2: Comprehensive Backend (Weeks 3-4)
- [ ] API endpoint unit tests
- [ ] Database model tests
- [ ] Service layer tests
- [ ] Middleware tests
- [ ] Achieve 80%+ backend coverage

### Phase 3: Frontend & E2E (Weeks 5-6)
- [ ] Set up Vitest + Playwright
- [ ] Component unit tests
- [ ] Frontend integration tests
- [ ] E2E critical workflows
- [ ] Achieve 70%+ frontend coverage

### Phase 4: CI/CD & Maintenance (Week 7)
- [ ] Configure GitHub Actions
- [ ] Coverage reporting
- [ ] Performance monitoring
- [ ] Documentation and training

---

## 11. Best Practices & Guidelines

### Test Naming
```python
# Format: test_{functionality}_{scenario}_{expected_result}
def test_login_with_valid_credentials_returns_token():
    # Test body
    pass

def test_register_with_duplicate_email_returns_400():
    # Test body
    pass
```

### Test Structure (Arrange-Act-Assert)
```python
def test_user_lockout_after_failed_attempts():
    # ARRANGE - Set up test data
    user = UserFactory.create(email='test@example.com')

    # ACT - Perform the action
    for i in range(5):
        login_endpoint('/login', user.email, 'wrong_password')

    # ASSERT - Verify the result
    assert user.locked_until is not None
    assert user.failed_login_attempts == 5
```

### Fixture Organization
- Fixtures in conftest.py by scope (session, module, function)
- Factory fixtures for creating test data
- Parametrized fixtures for testing multiple scenarios
- Clear fixture dependencies documented

### Mocking Strategy
- Mock external services (Claude, Stripe, Email)
- Never mock what you're testing
- Use real database for integration tests
- MSW for frontend API testing
- Verify mock calls, not just return values

### Performance Guidelines
- Unit tests: < 100ms each
- Integration tests: < 1s each
- E2E tests: < 30s each
- Total suite: < 17 minutes
- Parallel execution for unit/integration tests

---

## 12. Common Testing Patterns

### Testing Async Functions
```python
@pytest.mark.asyncio
async def test_async_scan_processing():
    result = await process_scan(scan_id)
    assert result['status'] == 'completed'
```

### Testing Database Transactions
```python
def test_cascade_delete_removes_related_items(db_session):
    user = UserFactory.create()
    site = SiteFactory.create(user=user)

    db_session.delete(user)
    db_session.commit()

    assert db_session.query(Site).filter_by(user_id=user.id).count() == 0
```

### Testing Time-Based Logic
```python
@freeze_time("2024-01-01 12:00:00")
def test_token_expires_after_one_hour():
    token = create_access_token(user_id=1, expires_delta=timedelta(hours=1))

    with freeze_time("2024-01-01 13:00:01"):
        assert not is_token_valid(token)
```

### Testing Error Responses
```python
def test_login_with_nonexistent_user_returns_401():
    response = client.post('/api/v1/auth/login', json={
        'email': 'nonexistent@example.com',
        'password': 'password'
    })

    assert response.status_code == 401
    assert 'Invalid credentials' in response.json()['detail']
```

---

## 13. Troubleshooting & Maintenance

### Flaky Tests
- Identify: Run 3x consecutively, rerun in CI
- Causes: Time-dependent code, race conditions, non-deterministic data
- Solutions: Use freezegun, avoid sleeps, reset state properly

### Slow Tests
- Profile: `pytest --durations=10` shows slowest tests
- Optimize: Reduce database queries, mock slow operations
- Parallelize: Use pytest-xdist for unit tests

### Test Isolation Issues
- Problem: Tests pass alone, fail together
- Cause: Shared state, database pollution, global mocks
- Solution: Use transaction rollback, reset mocks, parametrize fixtures

### Coverage Gaps
- Monitor: HTML coverage reports with branch coverage
- Identify: Focus on critical business logic first
- Track: Trends over time, set increasing targets

---

## 14. Success Criteria

### Coverage Milestones
- ✓ Week 1: 50% backend coverage
- ✓ Week 2: 70% backend coverage
- ✓ Week 3: 80% backend coverage
- ✓ Week 4: 70% frontend coverage
- ✓ Week 5: Critical E2E scenarios passing
- ✓ Week 6: Full suite passing in CI/CD

### Quality Gates
- ✓ All new code requires tests
- ✓ No test regressions
- ✓ No flaky tests in CI
- ✓ Performance within budget
- ✓ Critical security paths fully covered

---

## References

- [pytest Documentation](https://docs.pytest.org)
- [Vitest Documentation](https://vitest.dev)
- [Playwright Documentation](https://playwright.dev)
- [Testing Library Best Practices](https://testing-library.com)
- [MSW Documentation](https://mswjs.io)

---

**Document Version:** 1.0
**Last Updated:** 2024-11-20
**Status:** Ready for Implementation
