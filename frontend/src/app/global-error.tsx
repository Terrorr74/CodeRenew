'use client'

import { useEffect } from 'react'
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

// Root error handler - cannot use components since they may have caused the error
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Global error:', error)
    // TODO: Send to Sentry
  }, [error])

  return (
    <html>
      <body>
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#f9fafb',
            padding: '2rem',
          }}
        >
          <div
            style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '3rem',
              textAlign: 'center',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              maxWidth: '32rem',
            }}
          >
            <ExclamationTriangleIcon
              style={{
                width: '48px',
                height: '48px',
                color: '#dc2626',
                margin: '0 auto',
              }}
            />
            <h1
              style={{
                marginTop: '1.5rem',
                fontSize: '1.5rem',
                fontWeight: 700,
                color: '#111827',
              }}
            >
              Application Error
            </h1>
            <p
              style={{
                marginTop: '0.75rem',
                color: '#6b7280',
              }}
            >
              A critical error occurred. Please refresh the page or try again later.
            </p>
            <button
              onClick={reset}
              style={{
                marginTop: '1.5rem',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                backgroundColor: '#2563eb',
                color: 'white',
                padding: '0.625rem 1.25rem',
                borderRadius: '6px',
                border: 'none',
                fontSize: '0.875rem',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              <ArrowPathIcon style={{ width: '16px', height: '16px' }} />
              Try again
            </button>
          </div>
        </div>
      </body>
    </html>
  )
}
