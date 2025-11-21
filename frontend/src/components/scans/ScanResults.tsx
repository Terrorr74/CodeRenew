'use client'

import { useState } from 'react'
import { apiClient } from '@/lib/api/client'

interface ScanResult {
    id: number
    severity: string
    issue_type: string
    file_path: string
    description: string
    recommendation: string
}

interface Scan {
    id: number
    status: string
    risk_level: string
    results: ScanResult[]
    created_at: string
}

interface ScanResultsProps {
    scan: Scan
}

export function ScanResults({ scan }: ScanResultsProps) {
    const [isDownloading, setIsDownloading] = useState(false)

    const handleDownloadPDF = async () => {
        try {
            setIsDownloading(true)
            const response = await apiClient.get<Blob>(`/scans/${scan.id}/report`, {
                responseType: 'blob'
            })

            // Create blob link to download
            const url = window.URL.createObjectURL(new Blob([response as any]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `coderenew_report_${scan.id}.pdf`)
            document.body.appendChild(link)
            link.click()
            link.parentNode?.removeChild(link)
        } catch (error) {
            console.error('Failed to download PDF:', error)
            alert('Failed to download PDF report. Please try again.')
        } finally {
            setIsDownloading(false)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-secondary-900">Scan Results</h2>
                <button
                    onClick={handleDownloadPDF}
                    disabled={isDownloading}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 flex items-center gap-2"
                >
                    {isDownloading ? 'Generating...' : 'Download PDF Report'}
                </button>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <ul className="divide-y divide-gray-200">
                    {scan.results.map((result) => (
                        <li key={result.id} className="px-6 py-4">
                            <div className="flex items-center justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${result.severity === 'critical' ? 'bg-red-100 text-red-800' :
                                                result.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                                                    'bg-blue-100 text-blue-800'
                                            }`}>
                                            {result.severity.toUpperCase()}
                                        </span>
                                        <span className="text-sm font-medium text-gray-900">
                                            {result.issue_type}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-500 mb-2">{result.description}</p>
                                    <p className="text-sm text-gray-600">
                                        <span className="font-medium">File:</span> {result.file_path}
                                    </p>
                                </div>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    )
}
