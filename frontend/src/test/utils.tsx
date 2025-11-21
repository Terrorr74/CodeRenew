/**
 * Test utilities for React Testing Library
 */
import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

// Import providers that wrap the app
// import { AuthProvider } from '@/contexts/AuthContext'

interface AllTheProvidersProps {
  children: React.ReactNode
}

/**
 * Wrapper component that includes all providers needed for testing
 */
function AllTheProviders({ children }: AllTheProvidersProps) {
  return (
    // Add providers here as needed
    // <AuthProvider>
    <>{children}</>
    // </AuthProvider>
  )
}

/**
 * Custom render function that wraps components with necessary providers
 */
function customRender(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return {
    user: userEvent.setup(),
    ...render(ui, { wrapper: AllTheProviders, ...options }),
  }
}

// Re-export everything from testing library
export * from '@testing-library/react'
export { customRender as render }
export { userEvent }

/**
 * Helper to wait for async operations
 */
export const waitForLoadingToFinish = () =>
  new Promise((resolve) => setTimeout(resolve, 0))

/**
 * Mock localStorage for testing
 */
export const mockLocalStorage = () => {
  const store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      Object.keys(store).forEach((key) => delete store[key])
    },
  }
}

/**
 * Create a mock router for testing
 */
export const createMockRouter = (overrides = {}) => ({
  push: vi.fn(),
  replace: vi.fn(),
  prefetch: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  ...overrides,
})

// Import vi for mock functions
import { vi } from 'vitest'
