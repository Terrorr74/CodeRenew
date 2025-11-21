'use client'

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { authApi } from '@/lib/api/auth'
import { ProfileForm } from '@/components/forms/ProfileForm'
import { PasswordChangeForm } from '@/components/forms/PasswordChangeForm'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'

export default function ProfilePage() {
    const { user, refreshUser } = useAuth()
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

    const handleProfileUpdate = async (data: any) => {
        try {
            setMessage(null)
            await authApi.updateProfile(data)
            await refreshUser()
            setMessage({ type: 'success', text: 'Profile updated successfully' })
        } catch (err: any) {
            setMessage({
                type: 'error',
                text: err.response?.data?.detail || 'Failed to update profile'
            })
        }
    }

    const handlePasswordChange = async (data: any) => {
        try {
            setMessage(null)
            await authApi.changePassword(data)
            setMessage({ type: 'success', text: 'Password changed successfully' })
        } catch (err: any) {
            setMessage({
                type: 'error',
                text: err.response?.data?.detail || 'Failed to change password'
            })
        }
    }

    if (!user) return null

    return (
        <ProtectedRoute>
            <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                <h1 className="text-3xl font-bold text-secondary-900 mb-8">Your Profile</h1>

                {message && (
                    <div className={`p-4 rounded-md mb-6 ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                        }`}>
                        {message.text}
                    </div>
                )}

                <div className="bg-white shadow rounded-lg overflow-hidden mb-8">
                    <div className="px-4 py-5 sm:p-6">
                        <h2 className="text-lg font-medium text-secondary-900 mb-4">Personal Information</h2>
                        <ProfileForm user={user} onSubmit={handleProfileUpdate} />
                    </div>
                </div>

                <div className="bg-white shadow rounded-lg overflow-hidden">
                    <div className="px-4 py-5 sm:p-6">
                        <h2 className="text-lg font-medium text-secondary-900 mb-4">Security</h2>
                        <PasswordChangeForm onSubmit={handlePasswordChange} />
                    </div>
                </div>
            </div>
        </ProtectedRoute>
    )
}
