'use client'

/**
 * Protected Route Component
 * Wraps components that require authentication
 * Redirects to login if user is not authenticated
 */
import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

interface ProtectedRouteProps {
    children: React.ReactNode
    fallback?: React.ReactNode
}

export function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
    const { isAuthenticated, loading, user } = useAuth()
    const router = useRouter()
    const pathname = usePathname()

    useEffect(() => {
        if (!loading && !isAuthenticated) {
            // Store the intended destination to redirect after login
            const returnUrl = encodeURIComponent(pathname)
            router.push(`/auth/login?returnUrl=${returnUrl}`)
        } else if (!loading && isAuthenticated && user && !user.onboarding_completed) {
            // Redirect to onboarding if user hasn't completed it
            // But don't redirect if already on the onboarding page
            if (pathname !== '/onboarding') {
                router.push('/onboarding')
            }
        }
    }, [isAuthenticated, loading, user, router, pathname])

    // Show loading state while checking authentication
    if (loading) {
        return (
            fallback || (
                <div className="min-h-screen flex items-center justify-center bg-secondary-50">
                    <div className="text-center">
                        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
                        <p className="text-secondary-600">Loading...</p>
                    </div>
                </div>
            )
        )
    }

    // Don't render children if not authenticated
    if (!isAuthenticated) {
        return null
    }

    // Don't render children if onboarding not completed (except on onboarding page)
    if (user && !user.onboarding_completed && pathname !== '/onboarding') {
        return null
    }

    return <>{children}</>
}

