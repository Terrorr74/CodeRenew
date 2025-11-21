'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { HomeIcon, PlusIcon, ClockIcon, UserIcon } from '@heroicons/react/24/outline'

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, current: pathname === '/dashboard' },
    { name: 'New Scan', href: '/intake', icon: PlusIcon, current: pathname === '/intake' },
    { name: 'History', href: '/dashboard/history', icon: ClockIcon, current: pathname === '/dashboard/history' },
    { name: 'Profile', href: '/profile', icon: UserIcon, current: pathname === '/profile' },
  ]

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/dashboard" className="text-2xl font-bold text-primary-600">
              CodeRenew
            </Link>

            <nav className="hidden md:flex space-x-6">
              {navigation.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${pathname === item.href
                    ? 'bg-primary-50 text-primary-700 font-medium'
                    : 'text-secondary-600 hover:bg-secondary-100'
                    }`}
                >
                  <span>{item.icon}</span>
                  <span>{item.name}</span>
                </Link>
              ))}
            </nav>

            <div className="flex items-center space-x-4">
              {user && (
                <span className="text-sm text-secondary-600">{user.email}</span>
              )}
              <button
                onClick={logout}
                className="text-secondary-600 hover:text-secondary-900 font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  )
}
