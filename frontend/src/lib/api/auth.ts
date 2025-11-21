/**
 * Authentication API
 * API methods for user authentication
 */
import { apiClient } from './client'

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  name?: string
  company?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface AuthResponseWithUser extends AuthResponse {
  user: User
}

export interface User {
  id: number
  email: string
  name: string
  company?: string
  is_verified: boolean
  onboarding_completed: boolean
  created_at: string
}

export interface OnboardingData {
  name: string
  company?: string
}

export const authApi = {
  /**
   * Login user
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      '/auth/login',
      credentials
    )
    apiClient.setToken(response.access_token)
    return response
  },

  /**
   * Register new user (returns token for auto-login)
   */
  async register(data: RegisterData): Promise<AuthResponseWithUser> {
    const response = await apiClient.post<AuthResponseWithUser>('/auth/register', data)
    apiClient.setToken(response.access_token)
    return response
  },

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/auth/me')
  },

  /**
   * Complete user onboarding
   */
  async completeOnboarding(data: OnboardingData): Promise<User> {
    return apiClient.put<User>('/auth/onboarding/complete', data)
  },

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    return apiClient.put<User>('/auth/profile', data)
  },

  /**
   * Change password
   */
  async changePassword(data: { old_password: string; new_password: string }): Promise<void> {
    return apiClient.post('/auth/change-password', data)
  },

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<void> {
    return apiClient.post('/auth/forgot-password', { email })
  },

  /**
   * Reset password
   */
  async resetPassword(token: string, new_password: string): Promise<void> {
    return apiClient.post('/auth/reset-password', { token, new_password })
  },

  /**
   * Logout user
   */
  logout(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      window.location.href = '/auth/login'
    }
  },
}

