'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { OnboardingForm } from '@/components/forms/OnboardingForm'
import { authApi } from '@/lib/api/auth'
import { useAuth } from '@/contexts/AuthContext'

export default function OnboardingPage() {
    const router = useRouter()
    const { user, refreshUser } = useAuth()
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        // If user has already completed onboarding, redirect to dashboard
        if (user?.onboarding_completed) {
            router.push('/dashboard')
        }
    }, [user, router])

    const handleOnboardingComplete = async (data: { name: string; company?: string }) => {
        try {
            setError(null)
            await authApi.completeOnboarding(data)
            // Refresh user data to get updated onboarding_completed status
            await refreshUser()
            // Redirect to dashboard
            router.push('/dashboard')
        } catch (err: any) {
            console.error('Onboarding error:', err)
            setError(err.response?.data?.detail || 'Failed to complete onboarding. Please try again.')
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-100 flex items-center justify-center px-4">
            <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
                <div className="text-center mb-8">
                    <div className="mb-4">
                        <span className="text-5xl">👋</span>
                    </div>
                    <h1 className="text-3xl font-bold text-secondary-900 mb-2">
                        Welcome to CodeRenew!
                    </h1>
                    <p className="text-secondary-600">
                        Let's get to know you better. This will only take a moment.
                    </p>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-sm text-red-600">{error}</p>
                    </div>
                )}

                <OnboardingForm
                    onSubmit={handleOnboardingComplete}
                    initialName={user?.name}
                    initialCompany={user?.company}
                />

                <div className="mt-6 text-center">
                    <p className="text-xs text-secondary-500">
                        Your information helps us provide a better experience
                    </p>
                </div>
            </div>
        </div>
    )
}
