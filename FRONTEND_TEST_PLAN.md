# CodeRenew Frontend Test Plan

## Overview
Detailed test specifications for React components, forms, and user workflows. Tests focus on user interactions, form validation, API integration, and critical user journeys.

---

## 1. Authentication Components

### File: `/frontend/tests/unit/components/auth/LoginForm.test.tsx`

#### Test 1.1: Login Form Rendering
**Priority:** HIGH
**Category:** Unit Test
**Description:** Verify login form renders with all elements

```typescript
import { render, screen } from 'vitest-browser-react'
import { LoginForm } from '@/components/auth/LoginForm'

describe('LoginForm', () => {
  test('renders email input field', async () => {
    const { getByLabelText } = render(<LoginForm onSuccess={() => {}} />)
    const emailInput = getByLabelText(/email/i)
    await expect.element(emailInput).toBeInTheDocument()
  })

  test('renders password input field', async () => {
    const { getByLabelText } = render(<LoginForm onSuccess={() => {}} />)
    const passwordInput = getByLabelText(/password/i)
    await expect.element(passwordInput).toBeInTheDocument()
  })

  test('renders submit button', async () => {
    const { getByRole } = render(<LoginForm onSuccess={() => {}} />)
    const submitButton = getByRole('button', { name: /sign in|login/i })
    await expect.element(submitButton).toBeInTheDocument()
  })

  test('renders forgot password link', async () => {
    const { getByRole } = render(<LoginForm onSuccess={() => {}} />)
    const link = getByRole('link', { name: /forgot password/i })
    await expect.element(link).toBeInTheDocument()
  })

  test('renders register link', async () => {
    const { getByRole } = render(<LoginForm onSuccess={() => {}} />)
    const link = getByRole('link', { name: /don't have an account|sign up|register/i })
    await expect.element(link).toBeInTheDocument()
  })
})
```

**Acceptance Criteria:**
- All form fields render
- All buttons and links present
- Proper labels for accessibility
- Input types correct (email, password)

**Mocks:** None (render only)
**Dependencies:** vitest-browser-react, @testing-library/react

---

#### Test 1.2: Login Form Input Validation
**Priority:** HIGH
**Category:** Unit Test
**Description:** Verify client-side validation works

```typescript
describe('LoginForm Validation', () => {
  test('shows error when email is empty', async () => {
    const { getByLabelText, getByText } = render(<LoginForm onSuccess={() => {}} />)
    const submitButton = getByRole('button', { name: /sign in/i })

    await page.getByLabelText(/email/i).fill('')
    await page.getByLabelText(/password/i).fill('password123')
    await submitButton.click()

    await expect.element(getByText(/email.*required|email.*invalid/i)).toBeInTheDocument()
  })

  test('shows error when password is empty', async () => {
    const { getByText } = render(<LoginForm onSuccess={() => {}} />)
    const submitButton = getByRole('button', { name: /sign in/i })

    await page.getByLabelText(/email/i).fill('test@example.com')
    await page.getByLabelText(/password/i).fill('')
    await submitButton.click()

    await expect.element(getByText(/password.*required/i)).toBeInTheDocument()
  })

  test('shows error for invalid email format', async () => {
    const { getByText } = render(<LoginForm onSuccess={() => {}} />)
    const submitButton = getByRole('button', { name: /sign in/i })

    await page.getByLabelText(/email/i).fill('not-an-email')
    await page.getByLabelText(/password/i).fill('password123')
    await submitButton.click()

    await expect.element(getByText(/email.*invalid|valid email/i)).toBeInTheDocument()
  })

  test('enables submit button when form is valid', async () => {
    const { getByRole } = render(<LoginForm onSuccess={() => {}} />)
    const submitButton = getByRole('button', { name: /sign in/i })

    await page.getByLabelText(/email/i).fill('test@example.com')
    await page.getByLabelText(/password/i).fill('ValidPassword123!')

    // Button should be enabled
    const isDisabled = await submitButton.getAttribute('disabled')
    expect(isDisabled).not.toBeTruthy()
  })
})
```

**Acceptance Criteria:**
- Validation errors display correctly
- Required fields enforced
- Email format validated
- Submit button disabled until valid
- Error messages clear

**Mocks:** None
**Dependencies:** vitest-browser-react, form validation library

---

#### Test 1.3: Login Form Submission
**Priority:** CRITICAL
**Category:** Integration Test
**Description:** Verify form submits to API correctly

```typescript
import { setupServer } from 'msw/browser'
import { http, HttpResponse } from 'msw'

describe('LoginForm Submission', () => {
  test('submits form data to API on valid input', async () => {
    const mockHandler = vi.fn()
    const server = setupServer(
      http.post('/api/v1/auth/login', () => {
        mockHandler()
        return HttpResponse.json({
          access_token: 'test_token',
          user: { id: 1, email: 'test@example.com' }
        })
      })
    )
    server.listen()

    const { getByRole } = render(<LoginForm onSuccess={() => {}} />)

    await page.getByLabelText(/email/i).fill('test@example.com')
    await page.getByLabelText(/password/i).fill('MyPassword123!')
    await getByRole('button', { name: /sign in/i }).click()

    // Wait for API call
    await expect.poll(() => mockHandler.mock.calls.length).toBe(1)

    server.close()
  })

  test('shows loading state while submitting', async () => {
    const server = setupServer(
      http.post('/api/v1/auth/login', async () => {
        await new Promise(resolve => setTimeout(resolve, 100))
        return HttpResponse.json({
          access_token: 'test_token',
          user: { id: 1, email: 'test@example.com' }
        })
      })
    )
    server.listen()

    const { getByRole } = render(<LoginForm onSuccess={() => {}} />)

    await page.getByLabelText(/email/i).fill('test@example.com')
    await page.getByLabelText(/password/i).fill('MyPassword123!')
    await getByRole('button', { name: /sign in/i }).click()

    // Button should show loading state
    const button = getByRole('button', { name: /sign in|signing in/i })
    await expect.element(button).toContainText(/signing in|loading/i)

    server.close()
  })

  test('shows error message on API failure', async () => {
    const server = setupServer(
      http.post('/api/v1/auth/login', () => {
        return HttpResponse.json(
          { detail: 'Invalid credentials' },
          { status: 401 }
        )
      })
    )
    server.listen()

    const { getByText } = render(<LoginForm onSuccess={() => {}} />)

    await page.getByLabelText(/email/i).fill('test@example.com')
    await page.getByLabelText(/password/i).fill('WrongPassword!')
    await getByRole('button', { name: /sign in/i }).click()

    await expect.element(getByText(/invalid credentials/i)).toBeInTheDocument()

    server.close()
  })

  test('calls onSuccess callback after successful login', async () => {
    const onSuccess = vi.fn()
    const server = setupServer(
      http.post('/api/v1/auth/login', () => {
        return HttpResponse.json({
          access_token: 'test_token',
          user: { id: 1, email: 'test@example.com' }
        })
      })
    )
    server.listen()

    const { getByRole } = render(<LoginForm onSuccess={onSuccess} />)

    await page.getByLabelText(/email/i).fill('test@example.com')
    await page.getByLabelText(/password/i).fill('MyPassword123!')
    await getByRole('button', { name: /sign in/i }).click()

    await expect.poll(() => onSuccess.mock.calls.length).toBeGreaterThan(0)

    server.close()
  })
})
```

**Acceptance Criteria:**
- Form data sent to correct endpoint
- Loading state shown during submission
- Error messages displayed on failure
- Success callback called on success
- Token stored securely (localStorage or cookie)

**Mocks:** MSW for API responses
**Dependencies:** vitest, msw, vi.fn()

---

#### Test 1.4: Password Visibility Toggle
**Priority:** MEDIUM
**Category:** Unit Test
**Description:** Verify password visibility toggle works

```typescript
describe('Password Visibility Toggle', () => {
  test('password field is initially type password', async () => {
    const { getByLabelText } = render(<LoginForm onSuccess={() => {}} />)
    const passwordInput = getByLabelText(/password/i) as HTMLInputElement

    expect(passwordInput.type).toBe('password')
  })

  test('clicking toggle shows password', async () => {
    const { getByRole, getByLabelText } = render(<LoginForm onSuccess={() => {}} />)
    const toggleButton = getByRole('button', { name: /show password|visibility/i })

    const passwordInput = getByLabelText(/password/i) as HTMLInputElement
    expect(passwordInput.type).toBe('password')

    await toggleButton.click()

    await expect.element(passwordInput).toHaveAttribute('type', 'text')
  })

  test('clicking toggle again hides password', async () => {
    const { getByRole, getByLabelText } = render(<LoginForm onSuccess={() => {}} />)
    const toggleButton = getByRole('button', { name: /show password|visibility/i })
    const passwordInput = getByLabelText(/password/i) as HTMLInputElement

    await toggleButton.click()
    expect(passwordInput.type).toBe('text')

    await toggleButton.click()
    expect(passwordInput.type).toBe('password')
  })
})
```

**Acceptance Criteria:**
- Toggle button functional
- Password visibility switches
- Icon/text updates appropriately

**Mocks:** None
**Dependencies:** vitest-browser-react

---

### File: `/frontend/tests/unit/components/auth/RegisterForm.test.tsx`

#### Test 2.1: Registration Form Validation
**Priority:** CRITICAL
**Category:** Unit Test
**Description:** Verify registration validation (email, password, confirm, terms)

```typescript
describe('RegisterForm', () => {
  test('requires email field', async () => {
    const { getByText } = render(<RegisterForm onSuccess={() => {}} />)
    const submitButton = getByRole('button', { name: /sign up|register/i })

    await page.getByLabelText(/email/i).fill('')
    await submitButton.click()

    await expect.element(getByText(/email.*required/i)).toBeInTheDocument()
  })

  test('validates email format', async () => {
    const { getByText } = render(<RegisterForm onSuccess={() => {}} />)
    const submitButton = getByRole('button', { name: /sign up|register/i })

    await page.getByLabelText(/email/i).fill('invalid-email')
    await submitButton.click()

    await expect.element(getByText(/email.*invalid|valid email/i)).toBeInTheDocument()
  })

  test('requires strong password', async () => {
    const { getByText } = render(<RegisterForm onSuccess={() => {}} />)

    // Test weak passwords
    const weakPasswords = ['short', '12345678', 'NoNumbers!', 'nouppErcase123!']

    for (const pwd of weakPasswords) {
      await page.getByLabelText(/^password/i).fill(pwd)
      await getByRole('button', { name: /sign up|register/i }).click()

      await expect.element(
        getByText(/password.*weak|uppercase|number|special/i)
      ).toBeInTheDocument()
    }
  })

  test('requires password confirmation to match', async () => {
    const { getByText } = render(<RegisterForm onSuccess={() => {}} />)

    await page.getByLabelText(/^password/i).fill('StrongPass123!')
    await page.getByLabelText(/confirm password/i).fill('DifferentPass123!')
    await getByRole('button', { name: /sign up|register/i }).click()

    await expect.element(getByText(/passwords do not match|confirm/i)).toBeInTheDocument()
  })

  test('requires terms acceptance', async () => {
    const { getByText } = render(<RegisterForm onSuccess={() => {}} />)

    await page.getByLabelText(/email/i).fill('test@example.com')
    await page.getByLabelText(/^password/i).fill('StrongPass123!')
    await page.getByLabelText(/confirm password/i).fill('StrongPass123!')
    // Don't check terms checkbox

    await getByRole('button', { name: /sign up|register/i }).click()

    await expect.element(
      getByText(/accept.*terms|terms.*required/i)
    ).toBeInTheDocument()
  })

  test('enables submit button when all fields valid', async () => {
    const { getByRole } = render(<RegisterForm onSuccess={() => {}} />)

    await page.getByLabelText(/email/i).fill('test@example.com')
    await page.getByLabelText(/^password/i).fill('StrongPass123!')
    await page.getByLabelText(/confirm password/i).fill('StrongPass123!')
    await page.getByRole('checkbox', { name: /accept.*terms/i }).click()

    const submitButton = getByRole('button', { name: /sign up|register/i })
    const isDisabled = await submitButton.getAttribute('disabled')

    expect(isDisabled).not.toBeTruthy()
  })
})
```

**Acceptance Criteria:**
- All validation rules enforced
- Error messages clear and specific
- Submit button disabled until valid
- UX feedback provided (real-time or on submit)

**Mocks:** None
**Dependencies:** vitest-browser-react, form validation

---

#### Test 2.2: Registration Submission and Auto-Login
**Priority:** CRITICAL
**Category:** Integration Test
**Description:** Verify registration creates user and auto-logs in

```typescript
describe('RegisterForm Submission', () => {
  test('submits registration data to API', async () => {
    const mockHandler = vi.fn()
    const server = setupServer(
      http.post('/api/v1/auth/register', () => {
        mockHandler()
        return HttpResponse.json({
          access_token: 'new_user_token',
          user: { id: 2, email: 'newuser@example.com', name: 'New User' }
        })
      })
    )
    server.listen()

    const { getByRole } = render(<RegisterForm onSuccess={() => {}} />)

    await page.getByLabelText(/email/i).fill('newuser@example.com')
    await page.getByLabelText(/name/i).fill('New User')
    await page.getByLabelText(/^password/i).fill('NewPass123!')
    await page.getByLabelText(/confirm password/i).fill('NewPass123!')
    await page.getByRole('checkbox', { name: /accept.*terms/i }).click()
    await getByRole('button', { name: /sign up|register/i }).click()

    await expect.poll(() => mockHandler.mock.calls.length).toBe(1)

    server.close()
  })

  test('handles duplicate email error', async () => {
    const server = setupServer(
      http.post('/api/v1/auth/register', () => {
        return HttpResponse.json(
          { detail: 'Email already registered' },
          { status: 400 }
        )
      })
    )
    server.listen()

    const { getByText } = render(<RegisterForm onSuccess={() => {}} />)

    await page.getByLabelText(/email/i).fill('existing@example.com')
    await page.getByLabelText(/name/i).fill('User')
    await page.getByLabelText(/^password/i).fill('StrongPass123!')
    await page.getByLabelText(/confirm password/i).fill('StrongPass123!')
    await page.getByRole('checkbox', { name: /accept.*terms/i }).click()
    await getByRole('button', { name: /sign up|register/i }).click()

    await expect.element(getByText(/email already registered/i)).toBeInTheDocument()

    server.close()
  })

  test('calls onSuccess after registration', async () => {
    const onSuccess = vi.fn()
    const server = setupServer(
      http.post('/api/v1/auth/register', () => {
        return HttpResponse.json({
          access_token: 'new_user_token',
          user: { id: 2, email: 'newuser@example.com' }
        })
      })
    )
    server.listen()

    const { getByRole } = render(<RegisterForm onSuccess={onSuccess} />)

    await page.getByLabelText(/email/i).fill('newuser@example.com')
    await page.getByLabelText(/name/i).fill('New User')
    await page.getByLabelText(/^password/i).fill('NewPass123!')
    await page.getByLabelText(/confirm password/i).fill('NewPass123!')
    await page.getByRole('checkbox', { name: /accept.*terms/i }).click()
    await getByRole('button', { name: /sign up|register/i }).click()

    await expect.poll(() => onSuccess.mock.calls.length).toBeGreaterThan(0)

    server.close()
  })
})
```

**Acceptance Criteria:**
- Registration data sent correctly
- Duplicate email handled
- User auto-logged in
- Token stored
- Redirect to dashboard/onboarding

**Mocks:** MSW for API responses
**Dependencies:** vitest, msw

---

### File: `/frontend/tests/unit/components/auth/ProtectedRoute.test.tsx`

#### Test 3.1: Protected Route Access Control
**Priority:** CRITICAL
**Category:** Unit Test
**Description:** Verify ProtectedRoute redirects unauthenticated users

```typescript
describe('ProtectedRoute', () => {
  test('allows authenticated users to access protected content', async () => {
    // Mock authenticated context
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider user={{ id: 1, email: 'test@example.com' }}>
        {children}
      </AuthProvider>
    )

    const { getByText } = render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>,
      { wrapper }
    )

    await expect.element(getByText('Protected Content')).toBeInTheDocument()
  })

  test('redirects unauthenticated users to login', async () => {
    const useRouter = vi.fn(() => ({
      push: vi.fn(),
      replace: vi.fn()
    }))

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider user={null}>
        {children}
      </AuthProvider>
    )

    render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>,
      { wrapper }
    )

    // Should redirect to login
    await expect.poll(() => {
      // Verify redirect occurred
      const router = useRouter()
      return router.push.mock.calls.some(call => call[0].includes('login'))
    }).toBeTruthy()
  })

  test('preserves redirect location after login', async () => {
    // Should remember where user tried to go and redirect after login
    const location = '/dashboard/scans'

    // Simulate user trying to access protected route
    // After login, should redirect back to original location
  })
})
```

**Acceptance Criteria:**
- Authenticated users access content
- Unauthenticated users redirected
- Redirect location preserved
- Clear auth flow

**Mocks:** Next.js router, auth context
**Dependencies:** vitest-browser-react, context mocking

---

## 2. Form Components

### File: `/frontend/tests/unit/components/forms/OnboardingForm.test.tsx`

#### Test 4.1: Multi-Step Form Navigation
**Priority:** HIGH
**Category:** Unit Test
**Description:** Verify multi-step form steps work correctly

```typescript
describe('OnboardingForm', () => {
  test('renders step 1 on initial load', async () => {
    const { getByText } = render(<OnboardingForm onComplete={() => {}} />)

    await expect.element(getByText(/step 1|company/i)).toBeInTheDocument()
  })

  test('navigates to next step on next button', async () => {
    const { getByRole, getByText } = render(<OnboardingForm onComplete={() => {}} />)

    // Fill step 1
    await page.getByLabelText(/company/i).fill('Acme Corp')
    const nextButton = getByRole('button', { name: /next|continue/i })
    await nextButton.click()

    // Should show step 2
    await expect.element(getByText(/step 2|wordpress/i)).toBeInTheDocument()
  })

  test('navigates back on previous button', async () => {
    const { getByRole, getByText } = render(<OnboardingForm onComplete={() => {}} />)

    // Go to step 2
    await page.getByLabelText(/company/i).fill('Acme Corp')
    await getByRole('button', { name: /next|continue/i }).click()

    // Go back to step 1
    const prevButton = getByRole('button', { name: /back|previous/i })
    await prevButton.click()

    await expect.element(getByText(/step 1|company/i)).toBeInTheDocument()
  })

  test('disables next button when step invalid', async () => {
    const { getByRole } = render(<OnboardingForm onComplete={() => {}} />)

    // Don't fill required fields
    const nextButton = getByRole('button', { name: /next|continue/i })
    const isDisabled = await nextButton.getAttribute('disabled')

    expect(isDisabled).toBeTruthy()
  })

  test('shows progress indicator', async () => {
    const { getByText } = render(<OnboardingForm onComplete={() => {}} />)

    // Should show something like "Step 1 of 3"
    await expect.element(getByText(/1.*3|step 1/i)).toBeInTheDocument()
  })
})
```

**Acceptance Criteria:**
- Steps display correctly
- Navigation works
- Progress shown
- Validation enforced per step
- Data persists across steps

**Mocks:** None
**Dependencies:** vitest-browser-react

---

#### Test 4.2: Form Data Persistence
**Priority:** HIGH
**Category:** Unit Test
**Description:** Verify data persists across form steps

```typescript
describe('OnboardingForm Data Persistence', () => {
  test('retains data when navigating between steps', async () => {
    const { getByRole, getByLabelText } = render(<OnboardingForm onComplete={() => {}} />)

    // Fill step 1
    await page.getByLabelText(/company/i).fill('Acme Corp')
    await getByRole('button', { name: /next|continue/i }).click()

    // Go back to step 1
    await getByRole('button', { name: /back|previous/i }).click()

    // Company name should still be there
    const companyInput = getByLabelText(/company/i) as HTMLInputElement
    expect(companyInput.value).toBe('Acme Corp')
  })

  test('submits all form data on final submit', async () => {
    const mockSubmit = vi.fn()
    const { getByRole } = render(
      <OnboardingForm onComplete={mockSubmit} />
    )

    // Fill all steps
    await page.getByLabelText(/company/i).fill('Acme Corp')
    await getByRole('button', { name: /next|continue/i }).click()

    await page.getByLabelText(/wordpress version/i).fill('6.0')
    await getByRole('button', { name: /next|continue/i }).click()

    // Final step submit
    await getByRole('button', { name: /complete|submit|finish/i }).click()

    // Should submit all data
    expect(mockSubmit).toHaveBeenCalledWith({
      company: 'Acme Corp',
      wordpress_version: '6.0',
      // ... other fields
    })
  })
})
```

**Acceptance Criteria:**
- Data persists across steps
- All data submitted at end
- Clear indication of final step

**Mocks:** None
**Dependencies:** vitest-browser-react

---

## 3. Dashboard Components

### File: `/frontend/tests/unit/components/layouts/DashboardLayout.test.tsx`

#### Test 5.1: Dashboard Layout Structure
**Priority:** HIGH
**Category:** Unit Test
**Description:** Verify dashboard layout renders correctly

```typescript
describe('DashboardLayout', () => {
  test('renders navigation header', async () => {
    const { getByRole } = render(
      <DashboardLayout>
        <div>Dashboard Content</div>
      </DashboardLayout>
    )

    const nav = getByRole('navigation')
    await expect.element(nav).toBeInTheDocument()
  })

  test('renders user menu', async () => {
    const { getByRole } = render(
      <DashboardLayout>
        <div>Dashboard Content</div>
      </DashboardLayout>
    )

    const userMenu = getByRole('button', { name: /profile|account|user/i })
    await expect.element(userMenu).toBeInTheDocument()
  })

  test('renders logout button in user menu', async () => {
    const { getByRole, getByText } = render(
      <DashboardLayout>
        <div>Dashboard Content</div>
      </DashboardLayout>
    )

    const userMenu = getByRole('button', { name: /profile|account|user/i })
    await userMenu.click()

    await expect.element(getByText(/logout|sign out/i)).toBeInTheDocument()
  })

  test('renders sidebar navigation', async () => {
    const { getByText } = render(
      <DashboardLayout>
        <div>Dashboard Content</div>
      </DashboardLayout>
    )

    await expect.element(getByText(/scans|results|settings/i)).toBeInTheDocument()
  })

  test('renders main content area', async () => {
    const { getByText } = render(
      <DashboardLayout>
        <div>Dashboard Content Here</div>
      </DashboardLayout>
    )

    await expect.element(getByText('Dashboard Content Here')).toBeInTheDocument()
  })
})
```

**Acceptance Criteria:**
- Layout renders all sections
- Navigation accessible
- User menu functional
- Content area displays children
- Responsive on mobile

**Mocks:** Next.js router
**Dependencies:** vitest-browser-react

---

## 4. API Integration Tests

### File: `/frontend/tests/unit/lib/api.test.ts`

#### Test 6.1: API Client Initialization
**Priority:** HIGH
**Category:** Unit Test
**Description:** Verify API client configured correctly

```typescript
describe('API Client', () => {
  test('initializes with correct base URL', () => {
    const client = getApiClient()

    expect(client.defaults.baseURL).toBe(process.env.NEXT_PUBLIC_API_URL)
  })

  test('includes authorization header when token present', () => {
    localStorage.setItem('access_token', 'test_token_123')
    const client = getApiClient()

    expect(client.defaults.headers.Authorization).toBe('Bearer test_token_123')
  })

  test('removes authorization header when token absent', () => {
    localStorage.removeItem('access_token')
    const client = getApiClient()

    expect(client.defaults.headers.Authorization).toBeUndefined()
  })
})
```

**Acceptance Criteria:**
- Client configured with correct base URL
- Token included when available
- Token removed when unavailable

**Mocks:** localStorage
**Dependencies:** vitest, axios

---

#### Test 6.2: API Error Handling
**Priority:** HIGH
**Category:** Integration Test
**Description:** Verify API errors handled correctly

```typescript
describe('API Error Handling', () => {
  test('handles 401 Unauthorized by logging out', async () => {
    const server = setupServer(
      http.get('/api/v1/user', () => {
        return HttpResponse.json(
          { detail: 'Unauthorized' },
          { status: 401 }
        )
      })
    )
    server.listen()

    const mockLogout = vi.fn()

    try {
      await api.get('/api/v1/user')
    } catch (error) {
      // Should trigger logout
      mockLogout()
    }

    expect(mockLogout).toHaveBeenCalled()

    server.close()
  })

  test('handles 403 Forbidden appropriately', async () => {
    const server = setupServer(
      http.post('/api/v1/scans/upload', () => {
        return HttpResponse.json(
          { detail: 'Access denied' },
          { status: 403 }
        )
      })
    )
    server.listen()

    try {
      await api.post('/api/v1/scans/upload', {})
    } catch (error: any) {
      expect(error.response.status).toBe(403)
    }

    server.close()
  })

  test('handles 500 Server Error', async () => {
    const server = setupServer(
      http.get('/api/v1/scans', () => {
        return HttpResponse.json(
          { detail: 'Internal server error' },
          { status: 500 }
        )
      })
    )
    server.listen()

    try {
      await api.get('/api/v1/scans')
    } catch (error: any) {
      expect(error.response.status).toBe(500)
    }

    server.close()
  })
})
```

**Acceptance Criteria:**
- 401 triggers logout
- Error messages user-friendly
- Proper status codes returned
- Network errors handled

**Mocks:** MSW for API responses
**Dependencies:** vitest, msw

---

## 5. Critical E2E Test Scenarios

### File: `/frontend/tests/e2e/auth.spec.ts`

#### Test 7.1: Complete Registration Flow
**Priority:** CRITICAL
**Category:** E2E Test
**Description:** Register user and verify access to dashboard

```typescript
import { test, expect } from '@playwright/test'

test('complete user registration and onboarding', async ({ page }) => {
  // 1. Navigate to registration
  await page.goto('/auth/register')

  // 2. Fill registration form
  await page.getByLabel(/email/i).fill('newuser@example.com')
  await page.getByLabel(/name/i).fill('New User')
  await page.getByLabel(/password/i).fill('SecurePassword123!')
  await page.getByLabel(/confirm password/i).fill('SecurePassword123!')
  await page.getByRole('checkbox', { name: /terms/i }).click()

  // 3. Submit registration
  await page.getByRole('button', { name: /sign up|register/i }).click()

  // 4. Verify redirect to onboarding
  await expect(page).toHaveURL('/onboarding')

  // 5. Complete onboarding
  await page.getByLabel(/company/i).fill('Acme Corp')
  await page.getByRole('button', { name: /next|continue/i }).click()

  await page.getByLabel(/wordpress version/i).selectOption('6.0')
  await page.getByRole('button', { name: /complete|finish/i }).click()

  // 6. Verify redirect to dashboard
  await expect(page).toHaveURL('/dashboard')

  // 7. Verify user data in profile
  await page.getByRole('button', { name: /profile|account|user/i }).click()
  await page.getByRole('link', { name: /profile/i }).click()

  await expect(page.getByText('New User')).toBeVisible()
  await expect(page.getByText('Acme Corp')).toBeVisible()
})
```

**Acceptance Criteria:**
- Registration completes successfully
- Auto-login works
- Onboarding accessible
- Dashboard loads after onboarding
- User data persists

**Mocks:** None (real API calls to test environment)
**Dependencies:** Playwright, test environment

---

#### Test 7.2: Login Flow
**Priority:** CRITICAL
**Category:** E2E Test

```typescript
test('user can login with valid credentials', async ({ page }) => {
  // 1. Navigate to login
  await page.goto('/auth/login')

  // 2. Fill login form
  await page.getByLabel(/email/i).fill('existinguser@example.com')
  await page.getByLabel(/password/i).fill('ExistingPassword123!')

  // 3. Submit login
  await page.getByRole('button', { name: /sign in|login/i }).click()

  // 4. Verify redirect to dashboard
  await expect(page).toHaveURL('/dashboard')

  // 5. Verify authenticated (can see user data)
  await expect(page.getByText(/dashboard|scans/i)).toBeVisible()
})
```

**Acceptance Criteria:**
- Login redirects to dashboard
- Auth header set
- Can access protected pages
- Protected routes block without auth

**Mocks:** None
**Dependencies:** Playwright, pre-created test user

---

#### Test 7.3: Scan Upload and Processing
**Priority:** CRITICAL
**Category:** E2E Test

```typescript
test('user can upload and process wordpress scan', async ({ page }) => {
  // 1. Login
  await page.goto('/auth/login')
  await page.getByLabel(/email/i).fill('testuser@example.com')
  await page.getByLabel(/password/i).fill('TestPassword123!')
  await page.getByRole('button', { name: /sign in/i }).click()

  // 2. Navigate to scans
  await page.goto('/dashboard/scans')

  // 3. Upload file
  const fileInput = page.locator('input[type="file"]')
  await fileInput.setInputFiles('./fixtures/test-theme.zip')

  // 4. Set version info
  await page.getByLabel(/current version/i).selectOption('5.9')
  await page.getByLabel(/target version/i).selectOption('6.4')

  // 5. Submit upload
  await page.getByRole('button', { name: /upload|scan/i }).click()

  // 6. Wait for processing to complete
  await page.waitForTimeout(5000)  // Wait for async processing

  // 7. View results
  await expect(page.getByText(/results|issues/i)).toBeVisible()

  // 8. Verify results contain expected data
  const resultsSection = page.locator('[data-testid="scan-results"]')
  await expect(resultsSection).toContainText(/deprecated|warning|critical/i)
})
```

**Acceptance Criteria:**
- File uploads successfully
- Processing status updates
- Results display
- Issues listed with details
- Performance acceptable

**Mocks:** None
**Dependencies:** Playwright, test files, test environment

---

## 6. Playwright Configuration

### File: `/frontend/tests/playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  testMatch: '**/*.spec.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

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
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

---

## 7. Vitest Configuration

### File: `/frontend/tests/vitest.config.ts`

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
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.test.ts',
        '**/*.spec.ts',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

---

## 8. Test Setup

### File: `/frontend/tests/setup.ts`

```typescript
import { expect, afterEach, vi } from 'vitest'
import { cleanup } from 'vitest-browser-react'
import * as matchers from '@testing-library/jest-dom/matchers'
import { setupServer } from 'msw/browser'

// Extend Vitest matchers
expect.extend(matchers)

// Cleanup after each test
afterEach(() => {
  cleanup()
  localStorage.clear()
  vi.clearAllMocks()
})

// Mock window.matchMedia
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
```

---

## 9. Test Execution Commands

```bash
# Run all unit and integration tests
npm run test:unit

# Run E2E tests
npm run test:e2e

# Run specific test file
npm run test:unit -- LoginForm.test.tsx

# Run with UI
npm run test:unit -- --ui

# Generate coverage report
npm run test:unit -- --coverage

# Run E2E tests in headless mode
npm run test:e2e -- --headed=false

# Run E2E tests in headed mode (see browser)
npm run test:e2e -- --headed

# Run single E2E spec
npm run test:e2e -- auth.spec.ts
```

---

## 10. Package.json Scripts

```json
{
  "scripts": {
    "test": "npm run test:unit && npm run test:e2e",
    "test:unit": "vitest run",
    "test:unit:watch": "vitest",
    "test:integration": "vitest run --include '**/integration/**'",
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed",
    "test:debug": "vitest --inspect-brk --inspect --no-file-parallelism",
    "test:coverage": "vitest run --coverage"
  }
}
```

---

## 11. MSW Mock Handlers

### File: `/frontend/tests/mocks/handlers.ts`

```typescript
import { http, HttpResponse } from 'msw'

export const handlers = [
  // Auth endpoints
  http.post('/api/v1/auth/login', async ({ request }) => {
    const body = await request.json() as any
    return HttpResponse.json({
      access_token: 'mock_token_' + Date.now(),
      user: {
        id: 1,
        email: body.email,
        name: 'Test User',
        is_verified: true,
      }
    })
  }),

  http.post('/api/v1/auth/register', async ({ request }) => {
    const body = await request.json() as any
    return HttpResponse.json({
      access_token: 'mock_token_' + Date.now(),
      user: {
        id: 2,
        email: body.email,
        name: body.name,
        is_verified: false,
      }
    }, { status: 201 })
  }),

  // Scan endpoints
  http.get('/api/v1/scans', () => {
    return HttpResponse.json([
      {
        id: 1,
        status: 'completed',
        created_at: new Date().toISOString(),
      }
    ])
  }),

  http.post('/api/v1/scans/upload', ({ request }) => {
    return HttpResponse.json({
      scan_id: Math.floor(Math.random() * 1000),
    }, { status: 202 })
  }),
]
```

---

**Document Version:** 1.0
**Last Updated:** 2024-11-20
**Status:** Ready for Implementation
