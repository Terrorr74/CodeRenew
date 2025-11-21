'use client'

import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'

export default function LandingNav() {
    const { isAuthenticated, user } = useAuth()

    return (
        <nav className="bg-white shadow-sm sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center">
                        <span className="text-2xl font-bold text-blue-600">CodeRenew</span>
                    </Link>

                    {/* Navigation Links */}
                    <div className="hidden md:flex items-center space-x-8">
                        <a href="#how-it-works" className="text-gray-600 hover:text-gray-900 transition-colors">
                            How It Works
                        </a>
                        <a href="#pricing" className="text-gray-600 hover:text-gray-900 transition-colors">
                            Pricing
                        </a>
                        <a href="#faq" className="text-gray-600 hover:text-gray-900 transition-colors">
                            FAQ
                        </a>
                    </div>

                    {/* Auth Buttons */}
                    <div className="flex items-center space-x-4">
                        {isAuthenticated ? (
                            <>
                                <span className="text-sm text-gray-600 hidden sm:inline">
                                    {user?.email}
                                </span>
                                <Link
                                    href="/dashboard"
                                    className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    Dashboard
                                </Link>
                            </>
                        ) : (
                            <>
                                <Link
                                    href="/auth/login"
                                    className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
                                >
                                    Sign In
                                </Link>
                                <Link
                                    href="/auth/register"
                                    className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    Get Started
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    )
}
