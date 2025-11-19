import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';

export async function GET(req: NextRequest) {
  const searchParams = req.nextUrl.searchParams;
  const sessionId = searchParams.get('session_id');

  if (!sessionId) {
    return NextResponse.json({ valid: false, error: 'No session ID provided' }, { status: 400 });
  }

  try {
    const session = await stripe.checkout.sessions.retrieve(sessionId);

    if (session.payment_status === 'paid') {
      return NextResponse.json({
        valid: true,
        customerEmail: session.customer_details?.email,
        amountPaid: session.amount_total,
        paymentIntentId: session.payment_intent,
      });
    } else {
      return NextResponse.json({
        valid: false,
        error: 'Payment not completed',
        paymentStatus: session.payment_status,
      });
    }
  } catch (error: any) {
    console.error('Error validating session:', error);
    return NextResponse.json(
      { valid: false, error: 'Invalid session', message: error.message },
      { status: 400 }
    );
  }
}
