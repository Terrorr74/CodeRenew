'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { User } from '@/lib/api/auth'

const profileSchema = z.object({
    name: z.string().min(1, 'Name is required').max(255, 'Name is too long'),
    company: z.string().max(255, 'Company name is too long').optional(),
    email: z.string().email('Invalid email address'),
})

type ProfileFormData = z.infer<typeof profileSchema>

interface ProfileFormProps {
    user: User
    onSubmit: (data: ProfileFormData) => void
}

export function ProfileForm({ user, onSubmit }: ProfileFormProps) {
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<ProfileFormData>({
        resolver: zodResolver(profileSchema),
        defaultValues: {
            name: user.name,
            company: user.company || '',
            email: user.email,
        },
    })

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                    <label
                        htmlFor="name"
                        className="block text-sm font-medium text-secondary-700 mb-1"
                    >
                        Full Name
                    </label>
                    <input
                        {...register('name')}
                        type="text"
                        id="name"
                        className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                    {errors.name && (
                        <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                    )}
                </div>

                <div>
                    <label
                        htmlFor="company"
                        className="block text-sm font-medium text-secondary-700 mb-1"
                    >
                        Company
                    </label>
                    <input
                        {...register('company')}
                        type="text"
                        id="company"
                        className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                    {errors.company && (
                        <p className="mt-1 text-sm text-red-600">{errors.company.message}</p>
                    )}
                </div>

                <div className="sm:col-span-2">
                    <label
                        htmlFor="email"
                        className="block text-sm font-medium text-secondary-700 mb-1"
                    >
                        Email Address
                    </label>
                    <input
                        {...register('email')}
                        type="email"
                        id="email"
                        className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                    {errors.email && (
                        <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                    )}
                </div>
            </div>

            <div className="flex justify-end">
                <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isSubmitting ? 'Saving...' : 'Save Changes'}
                </button>
            </div>
        </form>
    )
}
