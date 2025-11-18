/**
 * Type Definitions
 * Shared TypeScript types and interfaces
 */

export interface ApiError {
  detail: string
  status_code?: number
}

export interface PaginationParams {
  skip?: number
  limit?: number
}

export type SeverityLevel = 'info' | 'low' | 'medium' | 'high' | 'critical'
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'
export type ScanStatus = 'pending' | 'processing' | 'completed' | 'failed'
