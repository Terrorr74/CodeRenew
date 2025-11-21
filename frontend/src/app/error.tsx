'use client'

import { useEffect } from 'react'
import { PageErrorFallback } from '@/components/errors'
import { logError } from '@/components/errors'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    logError(error, undefined, { digest: error.digest, page: 'app-error' })
  }, [error])

  return <PageErrorFallback error={error} resetErrorBoundary={reset} />
}
