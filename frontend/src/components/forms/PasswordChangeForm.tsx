'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const passwordChangeSchema = z.object({
    old_password: z.string().min(1, 'Current password is required'),
    new_password: z.string().min(8, 'Password must be at least 8 characters'),
    confirm_password: z.string(),
}).refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords don't match",
    path: ['confirm_password'],
})

type PasswordChangeFormData = z.infer<typeof passwordChangeSchema>

interface PasswordChangeFormProps {
    onSubmit: (data: { old_password: string; new_password: string }) => void
}

export function PasswordChangeForm({ onSubmit }: PasswordChangeFormProps) {
    const {
        register,
        handleSubmit,
        reset,
        formState: { errors, isSubmitting },
    } = useForm<PasswordChangeFormData>({
        resolver: zodResolver(passwordChangeSchema),
    })

    const handleFormSubmit = async (data: PasswordChangeFormData) => {
        await onSubmit({
            old_password: data.old_password,
            new_password: data.new_password,
        })
        reset()
    }

    return (
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
            <div>
                <label
                    htmlFor="old_password"
                    className="block text-sm font-medium text-secondary-700 mb-1"
                >
                    Current Password
                </label>
                <input
                    {...register('old_password')}
                    type="password"
                    id="old_password"
                    className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                {errors.old_password && (
                    <p className="mt-1 text-sm text-red-600">{errors.old_password.message}</p>
                )}
            </div>

            <div>
                <label
                    htmlFor="new_password"
                    className="block text-sm font-medium text-secondary-700 mb-1"
                >
                    New Password
                </label>
                <input
                    {...register('new_password')}
                    type="password"
                    id="new_password"
                    className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                {errors.new_password && (
                    <p className="mt-1 text-sm text-red-600">{errors.new_password.message}</p>
                )}
            </div>

            <div>
                <label
                    htmlFor="confirm_password"
                    className="block text-sm font-medium text-secondary-700 mb-1"
                >
                    Confirm New Password
                </label>
                <input
                    {...register('confirm_password')}
                    type="password"
                    id="confirm_password"
                    className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                {errors.confirm_password && (
                    <p className="mt-1 text-sm text-red-600">{errors.confirm_password.message}</p>
                )}
            </div>

            <div className="flex justify-end">
                <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isSubmitting ? 'Change Password' : 'Change Password'}
                </button>
            </div>
        </form>
    )
}
