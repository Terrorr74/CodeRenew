import Stripe from 'stripe';
import { loadStripe, Stripe as StripeJS } from '@stripe/stripe-js';

// Server-side Stripe instance
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-11-17.clover',
});

// Client-side Stripe instance
let stripePromise: Promise<StripeJS | null>;
export const getStripe = () => {
  if (!stripePromise) {
    stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);
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
