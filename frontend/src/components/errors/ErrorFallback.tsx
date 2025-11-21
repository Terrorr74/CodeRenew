'use client'

import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

interface ErrorFallbackProps {
  error: Error
  resetErrorBoundary: () => void
}

// Generic error fallback with retry button
export function GenericErrorFallback({ error, resetErrorBoundary }: ErrorFallbackProps) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center p-8">
      <div className="rounded-lg bg-red-50 p-8 text-center max-w-md">
        <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-500" />
        <h2 className="mt-4 text-lg font-semibold text-gray-900">Something went wrong</h2>
        <p className="mt-2 text-sm text-gray-600">
          {error.message || 'An unexpected error occurred'}
        </p>
        <button
          onClick={resetErrorBoundary}
          className="mt-4 inline-flex items-center gap-2 rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        >
          <ArrowPathIcon className="h-4 w-4" />
          Try again
        </button>
      </div>
    </div>
  )
}

// Page-level error fallback (full page)
export function PageErrorFallback({ error, resetErrorBoundary }: ErrorFallbackProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-8">
      <div className="rounded-xl bg-white p-12 text-center shadow-lg max-w-lg">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
          <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
        </div>
        <h1 className="mt-6 text-2xl font-bold text-gray-900">Page Error</h1>
        <p className="mt-3 text-gray-600">
          We encountered an error loading this page. Please try again.
        </p>
        {process.env.NODE_ENV === 'development' && (
          <pre className="mt-4 rounded bg-gray-100 p-3 text-left text-xs text-red-700 overflow-auto max-h-32">
            {error.message}
          </pre>
        )}
        <div className="mt-6 flex justify-center gap-3">
          <button
            onClick={resetErrorBoundary}
            className="inline-flex items-center gap-2 rounded-md bg-primary-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-primary-700"
          >
            <ArrowPathIcon className="h-4 w-4" />
            Retry
          </button>
          <a
            href="/dashboard"
            className="inline-flex items-center rounded-md border border-gray-300 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Go to Dashboard
          </a>
        </div>
      </div>
    </div>
  )
}

// Component-level error fallback (inline, smaller)
export function InlineErrorFallback({ error, resetErrorBoundary }: ErrorFallbackProps) {
  return (
    <div className="rounded-md border border-red-200 bg-red-50 p-4">
      <div className="flex items-start gap-3">
        <ExclamationTriangleIcon className="h-5 w-5 flex-shrink-0 text-red-500" />
        <div className="flex-1">
          <p className="text-sm font-medium text-red-800">Error loading component</p>
          <p className="mt-1 text-xs text-red-600">{error.message}</p>
          <button
            onClick={resetErrorBoundary}
            className="mt-2 text-xs font-medium text-red-700 hover:text-red-900 underline"
          >
            Try again
          </button>
        </div>
      </div>
    </div>
  )
}
