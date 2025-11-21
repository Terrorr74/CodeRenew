'use client'

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { GenericErrorFallback } from './ErrorFallback'

// Error logging hook for future Sentry integration
export function logError(error: Error, errorInfo?: ErrorInfo, context?: Record<string, unknown>) {
  // Console log for development
  console.error('Error caught by boundary:', error)
  if (errorInfo) {
    console.error('Component stack:', errorInfo.componentStack)
  }
  if (context) {
    console.error('Context:', context)
  }

  // TODO: Integrate with Sentry
  // if (typeof window !== 'undefined' && window.Sentry) {
  //   Sentry.captureException(error, { extra: { ...errorInfo, ...context } })
  // }
}

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  FallbackComponent?: React.ComponentType<{
    error: Error
    resetErrorBoundary: () => void
  }>
  onError?: (error: Error, errorInfo: ErrorInfo) => void
  onReset?: () => void
  context?: Record<string, unknown>
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    logError(error, errorInfo, this.props.context)
    this.props.onError?.(error, errorInfo)
  }

  resetErrorBoundary = () => {
    this.props.onReset?.()
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      if (this.props.FallbackComponent) {
        return (
          <this.props.FallbackComponent
            error={this.state.error}
            resetErrorBoundary={this.resetErrorBoundary}
          />
        )
      }

      return (
        <GenericErrorFallback
          error={this.state.error}
          resetErrorBoundary={this.resetErrorBoundary}
        />
      )
    }

    return this.props.children
  }
}

// Hook to handle async errors in client components
export function useAsyncErrorHandler() {
  const handleError = React.useCallback((error: Error, context?: Record<string, unknown>) => {
    logError(error, undefined, context)
    // Re-throw to trigger nearest error boundary
    throw error
  }, [])

  return handleError
}
