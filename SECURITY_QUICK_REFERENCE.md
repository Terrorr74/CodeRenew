# Security Implementation - Quick Reference Guide

## 🚀 Getting Started

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Database Migration
```bash
cd backend
alembic upgrade head
```

### 3. Update Environment Variables
Add to your `.env` file:
```bash
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

---

## 🔐 Security Features Overview

### Rate Limiting
| Endpoint | Limit | Purpose |
|----------|-------|---------|
| `/api/v1/auth/login` | 5 per 15 min | Prevent brute force |
| `/api/v1/auth/register` | 3 per hour | Prevent spam accounts |
| `/api/v1/auth/forgot-password` | 3 per hour | Prevent email bombing |
| `/api/v1/auth/reset-password` | 3 per hour | Prevent token guessing |

### Password Requirements
- ✅ Minimum 8 characters
- ✅ At least 1 uppercase letter
- ✅ At least 1 lowercase letter
- ✅ At least 1 number
- ✅ At least 1 special character
- ✅ Not in common password list
- ✅ No sequential characters

### Account Lockout
- **Trigger:** 5 failed login attempts
- **Duration:** 30 minutes
- **Notification:** Email sent to user
- **Recovery:** Automatic after 30 minutes OR password reset

---

## 🛠️ Common Tasks

### Testing Password Validation
```python
from app.core.password_policy import validate_password_strength

# This will pass
validate_password_strength("MyP@ssw0rd123")

# This will raise PasswordValidationError
validate_password_strength("password")  # Too common
validate_password_strength("Short1!")   # Too short
```

### Testing Rate Limiting
```bash
# Should succeed (first attempt)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}'

# After 5 attempts, should return 429 Too Many Requests
```

### Manually Unlock Account (Development)
```python
from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.email == "user@example.com").first()
user.failed_login_attempts = 0
user.locked_until = None
db.commit()
```

### Testing Stripe Webhooks
```bash
# 1. Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# 2. Forward webhooks to local server
stripe listen --forward-to localhost:8000/api/v1/orders/webhooks/stripe

# 3. Get the webhook secret from CLI output and add to .env
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx

# 4. Trigger test event
stripe trigger checkout.session.completed
```

---

## 📁 Key Files

### Security Modules
```
backend/app/
├── core/
│   ├── password_policy.py       # Password validation
│   ├── rate_limiting.py         # Rate limiter config
│   └── input_sanitization.py   # XSS prevention
├── middleware/
│   └── security_headers.py      # Security headers
└── services/
    └── email.py                 # Security notifications
```

### Configuration
```
backend/
├── app/
│   └── core/
│       └── config.py            # Environment settings
├── alembic/versions/
│   └── 004_add_account_lockout_fields.py  # Database migration
└── .env.example                 # Environment template
```

---

## 🔍 Debugging

### Check if Account is Locked
```python
from app.models.user import User
from datetime import datetime

user = db.query(User).filter(User.email == "user@example.com").first()
if user.locked_until and user.locked_until > datetime.utcnow():
    print(f"Account locked until: {user.locked_until}")
    print(f"Failed attempts: {user.failed_login_attempts}")
```

### View Rate Limit Status
Rate limit information is returned in response headers:
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1234567890
```

### Check Security Headers
```bash
curl -I http://localhost:8000/api/v1/auth/login
```

Look for:
- `Strict-Transport-Security`
- `Content-Security-Policy`
- `X-Frame-Options`
- `X-Content-Type-Options`

---

## ⚠️ Common Issues

### Issue: Rate Limiting Not Working
**Cause:** Limiter not registered in main.py
**Fix:** Ensure these lines are in `app/main.py`:
```python
from app.core.rate_limiting import limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### Issue: Password Validation Failing Unexpectedly
**Cause:** Password contains sequential characters or common words
**Fix:** Check password against requirements:
```python
from app.core.password_policy import get_password_strength_score
score = get_password_strength_score("your_password")
print(f"Password strength: {score}/100")
```

### Issue: Stripe Webhooks Failing
**Cause:** Missing or incorrect `STRIPE_WEBHOOK_SECRET`
**Fix:**
1. Get secret from Stripe Dashboard → Developers → Webhooks
2. Add to `.env`: `STRIPE_WEBHOOK_SECRET=whsec_...`
3. Restart server

### Issue: Account Lockout Not Triggering
**Cause:** Migration not run
**Fix:**
```bash
cd backend
alembic upgrade head
```

### Issue: Email Notifications Not Sending
**Cause:** Missing `RESEND_API_KEY`
**Fix:** Add to `.env`:
```bash
RESEND_API_KEY=re_your_api_key_here
```

---

## 🧪 Testing Checklist

Before deploying to production:

- [ ] Rate limiting blocks after configured attempts
- [ ] Strong password required for registration
- [ ] Weak passwords are rejected with clear errors
- [ ] Account locks after 5 failed login attempts
- [ ] Lockout email notification is sent
- [ ] Account unlocks automatically after 30 minutes
- [ ] Successful login resets failed attempt counter
- [ ] Security headers present in all responses
- [ ] Stripe webhook signature verification works
- [ ] Duplicate webhook events are ignored
- [ ] Input sanitization prevents XSS in text fields
- [ ] Password reset flow works end-to-end
- [ ] CORS headers configured correctly

---

## 📞 Support

For questions or issues:
1. Check the main implementation summary: `SECURITY_IMPLEMENTATION_SUMMARY.md`
2. Review error logs in `backend/logs/`
3. Contact the development team

---

## 🔐 Security Best Practices

### DO
✅ Use environment variables for secrets
✅ Run database migrations before deployment
✅ Test security features in staging first
✅ Monitor failed login attempts
✅ Keep dependencies updated
✅ Use HTTPS in production
✅ Set strong JWT secret keys

### DON'T
❌ Commit `.env` files to version control
❌ Disable signature verification in production
❌ Use weak passwords for test accounts
❌ Skip database migrations
❌ Ignore security warnings in logs
❌ Expose sensitive data in error messages
❌ Use development settings in production

---

**Remember: Security is a continuous process, not a one-time implementation.**
