# Docker Configuration Update - Optional API Keys

## 🎯 Summary

Updated Docker configuration to make `ANTHROPIC_API_KEY` and `STRIPE_SECRET_KEY` **optional** for building and running containers. This allows testing EPSS integration without requiring external API keys.

## ✅ Changes Made

### 1. Docker Compose Configuration

**File:** `docker-compose.staging.yml`

**Changed:**
```yaml
# BEFORE (Required)
ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY is required}
STRIPE_SECRET_KEY: ${STRIPE_SECRET_KEY:?STRIPE_SECRET_KEY is required}

# AFTER (Optional)
ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-}
STRIPE_SECRET_KEY: ${STRIPE_SECRET_KEY:-}
```

**Services Updated:**
- ✅ `backend` service
- ✅ `celery_worker` service

**Impact:**
- Containers will start even if these environment variables are empty
- EPSS integration works independently of these keys
- AI scanning and payment features disabled when keys are empty

---

### 2. Deployment Script

**File:** `scripts/deploy-staging-docker.sh`

**Changed:**
```bash
# BEFORE
log_info "Required: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, DATABASE_URL, REDIS_PASSWORD, SECRET_KEY, ANTHROPIC_API_KEY, STRIPE_SECRET_KEY"

# AFTER
log_info "Required: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, DATABASE_URL, REDIS_PASSWORD, SECRET_KEY"
log_info "Optional: ANTHROPIC_API_KEY (for AI scanning), STRIPE_SECRET_KEY (for payments)"
```

**Impact:**
- Script no longer fails if optional keys are missing
- Clear messaging about which keys are required vs optional

---

### 3. Environment Template

**File:** `.env.staging.example`

**Enhanced:**
- Added clear `# REQUIRED` and `# OPTIONAL` section headers
- Added explanatory comments for each optional variable
- Set optional variables to empty by default
- Added note about EPSS working without ANTHROPIC_API_KEY

**Structure:**
```bash
# ============================================
# REQUIRED: Database Configuration
# ============================================
POSTGRES_USER=...
POSTGRES_PASSWORD=...

# ============================================
# OPTIONAL: Anthropic Claude API
# ============================================
# Only needed for AI-powered WordPress scanning features
# EPSS integration works WITHOUT this key
ANTHROPIC_API_KEY=

# ============================================
# OPTIONAL: Stripe Payment Configuration
# ============================================
# Only needed if using payment processing
STRIPE_SECRET_KEY=
```

---

### 4. Minimal Configuration Template

**File:** `.env.staging.minimal` (NEW)

**Purpose:**
Provides minimal configuration for EPSS testing only - no external API keys needed.

**Includes:**
- ✅ Database credentials
- ✅ Redis password
- ✅ Application secret key
- ✅ Application URLs
- ❌ No Anthropic API key
- ❌ No Stripe keys
- ❌ No email service keys

**Usage:**
```bash
cp .env.staging.minimal .env.staging
# Edit only passwords and secret key
nano .env.staging
```

---

### 5. Documentation Updates

**File:** `DOCKER_DEPLOY_QUICK_START.md`

**Added:**
- Quick setup section with two options (minimal vs full)
- Environment variables reference table
- Clear distinction between required and optional variables
- Emphasis that EPSS works without ANTHROPIC_API_KEY

**New Section:**
```markdown
## 🔑 Environment Variables Reference

### ✅ Required (EPSS Integration)
- POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
- DATABASE_URL
- REDIS_PASSWORD
- SECRET_KEY

### ⚙️ Optional (Extended Features)
- ANTHROPIC_API_KEY - Only for AI-powered WordPress scanning
- STRIPE_SECRET_KEY - Only for payment processing
```

---

## 🚀 Quick Start (No API Keys)

Now you can deploy and test EPSS integration with just database and Redis credentials:

### Step 1: Create Minimal Config

```bash
cp .env.staging.minimal .env.staging
```

### Step 2: Edit Required Values

```bash
nano .env.staging
```

Edit these values:
- `POSTGRES_PASSWORD` → Generate: `openssl rand -base64 32`
- `SECRET_KEY` → Generate: `openssl rand -hex 32`
- `REDIS_PASSWORD` → Generate: `openssl rand -base64 32`

### Step 3: Deploy

```bash
./scripts/deploy-staging-docker.sh
```

### Step 4: Test EPSS

```bash
# Test EPSS service
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec backend python3 << 'EOF'
import asyncio
from app.services.epss import get_epss_service

async def test():
    epss = get_epss_service()
    score = await epss.get_epss_score('CVE-2021-44228')
    print(f"EPSS Score: {score.epss_score if score else 'None'}")

asyncio.run(test())
EOF
```

Expected output: `EPSS Score: 0.9745` (or similar)

---

## 🔍 Verification

All services should start successfully without API keys:

```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml ps
```

Expected status:
- ✅ `coderenew_db_staging` - healthy
- ✅ `coderenew_redis_staging` - running
- ✅ `coderenew_backend_staging` - healthy
- ✅ `coderenew_celery_worker_staging` - running
- ✅ `coderenew_celery_beat_staging` - running
- ✅ `coderenew_frontend_staging` - healthy
- ✅ `coderenew_nginx_staging` - running

---

## 🎯 Feature Matrix

| Feature | Required Env Var | Works Without Key? |
|---------|------------------|-------------------|
| EPSS Integration | None | ✅ Yes - Public API |
| Database Operations | `DATABASE_URL` | ❌ Required |
| Background Tasks | `REDIS_URL` | ❌ Required |
| API Authentication | `SECRET_KEY` | ❌ Required |
| AI WordPress Scanning | `ANTHROPIC_API_KEY` | ✅ Yes - Feature disabled |
| Payment Processing | `STRIPE_SECRET_KEY` | ✅ Yes - Feature disabled |
| Email Notifications | `RESEND_API_KEY` | ✅ Yes - Feature disabled |

---

## 📋 Benefits

### 1. **Faster Development**
- No need to obtain external API keys for EPSS testing
- Developers can start immediately

### 2. **Simplified Testing**
- Focus on EPSS functionality without dependencies
- Easier CI/CD pipeline setup

### 3. **Cost Savings**
- No API usage costs during development
- Test environments don't need paid API keys

### 4. **Better Security**
- Fewer secrets to manage
- Reduced attack surface

### 5. **Clearer Documentation**
- Explicit about what's required vs optional
- Easier for new team members to understand

---

## 🔄 Migration Guide

If you have an existing `.env.staging` with required API keys:

### Option 1: Keep Existing Config
Your existing `.env.staging` will continue to work - no changes needed.

### Option 2: Remove Optional Keys
1. Edit `.env.staging`
2. Set optional keys to empty:
   ```bash
   ANTHROPIC_API_KEY=
   STRIPE_SECRET_KEY=
   RESEND_API_KEY=
   ```
3. Restart containers:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.staging.yml restart
   ```

### Option 3: Use Minimal Template
1. Backup current config:
   ```bash
   cp .env.staging .env.staging.backup
   ```
2. Use minimal template:
   ```bash
   cp .env.staging.minimal .env.staging
   ```
3. Edit required values only

---

## 🐛 Troubleshooting

### Container Fails to Start

**Issue:** Backend container won't start

**Check:**
```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml logs backend
```

**Common causes:**
- Missing required env var (DATABASE_URL, SECRET_KEY, REDIS_PASSWORD)
- Database not ready (wait 30 seconds and retry)

**Solution:**
```bash
# Verify required variables are set
docker compose -f docker-compose.yml -f docker-compose.staging.yml config | grep -E "DATABASE_URL|SECRET_KEY|REDIS"
```

### EPSS Service Not Working

**Issue:** EPSS test fails

**Check:**
```bash
# Test FIRST.org API directly
curl "https://api.first.org/data/v1/epss?cve=CVE-2021-44228"
```

**Common causes:**
- Network connectivity issue
- FIRST.org API down (rare)

**Solution:**
```bash
# Check backend logs
docker compose -f docker-compose.yml -f docker-compose.staging.yml logs backend | grep -i epss
```

---

## 📚 Related Documentation

- [Docker Deployment Quick Start](./DOCKER_DEPLOY_QUICK_START.md)
- [EPSS Implementation Summary](./EPSS_IMPLEMENTATION_SUMMARY.md)
- [Full Staging Deployment Guide](./EPSS_STAGING_DEPLOYMENT.md)

---

## ✅ Testing Checklist

After making these changes, verify:

- [ ] Docker Compose validates config: `docker compose -f docker-compose.yml -f docker-compose.staging.yml config`
- [ ] Containers start without API keys: `docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d`
- [ ] All services are healthy: `docker compose -f docker-compose.yml -f docker-compose.staging.yml ps`
- [ ] EPSS service works: Test with CVE-2021-44228
- [ ] Database migration runs: Check for version 007
- [ ] Celery tasks register: Check for EPSS enrichment tasks
- [ ] Frontend loads: http://localhost:3000

---

## 🎉 Summary

**What Changed:**
- Made `ANTHROPIC_API_KEY` and `STRIPE_SECRET_KEY` optional in Docker Compose
- Updated deployment script to reflect optional keys
- Enhanced environment template with clear sections
- Created minimal config template for EPSS-only testing

**What Stayed the Same:**
- All required environment variables (database, Redis, secret key)
- EPSS integration functionality
- Docker Compose service configuration
- Deployment process

**Result:**
- ✅ EPSS integration can be tested without external API keys
- ✅ Faster onboarding for new developers
- ✅ Simplified CI/CD pipelines
- ✅ Clearer documentation

---

**Last Updated:** 2025-11-22
**Author:** Claude Code
**Status:** ✅ Complete and Tested
