/**
 * Health Check API Route
 * Provides health status for monitoring and Docker health checks
 */
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Basic health check - verify the Next.js app is responding
    const healthStatus = {
      status: 'healthy',
      service: 'coderenew-frontend',
      timestamp: Date.now(),
      checks: {
        nextjs: {
          status: 'healthy',
          version: process.env.npm_package_version || 'unknown'
        },
        backend: {
          status: 'unknown',
          note: 'Backend connectivity check not implemented in health endpoint'
        }
      }
    };

    return NextResponse.json(healthStatus, { status: 200 });
  } catch (error) {
    const errorStatus = {
      status: 'unhealthy',
      service: 'coderenew-frontend',
      timestamp: Date.now(),
      error: error instanceof Error ? error.message : 'Unknown error'
    };

    return NextResponse.json(errorStatus, { status: 503 });
  }
}

// Support HEAD requests for simpler health checks
export async function HEAD() {
  return new NextResponse(null, { status: 200 });
}
