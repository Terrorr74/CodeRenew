# Docker Deployment Quick Start

## 🚀 Deploy to Staging in 5 Minutes

### Prerequisites
- Docker & Docker Compose installed
- `.env.staging` file configured

### Quick Setup

**Option 1: Minimal config (EPSS testing only)**
```bash
# Use minimal config - no API keys needed!
cp .env.staging.minimal .env.staging

# Edit passwords only
nano .env.staging
```

**Option 2: Full config (all features)**
```bash
# Use full config template
cp .env.staging.example .env.staging

# Edit all values including optional API keys
nano .env.staging
```

### One-Command Deployment

```bash
./scripts/deploy-staging-docker.sh
```

This script will:
1. ✅ Create database backup
2. ✅ Pull latest code
3. ✅ Build Docker images
4. ✅ Run database migration (includes EPSS fields)
5. ✅ Start all services (API, Celery, Frontend, Database, Redis, Nginx)
6. ✅ Run verification tests (API health, EPSS service, Celery workers)
7. ✅ Show deployment summary

---

## 🔑 Environment Variables Reference

### ✅ Required (EPSS Integration)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `DATABASE_URL`
- `REDIS_PASSWORD`
- `SECRET_KEY`
- `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_APP_URL`

### ⚙️ Optional (Extended Features)
- `ANTHROPIC_API_KEY` - Only for AI-powered WordPress scanning
- `STRIPE_SECRET_KEY` - Only for payment processing
- `RESEND_API_KEY` - Only for email notifications

**Important:** EPSS integration works WITHOUT `ANTHROPIC_API_KEY`!
The EPSS API (https://api.first.org) is public and requires no authentication.

---

## 📦 Manual Deployment Steps

If you prefer manual control:

### 1. Setup Environment

```bash
# Copy and configure environment variables
cp .env.staging.example .env.staging
nano .env.staging  # Edit with your values
```

### 2. Build & Deploy

```bash
# Build images
docker compose -f docker-compose.yml -f docker-compose.staging.yml build

# Start database first
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d db redis

# Wait 10 seconds for database to initialize
sleep 10

# Run migration
docker compose -f docker-compose.yml -f docker-compose.staging.yml run --rm backend alembic upgrade head

# Start all services
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

### 3. Verify Deployment

```bash
# Check service status
docker compose -f docker-compose.yml -f docker-compose.staging.yml ps

# Test API health
curl http://localhost:8000/api/v1/health

# Check logs
docker compose -f docker-compose.yml -f docker-compose.staging.yml logs -f
```

---

## 🔍 Verification Checklist

After deployment, verify these components:

### ✅ Services Running

```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml ps
```

Expected output:
- ✅ `coderenew_db_staging` - healthy
- ✅ `coderenew_redis_staging` - healthy
- ✅ `coderenew_backend_staging` - healthy
- ✅ `coderenew_celery_worker_staging` - running
- ✅ `coderenew_celery_beat_staging` - running
- ✅ `coderenew_frontend_staging` - healthy
- ✅ `coderenew_nginx_staging` - running

### ✅ EPSS Database Migration

```bash
# Check migration version (should show 007_add_epss_fields)
docker compose -f docker-compose.yml -f docker-compose.staging.yml \
  exec backend alembic current

# Verify EPSS columns exist
docker compose -f docker-compose.yml -f docker-compose.staging.yml \
  exec db psql -U coderenew -d coderenew_staging -c "\d scan_results" | grep epss
```

Expected columns:
- `cve_id` (character varying)
- `epss_score` (double precision)
- `epss_percentile` (double precision)
- `epss_updated_at` (timestamp with time zone)

### ✅ EPSS Service Test

```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml \
  exec backend python3 -c "
import asyncio
from app.services.epss import get_epss_service

async def test():
    epss = get_epss_service()
    score = await epss.get_epss_score('CVE-2021-44228')
    print(f'EPSS Score: {score.epss_score if score else None}')

asyncio.run(test())
"
```

Expected: `EPSS Score: 0.9745` (or similar high score for Log4Shell)

### ✅ API Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/health | jq

# Test EPSS API directly
curl "https://api.first.org/data/v1/epss?cve=CVE-2021-44228" | jq
```

### ✅ Celery Tasks

```bash
# Check active tasks
docker compose -f docker-compose.yml -f docker-compose.staging.yml \
  exec celery_worker celery -A app.core.celery_app inspect active

# Check registered tasks
docker compose -f docker-compose.yml -f docker-compose.staging.yml \
  exec celery_worker celery -A app.core.celery_app inspect registered | grep epss
```

Expected tasks:
- `app.tasks.epss_tasks.enrich_scan_results_with_epss`
- `app.tasks.epss_tasks.refresh_all_epss_scores_daily`

### ✅ Frontend Display

Open browser: `http://localhost:3000/scans/1`

Verify:
- [ ] EPSS risk badges are visible (color-coded: Critical/High/Medium/Low)
- [ ] Sort dropdown has "Exploit Risk (EPSS)" option
- [ ] CVE IDs are displayed
- [ ] Sorting by EPSS score works correctly
- [ ] Risk badges show score percentage

---

## 🛠️ Common Operations

### View Logs

```bash
# All services
docker compose -f docker-compose.yml -f docker-compose.staging.yml logs -f

# Specific service
docker compose -f docker-compose.yml -f docker-compose.staging.yml logs -f backend

# Filter for EPSS
docker compose -f docker-compose.yml -f docker-compose.staging.yml logs backend | grep -i epss
```

### Restart Services

```bash
# Restart specific service
docker compose -f docker-compose.yml -f docker-compose.staging.yml restart backend

# Restart all services
docker compose -f docker-compose.yml -f docker-compose.staging.yml restart
```

### Database Operations

```bash
# Connect to PostgreSQL
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec db \
  psql -U coderenew -d coderenew_staging

# Backup database
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec db \
  pg_dump -U coderenew coderenew_staging > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Execute Commands

```bash
# Backend shell
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec backend /bin/bash

# Python REPL
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec backend python3

# Run migration
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec backend \
  alembic upgrade head
```

### Resource Monitoring

```bash
# Resource usage
docker stats

# Disk usage
docker system df

# Clean up old images
docker image prune -a
```

---

## 🚨 Troubleshooting

### Backend Not Starting

```bash
# Check logs
docker compose -f docker-compose.yml -f docker-compose.staging.yml logs backend

# Common issues:
# 1. Database not ready - wait 30 seconds and restart
# 2. Missing environment variables - check .env.staging
# 3. Port already in use - change port in docker-compose.staging.yml
```

### Database Migration Fails

```bash
# Check current version
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec backend \
  alembic current

# Check migration history
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec backend \
  alembic history

# Rollback one version
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec backend \
  alembic downgrade -1
```

### EPSS Service Not Working

```bash
# Test EPSS API directly
curl "https://api.first.org/data/v1/epss?cve=CVE-2021-44228"

# Check httpx is installed
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec backend \
  pip list | grep httpx

# Check backend logs for errors
docker compose -f docker-compose.yml -f docker-compose.staging.yml logs backend | grep -i epss
```

### Celery Workers Not Running

```bash
# Check worker status
docker compose -f docker-compose.yml -f docker-compose.staging.yml ps | grep celery

# Check worker logs
docker compose -f docker-compose.yml -f docker-compose.staging.yml logs celery_worker

# Restart workers
docker compose -f docker-compose.yml -f docker-compose.staging.yml restart celery_worker celery_beat
```

---

## 🔄 Rollback Procedure

If deployment fails:

### 1. Stop Services

```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml down
```

### 2. Restore Database

```bash
# Start database only
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d db

# Restore from backup
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec -T db \
  psql -U coderenew -d coderenew_staging < backups/coderenew_staging_YYYYMMDD_HHMMSS.sql
```

### 3. Rollback Migration

```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml run --rm backend \
  alembic downgrade -1
```

### 4. Restart Services

```bash
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

---

## 📊 Performance Expectations

### Resource Usage

| Service | CPU | Memory | Notes |
|---------|-----|--------|-------|
| Backend | <50% | ~400MB | With 2 workers |
| Celery Worker | <30% | ~300MB | Concurrency: 2 |
| Celery Beat | <5% | ~100MB | Scheduler only |
| Database | <20% | ~200MB | Small dataset |
| Redis | <10% | ~50MB | In-memory cache |
| Frontend | <10% | ~200MB | Next.js production |
| Nginx | <5% | ~20MB | Reverse proxy |

**Total Expected:** ~2 CPU cores, ~1.3GB RAM

### Response Times

| Endpoint | Target | Expected |
|----------|--------|----------|
| API Health | <100ms | ~50ms |
| Scan Results (with EPSS) | <500ms | ~300ms |
| EPSS API Call | <1s | ~400ms |
| Database Queries | <50ms | ~10ms |
| Frontend Load | <2s | ~1s |

---

## 🎯 Success Criteria

Deployment is successful when:

- [x] All 7 containers are running
- [x] Database migration shows version 007 (EPSS fields)
- [x] API health check returns 200 OK
- [x] EPSS service test passes (returns score for CVE-2021-44228)
- [x] Celery workers respond to ping
- [x] Frontend loads without errors
- [x] No critical errors in logs (first 5 minutes)

---

## 📚 Additional Resources

- **Full Deployment Guide:** [DOCKER_STAGING_DEPLOY.md](./DOCKER_STAGING_DEPLOY.md)
- **Manual Deployment:** [EPSS_STAGING_DEPLOYMENT.md](./EPSS_STAGING_DEPLOYMENT.md)
- **Quick Deploy Guide:** [QUICK_DEPLOY_GUIDE.md](./QUICK_DEPLOY_GUIDE.md)
- **EPSS Implementation:** [EPSS_IMPLEMENTATION_SUMMARY.md](./EPSS_IMPLEMENTATION_SUMMARY.md)
- **Code Review:** [EPSS_REVIEW_SUMMARY.md](./EPSS_REVIEW_SUMMARY.md)

---

## 💡 Pro Tips

1. **Use aliases** for long commands:
   ```bash
   alias dc-staging='docker compose -f docker-compose.yml -f docker-compose.staging.yml'
   dc-staging ps
   dc-staging logs -f backend
   ```

2. **Monitor logs in real-time** during deployment:
   ```bash
   dc-staging logs -f | grep -i "error\|epss\|migration"
   ```

3. **Quick health check** one-liner:
   ```bash
   dc-staging ps && curl -f http://localhost:8000/api/v1/health && echo "✅ All good!"
   ```

4. **Backup before every deployment:**
   ```bash
   ./scripts/deploy-staging-docker.sh  # Already includes automatic backup
   ```

5. **Test EPSS locally first:**
   ```bash
   curl "https://api.first.org/data/v1/epss?cve=CVE-2021-44228" | jq
   ```

---

**Ready to deploy?**

```bash
./scripts/deploy-staging-docker.sh
```

**Questions?** Check [DOCKER_STAGING_DEPLOY.md](./DOCKER_STAGING_DEPLOY.md) for detailed guide.
