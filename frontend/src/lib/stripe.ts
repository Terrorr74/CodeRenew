import Stripe from 'stripe';
import { loadStripe, Stripe as StripeJS } from '@stripe/stripe-js';

// Server-side Stripe instance - Lazy initialization to avoid build-time errors
let _stripe: Stripe | null = null;

export const getStripeServer = (): Stripe => {
  if (!_stripe) {
    const apiKey = process.env.STRIPE_SECRET_KEY;

    if (!apiKey) {
      throw new Error(
        'STRIPE_SECRET_KEY is not set. Please add it to your .env.local file.\n' +
        'Get your key from: https://dashboard.stripe.com/apikeys'
      );
    }

    _stripe = new Stripe(apiKey, {
      apiVersion: '2025-11-17.clover',
      typescript: true,
    });
  }

  return _stripe;
};

// Client-side Stripe instance
let stripePromise: Promise<StripeJS | null>;

export const getStripe = () => {
  if (!stripePromise) {
    const publishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;

    if (!publishableKey) {
      console.error(
        'NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY is not set. Please add it to your .env.local file.\n' +
        'Get your key from: https://dashboard.stripe.com/apikeys'
      );
      stripePromise = Promise.resolve(null);
    } else {
      stripePromise = loadStripe(publishableKey);
    }
  }

  return stripePromise;
};

// Stripe price configuration for CodeRenew landing page
export const STRIPE_CONFIG = {
  SITE_ANALYSIS_PRICE: 4900, // $49.00 in cents
  CURRENCY: 'usd',
  PRODUCT_NAME: 'WordPress Site Compatibility Analysis',
  PRODUCT_DESCRIPTION: 'AI-powered WordPress compatibility analysis delivered within 24 hours',
} as const;
