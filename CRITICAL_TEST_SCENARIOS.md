# CodeRenew Critical Test Scenarios & Acceptance Criteria

## Overview
This document defines the most critical user workflows and system behaviors that must be thoroughly tested. These scenarios represent core business functionality and security features that must never fail in production.

---

## Priority Levels

- **P0 (CRITICAL):** System cannot function without this. Must pass 100% of time.
- **P1 (HIGH):** Core features that users depend on daily. Must pass before any release.
- **P2 (MEDIUM):** Important but not blocking. Should pass in production.

---

## 1. Security & Authentication Scenarios

### Scenario S1: User Registration with Validation
**Priority:** P0
**Category:** Authentication
**Impact:** User cannot create account

**Preconditions:**
- System running, database empty
- Email service working or mocked
- API endpoints accessible

**Test Steps:**

1. POST `/api/v1/auth/register` with valid data:
   ```json
   {
     "email": "newuser@example.com",
     "password": "SecurePass123!",
     "name": "New User"
   }
   ```

2. Verify HTTP 201 response
3. Verify user created in database with:
   - Email set correctly
   - Password hashed (not plaintext)
   - is_verified = false
   - onboarding_completed = false
4. Verify token returned:
   - Valid JWT format
   - Contains user ID in 'sub' claim
   - Expires in 24 hours
5. Verify user can access protected endpoint with token

**Expected Results:**
- HTTP 201 Created
- User in database
- Token valid and working
- User auto-logged in
- Response time < 500ms

**Acceptance Criteria:**
- [ ] User created with correct email
- [ ] Password properly hashed
- [ ] Token returned and valid
- [ ] User can access protected routes
- [ ] Verification email sent (if required)
- [ ] No plaintext passwords in logs/responses

**Test Variations:**
- Duplicate email → HTTP 400
- Missing fields → HTTP 422
- Weak password → HTTP 422
- Invalid email format → HTTP 422
- Rate limited (6th request) → HTTP 429

**Dependencies:**
- Database connection
- Email service (mock acceptable)
- Security utilities

**Mocks Required:**
- Email service (optional - can test with mock)

---

### Scenario S2: Account Lockout After Failed Logins
**Priority:** P0
**Category:** Security
**Impact:** Account security feature critical

**Preconditions:**
- User exists with known password
- Account not locked
- Login attempts recorded
- System time available

**Test Steps:**

1. Create test user: `testuser@example.com` / `CorrectPass123!`

2. Attempt login 5 times with wrong password:
   ```bash
   for i in {1..5}; do
     POST /api/v1/auth/login
     {"email": "testuser@example.com", "password": "WrongPass123!"}
   done
   ```

3. Verify each attempt returns HTTP 401
4. Verify failed_login_attempts incremented after each
5. After 5th failure, verify:
   - User.locked_until is set (30 minutes from now)
   - User.failed_login_attempts = 5
   - DB status shows locked
6. Attempt login with CORRECT password
   - Should return HTTP 403 "Account locked"
   - Should NOT return HTTP 401 "Invalid credentials"
   - Message must differ from wrong password
7. Wait 30 minutes (simulate with freezegun)
8. Attempt login with correct password
   - Should return HTTP 200 with token
   - failed_login_attempts should be 0
   - locked_until should be NULL

**Expected Results:**
- 5 failed attempts lock account
- Locked account rejects even correct password
- Lock message differs from "invalid credentials"
- Auto-unlock after 30 minutes
- Successful login resets counter

**Acceptance Criteria:**
- [ ] Lockout after exactly 5 failed attempts
- [ ] Lock duration is 30 minutes
- [ ] Correct password fails when locked
- [ ] Different error message for locked vs wrong password
- [ ] Auto-unlock works
- [ ] Counter reset on successful login
- [ ] Timestamp logic correct (no timezone issues)

**Security Considerations:**
- Message doesn't reveal whether account exists
- Timing attack resistant
- DoS prevention (rate limiting still applies)

**Test Variations:**
- Reset password while locked → should work
- Multiple concurrent login attempts → race condition handled
- Manual unlock by admin → should work

---

### Scenario S3: Rate Limiting on Auth Endpoints
**Priority:** P0
**Category:** Security
**Impact:** Brute force attack prevention

**Preconditions:**
- System running
- Rate limiter configured
- Fresh rate limit bucket (no previous requests)

**Test Steps:**

1. **Register Rate Limit (5/hour):**
   ```
   Make 6 registration requests from same IP
   - Requests 1-5: Should succeed or return validation errors
   - Request 6: Should return HTTP 429 Too Many Requests
   ```

2. **Login Rate Limit (10/hour):**
   ```
   Make 11 login requests from same IP
   - Requests 1-10: Should return 401 or 200
   - Request 11: Should return HTTP 429
   ```

3. **Password Reset Rate Limit (3/hour):**
   ```
   Make 4 password reset requests from same IP
   - Requests 1-3: Should return 200
   - Request 4: Should return HTTP 429
   ```

4. **Verify rate limit headers:**
   ```
   Response should include:
   X-RateLimit-Limit: 5
   X-RateLimit-Remaining: 4
   X-RateLimit-Reset: (timestamp)
   ```

5. **Verify different users have separate limits:**
   ```
   User A makes 5 requests → limited
   User B makes 5 requests → NOT limited
   ```

**Expected Results:**
- Rate limits enforced per endpoint
- Different limits for different endpoints
- Per-IP or per-user limiting (as designed)
- Headers indicate remaining requests
- Limits reset after time window

**Acceptance Criteria:**
- [ ] Register limited to 5/hour
- [ ] Login limited to 10/hour
- [ ] Password reset limited to 3/hour
- [ ] HTTP 429 returned when exceeded
- [ ] Rate limit headers present
- [ ] Per-user/IP isolation correct
- [ ] Response time < 10ms even when rate limited

**Test Variations:**
- Different IPs bypass limits (if per-IP)
- Different users bypass limits (if per-user)
- Time window boundaries (exactly at limit)

---

### Scenario S4: Password Reset Secure Flow
**Priority:** P0
**Category:** Security
**Impact:** Account recovery essential feature

**Preconditions:**
- User exists with email
- Email service working
- Reset tokens table empty

**Test Steps:**

1. Request password reset:
   ```json
   POST /api/v1/auth/request-password-reset
   {"email": "user@example.com"}
   ```

2. Verify HTTP 200 response (generic, no info leak)

3. Verify email sent with reset link:
   - Token in database for user
   - Token has expiration (1 hour from now)
   - Token unique and random

4. Extract token from email or database

5. Verify token validity:
   ```json
   POST /api/v1/auth/reset-password
   {
     "token": "valid_token_here",
     "new_password": "NewSecurePass123!"
   }
   ```

6. Verify HTTP 200 response

7. Verify password changed:
   - Old password no longer works
   - New password logs in successfully
   - User.reset_token is NULL
   - User.reset_token_expires is NULL

8. Attempt to use same token again:
   - Should fail with HTTP 400 (single-use)

9. Let token expire (> 1 hour):
   - Reset attempt fails with HTTP 400

**Expected Results:**
- Reset token created and sent
- Token expires after 1 hour
- Token single-use only
- Password updated in database
- Old password invalid
- New password valid immediately
- No info leak in responses

**Acceptance Criteria:**
- [ ] Token generated (32+ chars, random)
- [ ] Email sent within 5 seconds
- [ ] Token expires after 1 hour
- [ ] Token is single-use
- [ ] Password hash updated
- [ ] Old password rejected
- [ ] New password accepted
- [ ] No timing differences for invalid tokens
- [ ] No error messages reveal user existence

**Security Considerations:**
- No email confirmation before reset (UX vs security tradeoff)
- Token should be cryptographically random
- Expiration must be enforced
- Rate limiting on reset requests

**Test Variations:**
- Non-existent email → HTTP 200 (no info leak)
- Invalid token → HTTP 400
- Expired token → HTTP 400
- Weak password in reset → HTTP 422

---

## 2. Payment Processing Scenarios

### Scenario P1: Complete Stripe Payment Flow
**Priority:** P0
**Category:** Payment
**Impact:** Revenue generation blocked

**Preconditions:**
- User authenticated
- Stripe test keys configured
- Payment processing enabled
- Webhook receiving configured

**Test Steps:**

1. User initiates payment:
   ```json
   POST /api/v1/orders/create-payment
   {
     "plan_id": "plan_monthly",
     "plan_name": "Monthly Plan",
     "amount": 2999
   }
   ```

2. Verify response includes:
   - client_secret
   - payment_intent_id
   - status: "requires_payment_method"

3. Frontend receives Stripe client secret

4. Payment submitted through Stripe with test card:
   - Card: 4242 4242 4242 4242
   - Expiry: 12/25
   - CVC: 123

5. Stripe returns success

6. Webhook received at `/api/v1/orders/webhook`:
   ```json
   {
     "type": "payment_intent.succeeded",
     "data": {
       "object": {
         "id": "pi_...",
         "status": "succeeded"
       }
     }
   }
   ```

7. Verify order updated:
   - Status = "paid"
   - Subscription activated
   - Subscription expiry set correctly

8. Verify user permissions updated:
   - Premium features unlocked
   - Can access premium endpoints

9. Verify email sent:
   - Payment confirmation
   - Subscription details
   - Receipt/invoice

**Expected Results:**
- Payment intent created
- Payment succeeds
- Webhook processed
- Order marked paid
- Subscription active
- User has access
- Email sent

**Acceptance Criteria:**
- [ ] Payment intent created with correct amount
- [ ] Client secret returned to frontend
- [ ] Stripe payment succeeds
- [ ] Webhook received and processed
- [ ] Order status updated to "paid"
- [ ] Subscription created with correct dates
- [ ] Premium features accessible
- [ ] Payment confirmation email sent
- [ ] No race conditions (concurrent payments)
- [ ] Idempotent webhook processing

**Test Variations:**
- Declined card → Payment fails, order stays "pending"
- Webhook received twice → Idempotent, no double charge
- Webhook delay (1 hour) → Order eventually marked paid
- Invalid webhook signature → Rejected (security)

**Mocks:**
- Stripe API (test mode or mock library)

---

### Scenario P2: Failed Payment Recovery
**Priority:** P1
**Category:** Payment
**Impact:** Payment processing robustness

**Test Steps:**

1. Initiate payment that will fail
2. Payment declined by Stripe
3. Verify:
   - Order status = "failed"
   - Subscription NOT activated
   - User keeps free tier access
   - Error message shown
4. User can retry:
   - Create new payment intent
   - Different card succeeds
   - Order marked paid
   - Subscription activated

**Acceptance Criteria:**
- [ ] Failed payments don't charge
- [ ] Order marked failed
- [ ] User not granted access
- [ ] Retry mechanism available
- [ ] No dangling subscriptions

---

## 3. Core Workflow Scenarios

### Scenario W1: Complete Registration → Onboarding → First Scan
**Priority:** P0
**Category:** Workflow
**Impact:** User activation

**Preconditions:**
- System running
- All services available
- Clean database

**Test Steps:**

1. **Registration Phase:**
   - Register new user
   - Verify token received
   - User auto-logged in
   - Email verification token sent

2. **Onboarding Phase:**
   - Navigate to onboarding page
   - Fill company name: "Acme Corp"
   - Fill WordPress version: "5.9"
   - Fill target version: "6.4"
   - Submit form

3. **Verify Onboarding:**
   - User.onboarding_completed = true
   - Redirect to dashboard
   - User profile shows data

4. **First Scan:**
   - Upload theme ZIP file
   - Verify scan created (PENDING)
   - Background processing starts
   - Wait for completion (mock Claude response)
   - Results displayed
   - Issues listed

5. **Verify End State:**
   - User in database with all data
   - Scan completed
   - Results in database
   - All emails sent
   - No errors in logs

**Expected Results:**
- Complete workflow succeeds
- Data persists correctly
- User can see results
- No missing steps
- Performance acceptable

**Acceptance Criteria:**
- [ ] Registration succeeds
- [ ] Auto-login works
- [ ] Onboarding accessible
- [ ] Onboarding completes
- [ ] Dashboard accessible
- [ ] Scan uploadable
- [ ] Processing works
- [ ] Results viewable
- [ ] All timestamps correct
- [ ] No orphaned records

**Dependencies:**
- All backend services
- File storage
- Email service
- Claude API (mock)

---

### Scenario W2: Scan Upload and Processing Pipeline
**Priority:** P0
**Category:** Core Feature
**Impact:** Product core functionality

**Preconditions:**
- User authenticated and onboarded
- Test theme ZIP file ready
- Claude API mocked

**Test Steps:**

1. User uploads theme:
   - POST `/api/v1/scans/upload`
   - File: WordPress theme ZIP
   - Version info included
   - Size < 50MB

2. Verify scan created:
   - Status = PENDING
   - File stored in correct location
   - DB record created
   - Timestamp set

3. Background processing starts:
   - Extract ZIP
   - Analyze files
   - Send to Claude API
   - Parse response

4. Verify processing:
   - Status changes to PROCESSING
   - No errors logged

5. Verify completion:
   - Status = COMPLETED
   - ScanResults created
   - Risk level calculated
   - Issues counted

6. Verify results retrieval:
   - GET `/api/v1/scans/{id}/results`
   - Issues returned (paginated)
   - Details correct
   - Sorting works

**Expected Results:**
- Upload succeeds
- Processing completes
- Results accurate
- Data persists
- Performance acceptable

**Acceptance Criteria:**
- [ ] File uploaded successfully
- [ ] Scan record created
- [ ] Status transitions correct
- [ ] Results generated
- [ ] Results retrievable
- [ ] File cleanup after processing
- [ ] Error handling works
- [ ] Large files handled
- [ ] Invalid files rejected
- [ ] Duplicate uploads handled

**Performance Requirements:**
- Upload: < 2 seconds
- Processing: < 30 seconds
- Results retrieval: < 1 second
- File extraction: < 10 seconds

---

## 4. Data Integrity Scenarios

### Scenario D1: User Data Isolation
**Priority:** P1
**Category:** Security/Data
**Impact:** Privacy violation if failed

**Preconditions:**
- Multiple users in system
- Each user has scans

**Test Steps:**

1. User A logs in
2. Attempts to access User B's scans:
   - GET `/api/v1/users/{b_id}/scans`
   - Verify HTTP 403 Forbidden
3. Attempts to modify User B's data:
   - PUT `/api/v1/scans/{b_scan_id}`
   - Verify HTTP 403 Forbidden
4. Attempts to delete User B's scans:
   - DELETE `/api/v1/scans/{b_scan_id}`
   - Verify HTTP 403 Forbidden
5. Verify User A can ONLY access own data

**Acceptance Criteria:**
- [ ] Users cannot see other user's scans
- [ ] Users cannot modify other user's data
- [ ] Users cannot delete other user's data
- [ ] API returns proper error codes
- [ ] No data leaks in error messages

---

### Scenario D2: Database Consistency
**Priority:** P1
**Category:** Data Integrity
**Impact:** Data corruption possible

**Test Steps:**

1. Create user with sites and scans
2. Delete user
3. Verify cascade delete:
   - Sites deleted
   - Scans deleted
   - ScanResults deleted
   - No orphaned records
4. Verify referential integrity:
   - Foreign key constraints enforced
   - No broken relationships
   - No NULL in required fields

**Acceptance Criteria:**
- [ ] Cascade delete works
- [ ] No orphaned records
- [ ] Foreign keys enforced
- [ ] Constraints enforced

---

## 5. Error Handling & Resilience

### Scenario E1: API Error Responses
**Priority:** P1
**Category:** Reliability
**Impact:** Poor UX if not handled

**Test Steps:**

1. Invalid input → HTTP 422 with field errors
2. Unauthorized → HTTP 401
3. Forbidden → HTTP 403
4. Not found → HTTP 404
5. Rate limited → HTTP 429
6. Server error → HTTP 500
7. Service unavailable → HTTP 503

**Acceptance Criteria:**
- [ ] All error codes used correctly
- [ ] Error messages are user-friendly
- [ ] No sensitive info in errors
- [ ] Consistent error format
- [ ] Proper HTTP semantics

---

### Scenario E2: Service Failure Recovery
**Priority:** P1
**Category:** Resilience
**Impact:** Temporary outages manageable

**Test Steps:**

1. Claude API failure:
   - Retry logic works
   - Max retries enforced
   - User notified
   - Scan marked failed

2. Email service failure:
   - Non-blocking (scan still processes)
   - Retry queue works
   - User can retry manually

3. Database connection failure:
   - Connection pool handles reconnection
   - Requests queue/retry
   - Graceful degradation

**Acceptance Criteria:**
- [ ] Retries work (exponential backoff)
- [ ] Max retries enforced
- [ ] User notified of failures
- [ ] System recovers gracefully
- [ ] No data loss
- [ ] Logs capture failures

---

## 6. Performance & Scale

### Scenario Perf1: Response Time Requirements
**Priority:** P1
**Category:** Performance
**Impact:** User experience

**Requirements:**
- Registration: < 500ms
- Login: < 500ms
- List scans: < 1s (paginated, 10 items)
- Get results: < 1s (paginated)
- Upload file: < 2s

**Test Method:**
- Load 100 concurrent users
- Measure p50, p95, p99 latencies
- Verify no timeouts
- Verify no memory leaks

---

## 7. Security Testing

### Scenario Sec1: SQL Injection Prevention
**Priority:** P0
**Category:** Security
**Impact:** Critical vulnerability

**Test Cases:**
- Email field: `admin'--`
- Search: `'; DROP TABLE users;--`
- Name field: `<script>alert(1)</script>`

**Verification:**
- Input sanitized/parameterized
- No error in response
- No data modified

---

### Scenario Sec2: XSS Prevention
**Priority:** P0
**Category:** Security
**Impact:** Critical vulnerability

**Test Cases:**
- Company name: `<img src=x onerror=alert(1)>`
- Scan results display: Verify escaping
- Error messages: Verify HTML-encoded

---

### Scenario Sec3: CSRF Protection
**Priority:** P0
**Category:** Security
**Impact:** Critical vulnerability

**Test Cases:**
- State-changing requests require CSRF token
- Token validated
- POST without token rejected

---

## Test Execution Matrix

| Scenario | Unit | Integration | E2E | Manual | Frequency |
|----------|------|-------------|-----|--------|-----------|
| S1 Registration | ✓ | ✓ | ✓ | - | Every PR |
| S2 Lockout | ✓ | ✓ | ✓ | - | Every PR |
| S3 Rate Limiting | ✓ | ✓ | - | - | Every PR |
| S4 Password Reset | ✓ | ✓ | ✓ | - | Every PR |
| P1 Payment | - | ✓ | ✓ | ✓ | Weekly |
| W1 Complete Flow | - | - | ✓ | ✓ | Every release |
| W2 Scan Pipeline | - | ✓ | ✓ | - | Every PR |
| D1 Data Isolation | ✓ | ✓ | - | - | Every PR |
| E1 Errors | ✓ | ✓ | - | - | Every PR |
| Sec1 SQL Injection | ✓ | ✓ | - | - | Every PR |

---

## Success Criteria for Testing

- All P0 scenarios pass 100% of time
- All P1 scenarios pass 99% of time
- Test coverage > 80% for modified code
- No flaky tests (pass/fail randomness)
- Performance requirements met
- All security tests passing
- Error handling tested
- Data integrity verified

---

**Document Version:** 1.0
**Last Updated:** 2024-11-20
**Status:** Ready for Implementation
**Owner:** QA Specialist Team
