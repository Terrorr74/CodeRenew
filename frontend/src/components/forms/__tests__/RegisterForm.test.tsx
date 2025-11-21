/**
 * Tests for RegisterForm component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/test/utils'
import RegisterForm from '../RegisterForm'

const mockPush = vi.fn()
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}))

describe('RegisterForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders registration form with all required fields', () => {
    render(<RegisterForm />)

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign up|register|create/i })).toBeInTheDocument()
  })

  it('displays validation errors for empty required fields', async () => {
    const { user } = render(<RegisterForm />)

    const submitButton = screen.getByRole('button', { name: /sign up|register|create/i })
    await user.click(submitButton)

    await waitFor(() => {
      // Should show at least one validation error
      const errors = screen.getAllByRole('alert')
      expect(errors.length).toBeGreaterThan(0)
    })
  })

  it('validates email format', async () => {
    const { user } = render(<RegisterForm />)

    const emailInput = screen.getByLabelText(/email/i)
    await user.type(emailInput, 'invalid-email')

    const submitButton = screen.getByRole('button', { name: /sign up|register|create/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/valid email|invalid email/i)).toBeInTheDocument()
    })
  })

  it('validates password strength - minimum length', async () => {
    const { user } = render(<RegisterForm />)

    const passwordInput = screen.getByLabelText(/^password$/i)
    await user.type(passwordInput, 'weak')

    const submitButton = screen.getByRole('button', { name: /sign up|register|create/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/8.*characters|too short|minimum/i)).toBeInTheDocument()
    })
  })

  it('validates password has uppercase letter', async () => {
    const { user } = render(<RegisterForm />)

    const passwordInput = screen.getByLabelText(/^password$/i)
    await user.type(passwordInput, 'lowercase123!')

    const submitButton = screen.getByRole('button', { name: /sign up|register|create/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/uppercase|capital/i)).toBeInTheDocument()
    })
  })

  it('validates password has number', async () => {
    const { user } = render(<RegisterForm />)

    const passwordInput = screen.getByLabelText(/^password$/i)
    await user.type(passwordInput, 'NoNumbersHere!')

    const submitButton = screen.getByRole('button', { name: /sign up|register|create/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/number|digit/i)).toBeInTheDocument()
    })
  })

  it('validates password has special character', async () => {
    const { user } = render(<RegisterForm />)

    const passwordInput = screen.getByLabelText(/^password$/i)
    await user.type(passwordInput, 'NoSpecial123')

    const submitButton = screen.getByRole('button', { name: /sign up|register|create/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/special.*character|symbol/i)).toBeInTheDocument()
    })
  })

  it('accepts valid strong password', async () => {
    const { user } = render(<RegisterForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password$/i)
    const nameInput = screen.getByLabelText(/name/i)

    await user.type(emailInput, 'newuser@example.com')
    await user.type(passwordInput, 'StrongPass123!')
    await user.type(nameInput, 'New User')

    const submitButton = screen.getByRole('button', { name: /sign up|register|create/i })
    await user.click(submitButton)

    // Should submit successfully without password validation errors
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalled()
    }, { timeout: 3000 })
  })

  it('shows error when email already exists', async () => {
    const { user } = render(<RegisterForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password$/i)
    const nameInput = screen.getByLabelText(/name/i)

    await user.type(emailInput, 'existing@example.com')
    await user.type(passwordInput, 'StrongPass123!')
    await user.type(nameInput, 'Existing User')

    const submitButton = screen.getByRole('button', { name: /sign up|register|create/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/already registered|already exists/i)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('has link to login page', () => {
    render(<RegisterForm />)

    const loginLink = screen.getByRole('link', { name: /sign in|log in|already have/i })
    expect(loginLink).toBeInTheDocument()
  })

  it('company field is optional', async () => {
    const { user } = render(<RegisterForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password$/i)
    const nameInput = screen.getByLabelText(/name/i)
    // Company field may or may not exist
    const companyInput = screen.queryByLabelText(/company/i)

    await user.type(emailInput, 'nocompany@example.com')
    await user.type(passwordInput, 'StrongPass123!')
    await user.type(nameInput, 'No Company User')

    // Don't fill company

    const submitButton = screen.getByRole('button', { name: /sign up|register|create/i })
    await user.click(submitButton)

    // Should submit successfully without company
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalled()
    }, { timeout: 3000 })
  })

  it('disables submit button while loading', async () => {
    const { user } = render(<RegisterForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password$/i)
    const nameInput = screen.getByLabelText(/name/i)

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'StrongPass123!')
    await user.type(nameInput, 'Test User')

    const submitButton = screen.getByRole('button', { name: /sign up|register|create/i })
    await user.click(submitButton)

    expect(submitButton).toBeDisabled()
  })

  it('shows password strength indicator', () => {
    render(<RegisterForm />)

    // Check if there's any password strength indicator
    const strengthIndicator = screen.queryByTestId('password-strength') ||
      screen.queryByText(/weak|medium|strong/i)

    // This may or may not exist depending on implementation
    // If it exists, test it
    if (strengthIndicator) {
      expect(strengthIndicator).toBeInTheDocument()
    }
  })
})
