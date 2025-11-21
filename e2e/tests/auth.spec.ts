/**
 * E2E tests for authentication flows
 */
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test.describe('Registration', () => {
    test('should register a new user successfully', async ({ page }) => {
      await page.goto('/auth/register')

      // Fill registration form
      await page.fill('input[name="email"], input[type="email"]', `test${Date.now()}@example.com`)
      await page.fill('input[name="password"], input[type="password"]', 'StrongPass123!')
      await page.fill('input[name="name"]', 'Test User')

      // Submit form
      await page.click('button[type="submit"]')

      // Should redirect to dashboard or onboarding
      await expect(page).toHaveURL(/\/(dashboard|onboarding)/, { timeout: 10000 })
    })

    test('should show error for existing email', async ({ page }) => {
      await page.goto('/auth/register')

      // Fill with existing email
      await page.fill('input[name="email"], input[type="email"]', 'existing@example.com')
      await page.fill('input[name="password"], input[type="password"]', 'StrongPass123!')
      await page.fill('input[name="name"]', 'Existing User')

      await page.click('button[type="submit"]')

      // Should show error message
      await expect(page.locator('text=/already registered|already exists/i')).toBeVisible({ timeout: 5000 })
    })

    test('should validate password strength', async ({ page }) => {
      await page.goto('/auth/register')

      // Fill with weak password
      await page.fill('input[name="email"], input[type="email"]', 'weak@example.com')
      await page.fill('input[name="password"], input[type="password"]', 'weak')

      await page.click('button[type="submit"]')

      // Should show password validation error
      await expect(page.locator('text=/8.*characters|too short|weak/i')).toBeVisible()
    })
  })

  test.describe('Login', () => {
    test('should login with valid credentials', async ({ page }) => {
      await page.goto('/auth/login')

      await page.fill('input[name="email"], input[type="email"]', 'test@example.com')
      await page.fill('input[name="password"], input[type="password"]', 'ValidPass123!')

      await page.click('button[type="submit"]')

      // Should redirect to dashboard
      await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 })
    })

    test('should show error for invalid credentials', async ({ page }) => {
      await page.goto('/auth/login')

      await page.fill('input[name="email"], input[type="email"]', 'wrong@example.com')
      await page.fill('input[name="password"], input[type="password"]', 'WrongPass123!')

      await page.click('button[type="submit"]')

      // Should show error message
      await expect(page.locator('text=/incorrect|invalid|error/i')).toBeVisible({ timeout: 5000 })
    })

    test('should navigate to forgot password', async ({ page }) => {
      await page.goto('/auth/login')

      await page.click('text=/forgot.*password/i')

      await expect(page).toHaveURL(/\/auth\/forgot-password/)
    })

    test('should navigate to register', async ({ page }) => {
      await page.goto('/auth/login')

      await page.click('text=/sign up|register|create.*account/i')

      await expect(page).toHaveURL(/\/auth\/register/)
    })
  })

  test.describe('Password Reset', () => {
    test('should request password reset', async ({ page }) => {
      await page.goto('/auth/forgot-password')

      await page.fill('input[name="email"], input[type="email"]', 'test@example.com')

      await page.click('button[type="submit"]')

      // Should show success message
      await expect(page.locator('text=/reset link|email sent|check your email/i')).toBeVisible({ timeout: 5000 })
    })

    test('should show message for non-existent email (no enumeration)', async ({ page }) => {
      await page.goto('/auth/forgot-password')

      await page.fill('input[name="email"], input[type="email"]', 'nonexistent@example.com')

      await page.click('button[type="submit"]')

      // Should show same message to prevent enumeration
      await expect(page.locator('text=/reset link|email sent|check your email/i')).toBeVisible({ timeout: 5000 })
    })
  })

  test.describe('Protected Routes', () => {
    test('should redirect to login when accessing protected route', async ({ page }) => {
      await page.goto('/dashboard')

      // Should redirect to login
      await expect(page).toHaveURL(/\/auth\/login/, { timeout: 5000 })
    })

    test('should access protected route when authenticated', async ({ page }) => {
      // Login first
      await page.goto('/auth/login')
      await page.fill('input[name="email"], input[type="email"]', 'test@example.com')
      await page.fill('input[name="password"], input[type="password"]', 'ValidPass123!')
      await page.click('button[type="submit"]')

      // Wait for redirect to dashboard
      await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 })

      // Should be on dashboard
      await expect(page.locator('text=/dashboard|welcome|overview/i')).toBeVisible()
    })
  })
})
