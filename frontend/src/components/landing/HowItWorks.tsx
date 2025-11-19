export default function HowItWorks() {
  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            How It Works
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Get your compatibility analysis in 3 simple steps
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 relative">
          {/* Connection Lines - Desktop Only */}
          <div className="hidden md:block absolute top-24 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-200 via-blue-400 to-blue-200" style={{ top: '6rem' }}></div>

          {/* Step 1 */}
          <div className="relative">
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mb-6 relative z-10 shadow-lg">
                1
              </div>
              <div className="bg-white rounded-lg shadow-md p-6 w-full">
                <div className="text-blue-600 text-5xl mb-4">📝</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  Tell Us Your Site Details
                </h3>
                <p className="text-gray-600">
                  Share your WordPress version, plugins, theme, and target update version. Takes less than 5 minutes.
                </p>
              </div>
            </div>
          </div>

          {/* Step 2 */}
          <div className="relative">
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mb-6 relative z-10 shadow-lg">
                2
              </div>
              <div className="bg-white rounded-lg shadow-md p-6 w-full">
                <div className="text-blue-600 text-5xl mb-4">🤖</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  We Analyze with AI
                </h3>
                <p className="text-gray-600">
                  Our AI scans WordPress core changes, plugin compatibility, and custom code. Delivered within 24 hours.
                </p>
              </div>
            </div>
          </div>

          {/* Step 3 */}
          <div className="relative">
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mb-6 relative z-10 shadow-lg">
                3
              </div>
              <div className="bg-white rounded-lg shadow-md p-6 w-full">
                <div className="text-blue-600 text-5xl mb-4">📊</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  Get Your Detailed Report
                </h3>
                <p className="text-gray-600">
                  Receive confidence scores, identified issues, and actionable recommendations. Update with confidence.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="mt-16 bg-blue-50 border border-blue-200 rounded-lg p-8">
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
              <span className="text-gray-900 font-semibold">Timeline:</span>
            </div>
            <span className="text-gray-600">Submit details (5 min)</span>
            <span className="text-gray-400">→</span>
            <span className="text-gray-600">AI analysis (within 24 hours)</span>
            <span className="text-gray-400">→</span>
            <span className="text-gray-600">Receive detailed report</span>
          </div>
        </div>
      </div>
    </section>
  );
}
