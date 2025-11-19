'use client';

import { useState } from 'react';

interface FAQItem {
  question: string;
  answer: string;
}

const faqs: FAQItem[] = [
  {
    question: 'How accurate is the compatibility analysis?',
    answer: 'Our AI-powered analysis achieves 95%+ accuracy by examining WordPress core changes, deprecated functions, plugin APIs, and known compatibility issues. We cross-reference against official WordPress documentation and test extensively against real-world upgrade scenarios.',
  },
  {
    question: 'What if I have custom code or custom plugins?',
    answer: 'We analyze custom code too! Simply provide details about your custom plugins or theme modifications in the intake form. Our AI can identify deprecated functions, breaking API changes, and potential compatibility issues in custom code just as effectively as with public plugins.',
  },
  {
    question: 'How long does the analysis take?',
    answer: 'We deliver your comprehensive compatibility report within 24 hours (one business day) of receiving your site details. Most reports are actually completed within 12 hours, but we guarantee 24-hour delivery.',
  },
  {
    question: 'What happens after I pay?',
    answer: 'After payment, you\'ll immediately fill out an intake form with your site details (WordPress version, plugins, theme, etc.). Our team receives your request and begins the AI-powered analysis. You\'ll receive a detailed PDF report via email with confidence scores and recommendations.',
  },
  {
    question: 'What if the analysis finds compatibility issues?',
    answer: 'The report identifies every potential issue with severity levels (critical, moderate, low) and provides specific recommendations. For critical issues, we include alternative solutions like compatible plugin versions or workarounds. You\'ll know exactly what needs attention before updating.',
  },
  {
    question: 'Do you offer refunds?',
    answer: 'Yes! We offer a 100% satisfaction guarantee. If you\'re not happy with the analysis quality or detail, contact us within 7 days for a full refund, no questions asked. We stand behind the quality of our service.',
  },
  {
    question: 'Can I analyze multiple sites?',
    answer: 'Absolutely! Each site requires a separate analysis since every site has unique plugins, themes, and configurations. For agencies managing 10+ sites, contact us at hello@coderenew.com for volume pricing discounts.',
  },
  {
    question: 'Do I need to provide admin access to my site?',
    answer: 'No! We never need access to your live site. You simply provide a list of your plugins (with versions), theme name/version, and WordPress versions. This can be exported easily from your WordPress admin or provided manually.',
  },
];

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-xl text-gray-600">
            Everything you need to know about CodeRenew
          </p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-md overflow-hidden transition-all duration-200"
            >
              <button
                onClick={() => toggleFAQ(index)}
                className="w-full px-6 py-5 text-left flex justify-between items-center hover:bg-gray-50 transition-colors"
              >
                <span className="font-semibold text-gray-900 pr-8">
                  {faq.question}
                </span>
                <svg
                  className={`w-5 h-5 text-blue-600 flex-shrink-0 transition-transform duration-200 ${
                    openIndex === index ? 'transform rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
              {openIndex === index && (
                <div className="px-6 pb-5 text-gray-600 leading-relaxed">
                  {faq.answer}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <p className="text-gray-600 mb-4">
            Still have questions?
          </p>
          <a
            href="mailto:hello@coderenew.com"
            className="inline-flex items-center text-blue-600 hover:text-blue-700 font-semibold"
          >
            Contact us at hello@coderenew.com
            <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </a>
        </div>
      </div>
    </section>
  );
}
