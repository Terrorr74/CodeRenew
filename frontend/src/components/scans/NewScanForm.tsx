'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api/client'

interface Site {
    id: number
    url: string
    name: string
}

export function NewScanForm() {
    const router = useRouter()
    const [sites, setSites] = useState<Site[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [showUpgradeModal, setShowUpgradeModal] = useState(false)

    const [formData, setFormData] = useState({
        siteId: '',
        versionFrom: '6.0',
        versionTo: '6.4',
        file: null as File | null
    })

    useEffect(() => {
        const fetchSites = async () => {
            try {
                const response = await apiClient.get<Site[]>('/sites')
                setSites(response.data)
            } catch (err) {
                console.error('Failed to fetch sites', err)
            }
        }
        fetchSites()
    }, [])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        if (!formData.file || !formData.siteId) {
            setError('Please fill in all fields')
            setLoading(false)
            return
        }

        const data = new FormData()
        data.append('file', formData.file)
        data.append('site_id', formData.siteId)
        data.append('wordpress_version_from', formData.versionFrom)
        data.append('wordpress_version_to', formData.versionTo)

        try {
            const response = await apiClient.post('/scans/upload', data, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })
            router.push(`/scans/${response.data.id}`)
        } catch (err: any) {
            if (err.response?.status === 403) {
                setShowUpgradeModal(true)
            } else {
                setError(err.response?.data?.detail || 'Failed to start scan')
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-6">Start New Scan</h2>

            {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded mb-6">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Select Site
                    </label>
                    <select
                        value={formData.siteId}
                        onChange={(e) => setFormData({ ...formData, siteId: e.target.value })}
                        className="w-full border border-gray-300 rounded-md p-2"
                        required
                    >
                        <option value="">Select a site...</option>
                        {sites.map((site) => (
                            <option key={site.id} value={site.id}>
                                {site.name} ({site.url})
                            </option>
                        ))}
                    </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Current Version
                        </label>
                        <input
                            type="text"
                            value={formData.versionFrom}
                            onChange={(e) => setFormData({ ...formData, versionFrom: e.target.value })}
                            className="w-full border border-gray-300 rounded-md p-2"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Target Version
                        </label>
                        <input
                            type="text"
                            value={formData.versionTo}
                            onChange={(e) => setFormData({ ...formData, versionTo: e.target.value })}
                            className="w-full border border-gray-300 rounded-md p-2"
                            required
                        />
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Upload Plugin/Theme (ZIP)
                    </label>
                    <input
                        type="file"
                        accept=".zip"
                        onChange={(e) => setFormData({ ...formData, file: e.target.files?.[0] || null })}
                        className="w-full border border-gray-300 rounded-md p-2"
                        required
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:opacity-50"
                >
                    {loading ? 'Uploading...' : 'Start Scan'}
                </button>
            </form>

            {showUpgradeModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-lg p-8 max-w-md w-full text-center">
                        <h3 className="text-2xl font-bold text-gray-900 mb-4">Daily Limit Reached</h3>
                        <p className="text-gray-600 mb-6">
                            You've reached your daily scan limit on the Free plan. Upgrade to Pro for unlimited scans and detailed PDF reports.
                        </p>
                        <div className="space-y-3">
                            <button
                                onClick={() => alert('Redirect to Stripe Checkout')}
                                className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 font-bold"
                            >
                                Upgrade to Pro
                            </button>
                            <button
                                onClick={() => setShowUpgradeModal(false)}
                                className="w-full text-gray-500 hover:text-gray-700"
                            >
                                Maybe Later
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
