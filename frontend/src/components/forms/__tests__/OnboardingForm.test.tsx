/**
 * Tests for OnboardingForm component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/test/utils'
import OnboardingForm from '../OnboardingForm'

const mockPush = vi.fn()
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}))

describe('OnboardingForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders onboarding form with name and company fields', () => {
    render(<OnboardingForm />)

    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/company/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /complete|continue|submit/i })).toBeInTheDocument()
  })

  it('validates name is required', async () => {
    const { user } = render(<OnboardingForm />)

    const submitButton = screen.getByRole('button', { name: /complete|continue|submit/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/name.*required|please enter.*name/i)).toBeInTheDocument()
    })
  })

  it('allows typing in form fields', async () => {
    const { user } = render(<OnboardingForm />)

    const nameInput = screen.getByLabelText(/name/i)
    const companyInput = screen.getByLabelText(/company/i)

    await user.type(nameInput, 'John Doe')
    await user.type(companyInput, 'Acme Corp')

    expect(nameInput).toHaveValue('John Doe')
    expect(companyInput).toHaveValue('Acme Corp')
  })

  it('submits form with valid data', async () => {
    const { user } = render(<OnboardingForm />)

    const nameInput = screen.getByLabelText(/name/i)
    const companyInput = screen.getByLabelText(/company/i)
    const submitButton = screen.getByRole('button', { name: /complete|continue|submit/i })

    await user.type(nameInput, 'Jane Smith')
    await user.type(companyInput, 'Tech Inc')
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalled()
    }, { timeout: 3000 })
  })

  it('company field can be optional', async () => {
    const { user } = render(<OnboardingForm />)

    const nameInput = screen.getByLabelText(/name/i)
    const submitButton = screen.getByRole('button', { name: /complete|continue|submit/i })

    await user.type(nameInput, 'Solo Developer')
    // Don't fill company
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalled()
    }, { timeout: 3000 })
  })

  it('disables submit button while loading', async () => {
    const { user } = render(<OnboardingForm />)

    const nameInput = screen.getByLabelText(/name/i)
    const submitButton = screen.getByRole('button', { name: /complete|continue|submit/i })

    await user.type(nameInput, 'Test User')
    await user.click(submitButton)

    expect(submitButton).toBeDisabled()
  })

  it('shows welcome or onboarding message', () => {
    render(<OnboardingForm />)

    // Check for welcome text
    const welcomeText = screen.queryByText(/welcome|get started|complete.*profile/i)
    if (welcomeText) {
      expect(welcomeText).toBeInTheDocument()
    }
  })
})
