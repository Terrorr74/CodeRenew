export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Column */}
          <div className="md:col-span-2">
            <h3 className="text-2xl font-bold text-white mb-3">CodeRenew</h3>
            <p className="text-gray-400 mb-4 max-w-md">
              WordPress compatibility analysis powered by AI.
              Know if your updates will break your sites before you click update.
            </p>
            <p className="text-gray-500 text-sm">
              Trusted by 50+ WordPress agencies worldwide.
            </p>
          </div>

          {/* Product Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#pricing" className="hover:text-white transition-colors">
                  Pricing
                </a>
              </li>
              <li>
                <a href="#how-it-works" className="hover:text-white transition-colors">
                  How It Works
                </a>
              </li>
              <li>
                <a href="#faq" className="hover:text-white transition-colors">
                  FAQ
                </a>
              </li>
              <li>
                <a href="mailto:hello@coderenew.com" className="hover:text-white transition-colors">
                  Contact Sales
                </a>
              </li>
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="/privacy" className="hover:text-white transition-colors">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="/terms" className="hover:text-white transition-colors">
                  Terms of Service
                </a>
              </li>
              <li>
                <a href="/refund" className="hover:text-white transition-colors">
                  Refund Policy
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-gray-500">
            &copy; {currentYear} CodeRenew. All rights reserved.
          </p>
          <div className="flex items-center gap-6">
            <a
              href="mailto:hello@coderenew.com"
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              hello@coderenew.com
            </a>
            <a
              href="mailto:support@coderenew.com"
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              support@coderenew.com
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
