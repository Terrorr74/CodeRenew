'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { ScanResults } from '@/components/scans/ScanResults'
import { apiClient } from '@/lib/api/client'

export default function ScanPage() {
    const params = useParams()
    const [scan, setScan] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        const fetchScan = async () => {
            try {
                const data = await apiClient.get(`/scans/${params.id}`)
                setScan(data)
            } catch (err) {
                setError('Failed to load scan results')
                console.error(err)
            } finally {
                setLoading(false)
            }
        }

        if (params.id) {
            fetchScan()
        }
    }, [params.id])

    if (loading) {
        return (
            <ProtectedRoute>
                <DashboardLayout>
                    <div className="flex justify-center items-center h-64">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                    </div>
                </DashboardLayout>
            </ProtectedRoute>
        )
    }

    if (error || !scan) {
        return (
            <ProtectedRoute>
                <DashboardLayout>
                    <div className="text-red-600 p-4">{error || 'Scan not found'}</div>
                </DashboardLayout>
            </ProtectedRoute>
        )
    }

    return (
        <ProtectedRoute>
            <DashboardLayout>
                <ScanResults scan={scan} />
            </DashboardLayout>
        </ProtectedRoute>
    )
}
