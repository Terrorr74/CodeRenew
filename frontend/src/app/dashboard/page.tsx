'use client'

import Link from 'next/link'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-secondary-900 mb-2">
          Dashboard
        </h1>
        <p className="text-secondary-600">
          Welcome to CodeRenew. Start by adding a site or running a scan.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <Link
          href="/dashboard/sites"
          className="p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border border-secondary-200"
        >
          <div className="text-primary-600 text-3xl mb-4">🌐</div>
          <h3 className="text-xl font-semibold text-secondary-900 mb-2">
            Manage Sites
          </h3>
          <p className="text-secondary-600">
            Add and manage your WordPress sites
          </p>
        </Link>

        <Link
          href="/scans/new"
          className="p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border border-secondary-200"
        >
          <div className="text-primary-600 text-3xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-secondary-900 mb-2">
            New Scan
          </h3>
          <p className="text-secondary-600">
            Run a compatibility scan on your code
          </p>
        </Link>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-secondary-900 mb-4">
          Recent Scans
        </h2>
        <p className="text-secondary-500">No scans yet. Create your first scan to get started.</p>
      </div>
    </DashboardLayout>
  )
}
