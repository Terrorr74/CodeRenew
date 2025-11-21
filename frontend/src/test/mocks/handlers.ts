/**
 * MSW request handlers for API mocking
 */
import { http, HttpResponse } from 'msw'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Mock user data
const mockUser = {
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  company: 'Test Company',
  is_verified: true,
  onboarding_completed: true,
  created_at: '2024-01-01T00:00:00Z',
}

// Mock token
const mockToken = 'mock-jwt-token-for-testing'

export const handlers = [
  // Auth endpoints
  http.post(`${API_URL}/api/v1/auth/register`, async ({ request }) => {
    const body = await request.json() as { email: string; password: string; name: string }

    if (!body.email || !body.password) {
      return HttpResponse.json(
        { detail: 'Email and password are required' },
        { status: 422 }
      )
    }

    if (body.email === 'existing@example.com') {
      return HttpResponse.json(
        { detail: 'Email already registered' },
        { status: 400 }
      )
    }

    return HttpResponse.json({
      access_token: mockToken,
      token_type: 'bearer',
      user: {
        ...mockUser,
        email: body.email,
        name: body.name || 'New User',
        is_verified: false,
        onboarding_completed: false,
      },
    }, { status: 201 })
  }),

  http.post(`${API_URL}/api/v1/auth/login`, async ({ request }) => {
    const body = await request.json() as { email: string; password: string }

    if (body.email === 'locked@example.com') {
      return HttpResponse.json(
        { detail: 'Account is locked due to multiple failed login attempts' },
        { status: 403 }
      )
    }

    if (body.email === 'test@example.com' && body.password === 'ValidPass123!') {
      return HttpResponse.json({
        access_token: mockToken,
        token_type: 'bearer',
      })
    }

    return HttpResponse.json(
      { detail: 'Incorrect email or password' },
      { status: 401 }
    )
  }),

  http.get(`${API_URL}/api/v1/auth/me`, ({ request }) => {
    const authHeader = request.headers.get('Authorization')

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return HttpResponse.json(
        { detail: 'Not authenticated' },
        { status: 401 }
      )
    }

    return HttpResponse.json(mockUser)
  }),

  http.put(`${API_URL}/api/v1/auth/profile`, async ({ request }) => {
    const authHeader = request.headers.get('Authorization')

    if (!authHeader) {
      return HttpResponse.json({ detail: 'Not authenticated' }, { status: 401 })
    }

    const body = await request.json() as Partial<typeof mockUser>
    return HttpResponse.json({ ...mockUser, ...body })
  }),

  http.post(`${API_URL}/api/v1/auth/change-password`, async ({ request }) => {
    const authHeader = request.headers.get('Authorization')

    if (!authHeader) {
      return HttpResponse.json({ detail: 'Not authenticated' }, { status: 401 })
    }

    const body = await request.json() as { old_password: string; new_password: string }

    if (body.old_password !== 'ValidPass123!') {
      return HttpResponse.json({ detail: 'Incorrect old password' }, { status: 400 })
    }

    return HttpResponse.json({ message: 'Password updated successfully' })
  }),

  http.post(`${API_URL}/api/v1/auth/forgot-password`, () => {
    return HttpResponse.json({ message: 'If the email exists, a reset link has been sent' })
  }),

  http.post(`${API_URL}/api/v1/auth/reset-password`, async ({ request }) => {
    const body = await request.json() as { token: string; new_password: string }

    if (body.token === 'invalid-token') {
      return HttpResponse.json({ detail: 'Invalid or expired token' }, { status: 400 })
    }

    return HttpResponse.json({ message: 'Password reset successfully' })
  }),

  http.put(`${API_URL}/api/v1/auth/onboarding/complete`, async ({ request }) => {
    const authHeader = request.headers.get('Authorization')

    if (!authHeader) {
      return HttpResponse.json({ detail: 'Not authenticated' }, { status: 401 })
    }

    const body = await request.json() as { name: string; company: string }
    return HttpResponse.json({
      ...mockUser,
      name: body.name,
      company: body.company,
      onboarding_completed: true,
    })
  }),

  // Sites endpoints
  http.get(`${API_URL}/api/v1/sites`, ({ request }) => {
    const authHeader = request.headers.get('Authorization')

    if (!authHeader) {
      return HttpResponse.json({ detail: 'Not authenticated' }, { status: 401 })
    }

    return HttpResponse.json([
      {
        id: 1,
        url: 'https://example.com',
        name: 'Example Site',
        user_id: 1,
        created_at: '2024-01-01T00:00:00Z',
      },
    ])
  }),

  // Scans endpoints
  http.get(`${API_URL}/api/v1/scans`, ({ request }) => {
    const authHeader = request.headers.get('Authorization')

    if (!authHeader) {
      return HttpResponse.json({ detail: 'Not authenticated' }, { status: 401 })
    }

    return HttpResponse.json([
      {
        id: 1,
        site_id: 1,
        status: 'completed',
        compatibility_score: 85,
        created_at: '2024-01-01T00:00:00Z',
      },
    ])
  }),

  // Health check
  http.get(`${API_URL}/health`, () => {
    return HttpResponse.json({
      status: 'healthy',
      service: 'coderenew-api',
      version: '1.0.0',
    })
  }),
]
