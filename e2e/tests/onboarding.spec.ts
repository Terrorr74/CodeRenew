/**
 * E2E tests for user onboarding flow
 */
import { test, expect } from '@playwright/test'

test.describe('Onboarding', () => {
  test.beforeEach(async ({ page }) => {
    // Register a new user to get to onboarding
    await page.goto('/auth/register')

    await page.fill('input[name="email"], input[type="email"]', `onboard${Date.now()}@example.com`)
    await page.fill('input[name="password"], input[type="password"]', 'StrongPass123!')
    await page.fill('input[name="name"]', 'Onboard User')

    await page.click('button[type="submit"]')

    // Wait for redirect
    await page.waitForURL(/\/(dashboard|onboarding)/, { timeout: 10000 })
  })

  test('should complete onboarding with required fields', async ({ page }) => {
    // If redirected to onboarding, fill it out
    if (page.url().includes('onboarding')) {
      await page.fill('input[name="name"]', 'Updated Name')
      await page.fill('input[name="company"]', 'Test Company')

      await page.click('button[type="submit"]')

      // Should redirect to dashboard
      await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 })
    }
  })

  test('should skip company field (optional)', async ({ page }) => {
    if (page.url().includes('onboarding')) {
      await page.fill('input[name="name"]', 'Solo Developer')
      // Leave company empty

      await page.click('button[type="submit"]')

      await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 })
    }
  })
})
