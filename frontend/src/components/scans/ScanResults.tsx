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
    cve_id?: string
    epss_score?: number
    epss_percentile?: number
    epss_updated_at?: string
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

// Helper function to get EPSS risk level and color
function getEPSSRiskLevel(score?: number): { level: string; color: string; bgColor: string } {
    if (!score) return { level: 'Unknown', color: 'text-gray-800', bgColor: 'bg-gray-100' }

    if (score >= 0.8) return { level: 'Critical Risk', color: 'text-red-800', bgColor: 'bg-red-100' }
    if (score >= 0.5) return { level: 'High Risk', color: 'text-orange-800', bgColor: 'bg-orange-100' }
    if (score >= 0.2) return { level: 'Medium Risk', color: 'text-yellow-800', bgColor: 'bg-yellow-100' }
    return { level: 'Low Risk', color: 'text-green-800', bgColor: 'bg-green-100' }
}

// Helper function to format EPSS score as percentage
function formatEPSSScore(score?: number): string {
    if (!score) return 'N/A'
    return `${(score * 100).toFixed(1)}%`
}

// Helper function to format percentile
function formatPercentile(percentile?: number): string {
    if (!percentile) return 'N/A'
    return `${(percentile * 100).toFixed(1)}th percentile`
}

export function ScanResults({ scan }: ScanResultsProps) {
    const [isDownloading, setIsDownloading] = useState(false)
    const [sortBy, setSortBy] = useState<'severity' | 'epss'>('epss')

    // Sort results by EPSS score or severity
    const sortedResults = [...scan.results].sort((a, b) => {
        if (sortBy === 'epss') {
            // Sort by EPSS score (highest first), fallback to severity
            const scoreA = a.epss_score ?? -1
            const scoreB = b.epss_score ?? -1
            return scoreB - scoreA
        }
        // Sort by severity
        const severityOrder = { critical: 4, high: 3, medium: 2, low: 1, info: 0 }
        return (severityOrder[b.severity as keyof typeof severityOrder] ?? 0) -
               (severityOrder[a.severity as keyof typeof severityOrder] ?? 0)
    })

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
                <div className="flex gap-3">
                    <div className="flex items-center gap-2">
                        <label className="text-sm font-medium text-gray-700">Sort by:</label>
                        <select
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value as 'severity' | 'epss')}
                            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-primary-500 focus:border-primary-500"
                        >
                            <option value="epss">Exploit Risk (EPSS)</option>
                            <option value="severity">Severity</option>
                        </select>
                    </div>
                    <button
                        onClick={handleDownloadPDF}
                        disabled={isDownloading}
                        className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 flex items-center gap-2"
                    >
                        {isDownloading ? 'Generating...' : 'Download PDF Report'}
                    </button>
                </div>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <ul className="divide-y divide-gray-200">
                    {sortedResults.map((result) => {
                        const epssRisk = getEPSSRiskLevel(result.epss_score)
                        return (
                            <li key={result.id} className="px-6 py-4">
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2 flex-wrap">
                                            {/* Severity Badge */}
                                            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${result.severity === 'critical' ? 'bg-red-100 text-red-800' :
                                                    result.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                                                        'bg-blue-100 text-blue-800'
                                                }`}>
                                                {result.severity.toUpperCase()}
                                            </span>

                                            {/* EPSS Badge */}
                                            {result.epss_score !== undefined && (
                                                <span
                                                    className={`px-2 py-0.5 text-xs font-medium rounded-full ${epssRisk.bgColor} ${epssRisk.color}`}
                                                    title={`EPSS Score: ${formatEPSSScore(result.epss_score)} | ${formatPercentile(result.epss_percentile)}`}
                                                >
                                                    🎯 {epssRisk.level}: {formatEPSSScore(result.epss_score)}
                                                </span>
                                            )}

                                            {/* CVE Badge */}
                                            {result.cve_id && (
                                                <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                                                    {result.cve_id}
                                                </span>
                                            )}

                                            <span className="text-sm font-medium text-gray-900">
                                                {result.issue_type}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-500 mb-2">{result.description}</p>
                                        <p className="text-sm text-gray-600">
                                            <span className="font-medium">File:</span> {result.file_path}
                                        </p>

                                        {/* EPSS Details */}
                                        {result.epss_score !== undefined && result.epss_percentile !== undefined && (
                                            <div className="mt-2 text-xs text-gray-500">
                                                <span className="font-medium">Exploit Probability:</span> {formatEPSSScore(result.epss_score)}
                                                <span className="mx-2">•</span>
                                                <span className="font-medium">Ranking:</span> {formatPercentile(result.epss_percentile)}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </li>
                        )
                    })}
                </ul>
            </div>
        </div>
    )
}
