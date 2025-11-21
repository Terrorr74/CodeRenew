'use client'

import { DashboardLayout } from '@/components/layouts/DashboardLayout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { NewScanForm } from '@/components/scans/NewScanForm'

export default function NewScanPage() {
    return (
        <ProtectedRoute>
            <DashboardLayout>
                <NewScanForm />
            </DashboardLayout>
        </ProtectedRoute>
    )
}
