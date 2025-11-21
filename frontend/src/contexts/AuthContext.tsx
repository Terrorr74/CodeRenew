'use client'

/**
 * Authentication Context
 * Provides authentication state and methods throughout the application
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi, User } from '@/lib/api/auth'

interface AuthContextType {
    user: User | null
    loading: boolean
    login: (email: string, password: string) => Promise<void>
    logout: () => void
    refreshUser: () => Promise<void>
    isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)

    // Check if user is authenticated on mount
    useEffect(() => {
        const initAuth = async () => {
            try {
                const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null

                if (token) {
                    // Verify token is still valid by fetching user
                    const currentUser = await authApi.getCurrentUser()
                    setUser(currentUser)
                }
            } catch (error) {
                // Token is invalid or expired
                console.error('Auth initialization error:', error)
                if (typeof window !== 'undefined') {
                    localStorage.removeItem('access_token')
                }
            } finally {
                setLoading(false)
            }
        }

        initAuth()
    }, [])

    const login = async (email: string, password: string) => {
        const response = await authApi.login({ email, password })

        // Token is already set by authApi.login
        // Now fetch the user data
        const currentUser = await authApi.getCurrentUser()
        setUser(currentUser)
    }

    const refreshUser = async () => {
        try {
            const currentUser = await authApi.getCurrentUser()
            setUser(currentUser)
        } catch (error) {
            console.error('Failed to refresh user:', error)
        }
    }

    const logout = () => {
        setUser(null)
        authApi.logout()
    }

    const value: AuthContextType = {
        user,
        loading,
        login,
        logout,
        refreshUser,
        isAuthenticated: !!user,
    }

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Hook to use authentication context
 * Must be used within AuthProvider
 */
export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}

