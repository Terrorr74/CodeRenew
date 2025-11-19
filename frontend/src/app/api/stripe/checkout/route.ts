import { NextRequest, NextResponse } from 'next/server';
import { stripe, STRIPE_CONFIG } from '@/lib/stripe';

export async function POST(req: NextRequest) {
  try {
    const origin = req.headers.get('origin') || process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';

    // Create Stripe Checkout Session
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: STRIPE_CONFIG.CURRENCY,
            product_data: {
              name: STRIPE_CONFIG.PRODUCT_NAME,
              description: STRIPE_CONFIG.PRODUCT_DESCRIPTION,
            },
            unit_amount: STRIPE_CONFIG.SITE_ANALYSIS_PRICE,
          },
          quantity: 1,
        },
      ],
      mode: 'payment',
      success_url: `${origin}/intake?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/?canceled=true`,
      metadata: {
        product_type: 'site_analysis',
      },
    });

    return NextResponse.json({ url: session.url, sessionId: session.id });
  } catch (error: any) {
    console.error('Error creating checkout session:', error);
    return NextResponse.json(
      { error: 'Error creating checkout session', message: error.message },
      { status: 500 }
    );
  }
}
