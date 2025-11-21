/**
 * Scans API
 * API methods for managing WordPress compatibility scans
 */
import { apiClient } from './client'

export interface Scan {
  id: number
  site_id: number
  user_id: number
  wordpress_version_from: string
  wordpress_version_to: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  risk_level?: 'low' | 'medium' | 'high' | 'critical'
  created_at: string
  completed_at?: string
  results?: ScanResult[]
}

export interface ScanResult {
  id: number
  scan_id: number
  issue_type: string
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical'
  file_path?: string
  line_number?: number
  description: string
  recommendation?: string
  code_snippet?: string
}

export interface CreateScanData {
  site_id: number
  wordpress_version_from: string
  wordpress_version_to: string
}

export interface UploadScanData {
  site_id: number
  wordpress_version_from: string
  wordpress_version_to: string
  file: File
}

export const scansApi = {
  /**
   * Upload a file and create a scan
   */
  async uploadScan(data: UploadScanData): Promise<Scan> {
    const formData = new FormData()
    formData.append('file', data.file)
    formData.append('site_id', data.site_id.toString())
    formData.append('wordpress_version_from', data.wordpress_version_from)
    formData.append('wordpress_version_to', data.wordpress_version_to)

    return apiClient.post<Scan>('/scans/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  /**
   * Get all scans for current user
   */
  async getScans(): Promise<Scan[]> {
    return apiClient.get<Scan[]>('/scans')
  },

  /**
   * Get a specific scan with results
   */
  async getScan(id: number): Promise<Scan> {
    return apiClient.get<Scan>(`/scans/${id}`)
  },

  /**
   * Create a new scan
   */
  async createScan(data: CreateScanData): Promise<Scan> {
    return apiClient.post<Scan>('/scans', data)
  },
}
