# CodeRenew Landing Page Setup Guide

This document provides complete instructions for setting up and deploying the CodeRenew landing page with Stripe payment integration.

## Overview

The landing page is a conversion-optimized funnel for selling WordPress compatibility analysis services at $49 per site.

**Payment Flow:**
1. User lands on homepage → sees value proposition
2. Clicks "Get Your First Site Analyzed - $49" CTA
3. Redirects to Stripe Checkout (hosted payment page)
4. After payment → redirects to intake form
5. User fills out site details → submits to backend API
6. Redirects to success confirmation page
7. Analysis begins (manual concierge service for MVP)

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python 3.11+), PostgreSQL, SQLAlchemy
- **Payments**: Stripe Checkout (one-time $49 payments)
- **Database**: PostgreSQL 15+

## Prerequisites

1. **Node.js 18+** - For frontend development
2. **Python 3.11+** - For backend API
3. **PostgreSQL 15+** - For database
4. **Stripe Account** - For payment processing (free test account works)

## Environment Variables Setup

### Frontend (.env.local)

Create `/frontend/.env.local`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Stripe Configuration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...  # From Stripe Dashboard
STRIPE_SECRET_KEY=sk_test_...                   # From Stripe Dashboard
STRIPE_WEBHOOK_SECRET=whsec_...                 # From Stripe Webhooks
```

**Getting Stripe Keys:**
1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy **Publishable key** → `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
3. Reveal and copy **Secret key** → `STRIPE_SECRET_KEY`
4. For webhooks (optional in dev): https://dashboard.stripe.com/test/webhooks

### Backend (.env)

Create `/backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://coderenew:your_password@localhost:5432/coderenew

# Stripe
STRIPE_SECRET_KEY=sk_test_...  # Same as frontend

# JWT (for future authenticated features)
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Anthropic (for future AI analysis)
ANTHROPIC_API_KEY=your-key-here

# App Settings
DEBUG=True
LOG_LEVEL=INFO
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=52428800
```

## Database Setup

### 1. Create PostgreSQL Database

```bash
# Using psql
psql -U postgres

CREATE DATABASE coderenew;
CREATE USER coderenew WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE coderenew TO coderenew;
\q
```

### 2. Run Migrations

```bash
cd backend

# If using virtual environment (recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migration to create orders table
# Note: You may need to install alembic globally or use docker
# For now, tables will be created automatically on first API call
# Or manually run the SQL from the migration file
```

**Manual Migration (if alembic doesn't work):**

Run this SQL in your PostgreSQL database:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stripe_payment_id VARCHAR(255) UNIQUE,
    stripe_session_id VARCHAR(255) UNIQUE NOT NULL,
    payment_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    amount_paid INTEGER NOT NULL,
    agency_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    site_name VARCHAR(255) NOT NULL,
    site_url VARCHAR(500),
    wp_current_version VARCHAR(50) NOT NULL,
    wp_target_version VARCHAR(50) NOT NULL,
    plugin_list TEXT NOT NULL,
    theme_name VARCHAR(255),
    theme_version VARCHAR(50),
    custom_notes TEXT,
    analysis_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    report_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_orders_email ON orders(contact_email);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);
CREATE INDEX idx_orders_analysis_status ON orders(analysis_status);
```

## Local Development

### 1. Start Backend

```bash
cd backend
source venv/bin/activate  # If using venv
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run on: http://localhost:8000
API Docs: http://localhost:8000/docs

### 2. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on: http://localhost:3000

### 3. Test Payment Flow

1. Open http://localhost:3000
2. Click "Get Your First Site Analyzed - $49"
3. Use Stripe test card: `4242 4242 4242 4242`
   - Any future expiry date (e.g., 12/34)
   - Any 3-digit CVC (e.g., 123)
   - Any ZIP code (e.g., 12345)
4. Complete payment → should redirect to intake form
5. Fill out site details → submit
6. Should redirect to success page

## Stripe Webhook Setup (Production)

For production, you need to configure webhooks:

1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter your webhook URL: `https://yourdomain.com/api/stripe/webhook`
4. Select events to listen for:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Copy the **Signing secret** → `STRIPE_WEBHOOK_SECRET`

## API Endpoints

### Frontend API Routes (Next.js)

- `POST /api/stripe/checkout` - Create Stripe checkout session
- `GET /api/stripe/validate-session?session_id=xxx` - Validate payment
- `POST /api/stripe/webhook` - Handle Stripe webhooks

### Backend API Endpoints (FastAPI)

- `POST /api/v1/orders` - Create order from intake form
- `GET /api/v1/orders/{id}` - Get specific order
- `GET /api/v1/orders` - List orders (with pagination/filtering)
- `POST /api/v1/orders/webhooks/stripe` - Alternative webhook handler

## Order Processing Workflow

For MVP (manual concierge service):

1. **Order Received**: Check email or database for new orders
2. **Analysis Status**: Update order analysis_status to "in_progress"
3. **Perform Analysis**: Manually or with AI tools
4. **Generate Report**: Create PDF or document
5. **Upload Report**: Store in cloud (S3, etc.) and update `report_url`
6. **Send Email**: Email report to customer's `contact_email`
7. **Mark Complete**: Update `analysis_status` to "completed" and set `completed_at`

### Query Pending Orders

```bash
# Using API
curl http://localhost:8000/api/v1/orders?analysis_status=pending

# Using SQL
SELECT * FROM orders WHERE analysis_status = 'pending' ORDER BY created_at DESC;
```

## Production Deployment

### Frontend (Vercel - Recommended)

1. Push code to GitHub
2. Import project to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy!

### Backend (Railway, Render, or AWS)

1. Set up PostgreSQL database
2. Set environment variables
3. Run migrations
4. Deploy FastAPI app
5. Update `NEXT_PUBLIC_API_URL` in frontend to production backend URL

### Database (Production)

- **Managed PostgreSQL**: Railway, Supabase, AWS RDS
- Update `DATABASE_URL` in backend .env
- Run migrations on production database

## Monitoring & Analytics

### Track These Metrics

1. **Conversion Rate**: Landing page visits → purchases
2. **Payment Success Rate**: Checkout started → payment completed
3. **Order Fulfillment Time**: Order created → analysis delivered
4. **Customer Satisfaction**: Follow-up survey or refund rate

### Tools to Integrate

- **Analytics**: Google Analytics, Plausible
- **Error Tracking**: Sentry
- **Email**: SendGrid, Mailgun (for automated order confirmations)

## Troubleshooting

### "Invalid session" error on intake form
- Check that Stripe session was actually paid
- Verify `STRIPE_SECRET_KEY` matches the session
- Session expires after 24 hours

### Orders not appearing in database
- Check backend logs for errors
- Verify database connection
- Ensure CORS is configured correctly

### Webhook not receiving events
- Check webhook URL is publicly accessible
- Verify webhook signing secret
- Check Stripe dashboard for delivery attempts

### Payment succeeded but order not created
- This is expected! Order is created when intake form is submitted
- The webhook just logs the payment event

## Security Checklist

- [ ] Never commit `.env` files to git
- [ ] Use environment variables for all secrets
- [ ] Verify webhook signatures in production
- [ ] Use HTTPS in production
- [ ] Validate all user inputs
- [ ] Rate limit API endpoints
- [ ] Set up CORS properly
- [ ] Use Stripe test mode for development

## Next Steps

1. **Email Automation**: Send confirmation emails when orders are created
2. **Admin Dashboard**: Build UI for viewing/managing orders
3. **Automated Analysis**: Integrate actual WordPress scanning
4. **Payment Plans**: Add monthly subscription option
5. **Analytics**: Track conversion funnel
6. **A/B Testing**: Test different landing page variations

## Support

For questions or issues:
- Email: support@coderenew.com
- GitHub Issues: [repository-url]/issues

## License

[Your License]
