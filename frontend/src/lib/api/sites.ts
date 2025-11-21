/**
 * Sites API
 * API methods for managing WordPress sites
 */
import { apiClient } from './client'

export interface Site {
  id: number
  user_id: number
  name: string
  url?: string
  description?: string
  created_at: string
  updated_at?: string
}

export interface CreateSiteData {
  name: string
  url?: string
  description?: string
}

export interface UpdateSiteData {
  name?: string
  url?: string
  description?: string
}

export const sitesApi = {
  /**
   * Get all sites for current user
   */
  async getSites(): Promise<Site[]> {
    return apiClient.get<Site[]>('/sites')
  },

  /**
   * Get a specific site
   */
  async getSite(id: number): Promise<Site> {
    return apiClient.get<Site>(`/sites/${id}`)
  },

  /**
   * Create a new site
   */
  async createSite(data: CreateSiteData): Promise<Site> {
    return apiClient.post<Site>('/sites', data)
  },

  /**
   * Update a site
   */
  async updateSite(id: number, data: UpdateSiteData): Promise<Site> {
    return apiClient.put<Site>(`/sites/${id}`, data)
  },

  /**
   * Delete a site
   */
  async deleteSite(id: number): Promise<void> {
    return apiClient.delete<void>(`/sites/${id}`)
  },
}
