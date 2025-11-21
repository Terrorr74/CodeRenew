'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const onboardingSchema = z.object({
    name: z.string().min(1, 'Name is required').max(255, 'Name is too long'),
    company: z.string().max(255, 'Company name is too long').optional(),
})

type OnboardingFormData = z.infer<typeof onboardingSchema>

interface OnboardingFormProps {
    onSubmit: (data: OnboardingFormData) => void
    initialName?: string
    initialCompany?: string
}

export function OnboardingForm({ onSubmit, initialName, initialCompany }: OnboardingFormProps) {
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<OnboardingFormData>({
        resolver: zodResolver(onboardingSchema),
        defaultValues: {
            name: initialName || '',
            company: initialCompany || '',
        },
    })

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
                <label
                    htmlFor="name"
                    className="block text-sm font-medium text-secondary-700 mb-1"
                >
                    Full Name <span className="text-red-500">*</span>
                </label>
                <input
                    {...register('name')}
                    type="text"
                    id="name"
                    className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="John Doe"
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
                    Company <span className="text-secondary-400">(optional)</span>
                </label>
                <input
                    {...register('company')}
                    type="text"
                    id="company"
                    className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Acme Inc."
                />
                {errors.company && (
                    <p className="mt-1 text-sm text-red-600">{errors.company.message}</p>
                )}
            </div>

            <button
                type="submit"
                disabled={isSubmitting}
                className="w-full px-4 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
                {isSubmitting ? 'Saving...' : 'Complete Setup'}
            </button>
        </form>
    )
}
