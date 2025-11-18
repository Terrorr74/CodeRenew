import Link from 'next/link'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-100">
      <div className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-secondary-900 mb-4">
            CodeRenew
          </h1>
          <p className="text-xl text-secondary-600 mb-8">
            WordPress Compatibility Scanner
          </p>
          <p className="text-lg text-secondary-500 max-w-2xl mx-auto mb-8">
            Analyze your WordPress themes and plugins for compatibility issues
            before upgrading. Get AI-powered insights and recommendations.
          </p>

          <div className="flex gap-4 justify-center">
            <Link
              href="/auth/register"
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Get Started
            </Link>
            <Link
              href="/auth/login"
              className="px-6 py-3 bg-white text-primary-600 border border-primary-600 rounded-lg hover:bg-primary-50 transition-colors"
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-primary-600 text-3xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-secondary-900 mb-2">
              Deep Analysis
            </h3>
            <p className="text-secondary-600">
              Scan your WordPress code for deprecated functions, breaking
              changes, and compatibility issues.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-primary-600 text-3xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold text-secondary-900 mb-2">
              AI-Powered
            </h3>
            <p className="text-secondary-600">
              Leverage Claude AI to understand complex code patterns and
              provide intelligent recommendations.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-primary-600 text-3xl mb-4">📊</div>
            <h3 className="text-xl font-semibold text-secondary-900 mb-2">
              Detailed Reports
            </h3>
            <p className="text-secondary-600">
              Get comprehensive reports with severity levels, file locations,
              and actionable fixes.
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
