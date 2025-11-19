'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

function IntakeFormContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get('session_id');

  const [isValidating, setIsValidating] = useState(true);
  const [isValid, setIsValid] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [customerEmail, setCustomerEmail] = useState('');

  const [formData, setFormData] = useState({
    agencyName: '',
    contactEmail: '',
    siteName: '',
    siteUrl: '',
    wpCurrentVersion: '',
    wpTargetVersion: '',
    pluginList: '',
    themeName: '',
    themeVersion: '',
    customNotes: '',
  });

  useEffect(() => {
    if (!sessionId) {
      router.push('/?error=no_session');
      return;
    }

    // Validate the session
    const validateSession = async () => {
      try {
        const response = await fetch(`/api/stripe/validate-session?session_id=${sessionId}`);
        const data = await response.json();

        if (data.valid) {
          setIsValid(true);
          setCustomerEmail(data.customerEmail || '');
          setFormData(prev => ({
            ...prev,
            contactEmail: data.customerEmail || '',
          }));
        } else {
          router.push('/?error=invalid_session');
        }
      } catch (error) {
        console.error('Error validating session:', error);
        router.push('/?error=validation_failed');
      } finally {
        setIsValidating(false);
      }
    };

    validateSession();
  }, [sessionId, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stripe_session_id: sessionId,
          agency_name: formData.agencyName,
          contact_email: formData.contactEmail,
          site_name: formData.siteName,
          site_url: formData.siteUrl,
          wp_current_version: formData.wpCurrentVersion,
          wp_target_version: formData.wpTargetVersion,
          plugin_list: formData.pluginList,
          theme_name: formData.themeName,
          theme_version: formData.themeVersion,
          custom_notes: formData.customNotes,
        }),
      });

      if (response.ok) {
        router.push('/success');
      } else {
        const error = await response.json();
        alert(`Error submitting order: ${error.detail || 'Please try again'}`);
      }
    } catch (error) {
      console.error('Error submitting order:', error);
      alert('Error submitting order. Please contact support at hello@coderenew.com');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  if (isValidating) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Validating your payment...</p>
        </div>
      </div>
    );
  }

  if (!isValid) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Success Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="flex-shrink-0">
              <svg className="w-12 h-12 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Payment Successful!</h1>
              <p className="text-gray-600">Now let&apos;s get your site analysis started.</p>
            </div>
          </div>
        </div>

        {/* Intake Form */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Site Details</h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Agency Info */}
            <div>
              <label htmlFor="agencyName" className="block text-sm font-medium text-gray-700 mb-1">
                Agency Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="agencyName"
                name="agencyName"
                required
                value={formData.agencyName}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Your Agency LLC"
              />
            </div>

            <div>
              <label htmlFor="contactEmail" className="block text-sm font-medium text-gray-700 mb-1">
                Contact Email <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                id="contactEmail"
                name="contactEmail"
                required
                value={formData.contactEmail}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="you@agency.com"
              />
              <p className="text-sm text-gray-500 mt-1">We&apos;ll send your analysis report to this email</p>
            </div>

            {/* Site Info */}
            <div className="border-t pt-6 mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">WordPress Site Information</h3>

              <div className="space-y-4">
                <div>
                  <label htmlFor="siteName" className="block text-sm font-medium text-gray-700 mb-1">
                    Site Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="siteName"
                    name="siteName"
                    required
                    value={formData.siteName}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Client Site Name"
                  />
                </div>

                <div>
                  <label htmlFor="siteUrl" className="block text-sm font-medium text-gray-700 mb-1">
                    Site URL (Optional)
                  </label>
                  <input
                    type="url"
                    id="siteUrl"
                    name="siteUrl"
                    value={formData.siteUrl}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="https://clientsite.com"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="wpCurrentVersion" className="block text-sm font-medium text-gray-700 mb-1">
                      Current WordPress Version <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      id="wpCurrentVersion"
                      name="wpCurrentVersion"
                      required
                      value={formData.wpCurrentVersion}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="6.4.2"
                    />
                  </div>

                  <div>
                    <label htmlFor="wpTargetVersion" className="block text-sm font-medium text-gray-700 mb-1">
                      Target WordPress Version <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      id="wpTargetVersion"
                      name="wpTargetVersion"
                      required
                      value={formData.wpTargetVersion}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="6.5.0"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="pluginList" className="block text-sm font-medium text-gray-700 mb-1">
                    Plugin List <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    id="pluginList"
                    name="pluginList"
                    required
                    value={formData.pluginList}
                    onChange={handleChange}
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                    placeholder="Enter one plugin per line with version:&#10;WooCommerce - 8.5.1&#10;Elementor Pro - 3.18.0&#10;Yoast SEO - 21.8"
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    List each plugin with its version number (one per line)
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="themeName" className="block text-sm font-medium text-gray-700 mb-1">
                      Theme Name
                    </label>
                    <input
                      type="text"
                      id="themeName"
                      name="themeName"
                      value={formData.themeName}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Astra"
                    />
                  </div>

                  <div>
                    <label htmlFor="themeVersion" className="block text-sm font-medium text-gray-700 mb-1">
                      Theme Version
                    </label>
                    <input
                      type="text"
                      id="themeVersion"
                      name="themeVersion"
                      value={formData.themeVersion}
                      onChange={handleChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="4.5.2"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="customNotes" className="block text-sm font-medium text-gray-700 mb-1">
                    Custom Code or Special Notes (Optional)
                  </label>
                  <textarea
                    id="customNotes"
                    name="customNotes"
                    value={formData.customNotes}
                    onChange={handleChange}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Mention any custom plugins, theme modifications, or specific concerns..."
                  />
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="border-t pt-6 mt-6">
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-4 px-6 text-lg font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Submitting...
                  </span>
                ) : (
                  'Submit for Analysis'
                )}
              </button>
              <p className="text-center text-sm text-gray-500 mt-4">
                Your analysis will be delivered within 24 hours to {formData.contactEmail || 'your email'}
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function IntakePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <IntakeFormContent />
    </Suspense>
  );
}
