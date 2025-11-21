/**
 * Tests for LoginForm component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/test/utils'
import LoginForm from '../LoginForm'

// Mock next/navigation
const mockPush = vi.fn()
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}))

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form with email and password fields', () => {
    render(<LoginForm />)

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in|log in/i })).toBeInTheDocument()
  })

  it('displays validation errors for empty fields', async () => {
    const { user } = render(<LoginForm />)

    // Submit empty form
    const submitButton = screen.getByRole('button', { name: /sign in|log in/i })
    await user.click(submitButton)

    // Check for validation errors
    await waitFor(() => {
      expect(screen.getByText(/email.*required|please enter.*email/i)).toBeInTheDocument()
    })
  })

  it('displays error for invalid email format', async () => {
    const { user } = render(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    await user.type(emailInput, 'invalid-email')

    const submitButton = screen.getByRole('button', { name: /sign in|log in/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/valid email|invalid email/i)).toBeInTheDocument()
    })
  })

  it('allows typing in email and password fields', async () => {
    const { user } = render(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'ValidPass123!')

    expect(emailInput).toHaveValue('test@example.com')
    expect(passwordInput).toHaveValue('ValidPass123!')
  })

  it('submits form with valid credentials', async () => {
    const { user } = render(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in|log in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'ValidPass123!')
    await user.click(submitButton)

    // Wait for form submission
    await waitFor(() => {
      // Check that either redirect happened or success state
      expect(mockPush).toHaveBeenCalled()
    }, { timeout: 3000 })
  })

  it('displays error message for invalid credentials', async () => {
    const { user } = render(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in|log in/i })

    await user.type(emailInput, 'wrong@example.com')
    await user.type(passwordInput, 'WrongPass123!')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/incorrect|invalid|error/i)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('displays locked account message', async () => {
    const { user } = render(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in|log in/i })

    await user.type(emailInput, 'locked@example.com')
    await user.type(passwordInput, 'AnyPass123!')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/locked/i)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('has link to forgot password page', () => {
    render(<LoginForm />)

    const forgotPasswordLink = screen.getByRole('link', { name: /forgot.*password/i })
    expect(forgotPasswordLink).toBeInTheDocument()
  })

  it('has link to register page', () => {
    render(<LoginForm />)

    const registerLink = screen.getByRole('link', { name: /sign up|register|create.*account/i })
    expect(registerLink).toBeInTheDocument()
  })

  it('disables submit button while loading', async () => {
    const { user } = render(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /sign in|log in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'ValidPass123!')
    await user.click(submitButton)

    // Button should be disabled during submission
    expect(submitButton).toBeDisabled()
  })

  it('password field has type="password"', () => {
    render(<LoginForm />)

    const passwordInput = screen.getByLabelText(/password/i)
    expect(passwordInput).toHaveAttribute('type', 'password')
  })
})
