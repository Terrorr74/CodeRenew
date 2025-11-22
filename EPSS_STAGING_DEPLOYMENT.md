# EPSS Integration - Staging Deployment Guide

**Target Environment:** Staging
**Deployment Date:** 2025-11-22
**Estimated Time:** 2-3 hours

---

## 🎯 Pre-Deployment Checklist

### Prerequisites

- [ ] Git repository up to date (`git pull origin main`)
- [ ] Staging server access credentials
- [ ] Database backup completed
- [ ] Staging environment variables configured
- [ ] Celery worker and beat running

### Required Access

- SSH access to staging server
- Database access (PostgreSQL)
- Deployment permissions
- Monitoring dashboard access

---

## 📋 Step-by-Step Deployment

### Step 1: Backup Current State (15 minutes)

```bash
# SSH into staging server
ssh user@staging.coderenew.com

# Backup database
sudo -u postgres pg_dump coderenew_staging > \
  ~/backups/coderenew_staging_pre_epss_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh ~/backups/coderenew_staging_pre_epss_*.sql

# Backup current code
cd /var/www/coderenew
sudo tar -czf ~/backups/coderenew_code_$(date +%Y%m%d_%H%M%S).tar.gz .

echo "✅ Backups completed"
```

**Rollback Plan:**
```bash
# If needed, restore database
sudo -u postgres psql coderenew_staging < ~/backups/coderenew_staging_pre_epss_*.sql
```

---

### Step 2: Pull Latest Code (5 minutes)

```bash
# Navigate to project directory
cd /var/www/coderenew

# Stash any local changes
git stash

# Pull latest changes
git pull origin main

# Verify EPSS files exist
ls -la backend/app/services/epss/
ls -la backend/alembic/versions/007_add_epss_fields.py

echo "✅ Code updated"
```

**Expected files:**
```
backend/app/services/epss/
├── __init__.py
├── epss_service.py
├── enrichment.py
└── README.md

backend/alembic/versions/
└── 007_add_epss_fields.py

backend/app/tasks/
└── epss_tasks.py
```

---

### Step 3: Backend Deployment (30 minutes)

#### 3.1 Install Dependencies

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies (httpx for EPSS API)
pip install -r requirements.txt

# Verify httpx is installed
pip list | grep httpx

echo "✅ Dependencies installed"
```

#### 3.2 Run Database Migration

```bash
# Check current migration version
alembic current

# See pending migrations
alembic history

# Run migration (adds EPSS fields)
alembic upgrade head

# Verify migration
alembic current
# Expected output: 007 (head)

echo "✅ Migration completed"
```

**Verify database changes:**
```bash
# Connect to database
psql coderenew_staging

# Check new columns
\d scan_results

# Expected output:
# Column          | Type                     | Nullable
# ----------------+--------------------------+----------
# cve_id          | character varying        | YES
# epss_score      | double precision         | YES
# epss_percentile | double precision         | YES
# epss_updated_at | timestamp with time zone | YES

# Check indexes
\di scan_results*

# Expected indexes:
# ix_scan_results_cve_id
# ix_scan_results_epss_score
# ix_scan_results_scan_id_epss_score

\q

echo "✅ Database schema verified"
```

#### 3.3 Test Migration Rollback (Optional but Recommended)

```bash
# Test rollback
alembic downgrade -1

# Verify rolled back
psql coderenew_staging -c "\d scan_results" | grep epss
# Should return nothing

# Re-apply migration
alembic upgrade head

# Verify columns exist again
psql coderenew_staging -c "\d scan_results" | grep epss
# Should show epss_* columns

echo "✅ Rollback tested successfully"
```

#### 3.4 Restart Backend API

```bash
# Using systemd
sudo systemctl restart coderenew-api

# Or using supervisor
sudo supervisorctl restart coderenew-api

# Check service status
sudo systemctl status coderenew-api

# Check logs for errors
sudo tail -f /var/log/coderenew/api.log

# Expected: No errors, API started successfully

echo "✅ Backend API restarted"
```

---

### Step 4: Configure Celery Tasks (20 minutes)

#### 4.1 Update Celery Configuration

```bash
cd /var/www/coderenew/backend

# Verify Celery Beat schedule exists
grep -A 5 "refresh-epss-daily" app/core/celery_app.py
```

**If not present, add to `app/core/celery_app.py`:**
```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'refresh-epss-daily': {
        'task': 'app.tasks.epss_tasks.refresh_all_epss_scores_daily',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM UTC daily
    },
}
```

#### 4.2 Restart Celery Services

```bash
# Restart Celery worker
sudo systemctl restart celery-worker

# Restart Celery beat scheduler
sudo systemctl restart celery-beat

# Verify services are running
sudo systemctl status celery-worker
sudo systemctl status celery-beat

# Check Celery logs
sudo tail -f /var/log/celery/worker.log
sudo tail -f /var/log/celery/beat.log

echo "✅ Celery services restarted"
```

#### 4.3 Test EPSS Task Manually

```bash
# Enter Python shell
cd /var/www/coderenew/backend
source venv/bin/activate
python

# Test EPSS service
>>> from app.services.epss import get_epss_service
>>> import asyncio
>>>
>>> async def test():
...     epss = get_epss_service()
...     score = await epss.get_epss_score('CVE-2021-44228')
...     print(f"EPSS Score: {score.epss_score if score else 'Not found'}")
...     return score
>>>
>>> result = asyncio.run(test())
>>> # Expected: EPSS Score: 0.9445 (or similar)
>>> exit()

echo "✅ EPSS service tested"
```

---

### Step 5: Frontend Deployment (20 minutes)

```bash
cd /var/www/coderenew/frontend

# Install dependencies (if package.json changed)
npm install

# Build frontend
npm run build

# Verify build output
ls -la .next/
ls -la out/ # if using static export

# Deploy build (method depends on your setup)

# Option A: Using PM2
pm2 restart coderenew-frontend

# Option B: Using systemd
sudo systemctl restart coderenew-frontend

# Option C: Static files to nginx
sudo cp -r .next/static /var/www/html/coderenew/

# Verify deployment
curl http://staging.coderenew.com/scans/1
# Should return HTML with EPSS-related elements

echo "✅ Frontend deployed"
```

---

### Step 6: Verification & Testing (30 minutes)

#### 6.1 API Health Check

```bash
# Test API is responding
curl -X GET "http://staging.coderenew.com/api/health" | jq

# Test scans endpoint
curl -X GET "http://staging.coderenew.com/api/v1/scans" \
  -H "Authorization: Bearer YOUR_TEST_TOKEN" | jq

# Verify response includes EPSS fields
curl -X GET "http://staging.coderenew.com/api/v1/scans/1" \
  -H "Authorization: Bearer YOUR_TEST_TOKEN" | jq '.results[0]'

# Expected fields in response:
# {
#   "cve_id": "CVE-2024-1234",
#   "epss_score": 0.75,
#   "epss_percentile": 0.95,
#   "epss_updated_at": "2025-11-22T..."
# }

echo "✅ API verified"
```

#### 6.2 Database Verification

```bash
# Check if EPSS data is being populated
psql coderenew_staging -c "
SELECT COUNT(*) as total_results,
       COUNT(epss_score) as with_epss,
       ROUND(COUNT(epss_score)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as coverage_pct
FROM scan_results
WHERE created_at > NOW() - INTERVAL '7 days';
"

# View sample EPSS data
psql coderenew_staging -c "
SELECT id, cve_id, epss_score, epss_percentile, severity
FROM scan_results
WHERE epss_score IS NOT NULL
ORDER BY epss_score DESC
LIMIT 5;
"

echo "✅ Database verified"
```

#### 6.3 Celery Task Test

```bash
# Trigger enrichment task manually for testing
cd /var/www/coderenew/backend
source venv/bin/activate

celery -A app.core.celery_app call \
  app.tasks.epss_tasks.enrich_scan_results_with_epss \
  --args='[1]'

# Monitor task execution
celery -A app.core.celery_app events

# Check task results
psql coderenew_staging -c "
SELECT id, cve_id, epss_score, epss_updated_at
FROM scan_results
WHERE scan_id = 1 AND epss_score IS NOT NULL
LIMIT 3;
"

echo "✅ Celery tasks verified"
```

#### 6.4 Frontend UI Test

**Manual Browser Testing:**

1. **Open staging URL:**
   ```
   https://staging.coderenew.com/scans/1
   ```

2. **Verify EPSS elements visible:**
   - [ ] Sort dropdown shows "Exploit Risk (EPSS)"
   - [ ] Risk badges are color-coded
   - [ ] CVE identifiers displayed
   - [ ] EPSS percentile shown
   - [ ] Sorting by EPSS works

3. **Test different scenarios:**
   - [ ] Scan with EPSS data displays correctly
   - [ ] Scan without EPSS data degrades gracefully
   - [ ] Sort by EPSS vs Severity works
   - [ ] Tooltips show EPSS details

**Screenshot checklist:**
- Take screenshots for documentation
- Verify UI matches design specifications

echo "✅ Frontend UI verified"

---

### Step 7: Performance Testing (20 minutes)

#### 7.1 EPSS API Performance

```bash
# Test EPSS API response time
time curl -X GET "https://api.first.org/data/v1/epss?cve=CVE-2021-44228"

# Expected: < 500ms

# Test batch query
time curl -X GET "https://api.first.org/data/v1/epss?cve=CVE-2021-44228,CVE-2024-1234"

# Expected: < 1s for batch
```

#### 7.2 Database Query Performance

```bash
psql coderenew_staging

-- Test sorting by EPSS
EXPLAIN ANALYZE
SELECT * FROM scan_results
WHERE scan_id = 1
ORDER BY epss_score DESC NULLS LAST
LIMIT 50;

-- Expected: Uses index, execution time < 10ms

-- Test filtered query
EXPLAIN ANALYZE
SELECT * FROM scan_results
WHERE scan_id = 1 AND epss_score > 0.5
ORDER BY epss_score DESC;

-- Expected: Uses ix_scan_results_scan_id_epss_score

\q
```

#### 7.3 Load Test (Optional)

```bash
# Install apache bench if not available
sudo apt-get install apache2-utils

# Test scan endpoint under load
ab -n 100 -c 10 \
  -H "Authorization: Bearer YOUR_TEST_TOKEN" \
  http://staging.coderenew.com/api/v1/scans/1/

# Expected:
# - 100% success rate
# - Mean response time < 200ms
```

---

### Step 8: Monitoring Setup (15 minutes)

#### 8.1 Set Up Logging

```bash
# Check EPSS-related logs
sudo tail -f /var/log/coderenew/api.log | grep -i epss

# Check Celery task logs
sudo tail -f /var/log/celery/worker.log | grep -i epss

# Set up log rotation if needed
sudo nano /etc/logrotate.d/coderenew
```

#### 8.2 Create Monitoring Alerts

**Example: DataDog/New Relic/Prometheus**

```yaml
# Alert: EPSS API High Error Rate
- name: epss_api_errors
  query: |
    sum(rate(epss_api_errors_total[5m])) > 0.05
  severity: warning
  message: "EPSS API error rate > 5%"

# Alert: EPSS Enrichment Task Failures
- name: epss_task_failures
  query: |
    sum(rate(celery_task_failures{task="enrich_scan_results_with_epss"}[10m])) > 0
  severity: critical
  message: "EPSS enrichment tasks failing"
```

#### 8.3 Health Check Endpoint

Add to `backend/app/api/v1/endpoints/health.py`:

```python
from fastapi import APIRouter
from app.services.epss import get_epss_service

router = APIRouter()

@router.get("/health/epss")
async def epss_health_check():
    """Check EPSS service health"""
    try:
        service = get_epss_service()
        # Test with known CVE
        score = await service.get_epss_score('CVE-2021-44228')

        return {
            "status": "healthy" if score else "degraded",
            "cache_valid": service._is_cache_valid(),
            "cache_size": len(service._cache),
            "test_cve": "CVE-2021-44228",
            "test_score": score.epss_score if score else None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

Test health endpoint:
```bash
curl http://staging.coderenew.com/api/health/epss | jq
```

---

### Step 9: Post-Deployment Validation (10 minutes)

#### 9.1 End-to-End Test

**Scenario: Create New Scan and Verify EPSS Enrichment**

```bash
# 1. Create test scan via API
curl -X POST "http://staging.coderenew.com/api/v1/scans" \
  -H "Authorization: Bearer YOUR_TEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": 1,
    "wordpress_version_from": "6.0",
    "wordpress_version_to": "6.4"
  }'

# Note the scan_id from response

# 2. Wait for scan to complete (or trigger manually)

# 3. Verify EPSS data was enriched
curl "http://staging.coderenew.com/api/v1/scans/{scan_id}" \
  -H "Authorization: Bearer YOUR_TEST_TOKEN" | jq '.results[] | select(.epss_score != null)'

# 4. Check frontend display
# Open: http://staging.coderenew.com/scans/{scan_id}
# Verify EPSS badges visible
```

#### 9.2 Smoke Tests Checklist

- [ ] API responds to requests
- [ ] Database contains EPSS columns
- [ ] Frontend displays EPSS data
- [ ] Sorting by EPSS works
- [ ] Celery tasks execute successfully
- [ ] No errors in logs
- [ ] Performance is acceptable (<500ms API, <10ms DB)

---

## 🚨 Rollback Procedure

**If critical issues are discovered:**

### Immediate Rollback (5 minutes)

```bash
# 1. Rollback database migration
cd /var/www/coderenew/backend
source venv/bin/activate
alembic downgrade -1

# 2. Revert code
git revert HEAD
git push origin main

# 3. Redeploy previous version
git checkout HEAD~1
sudo systemctl restart coderenew-api
sudo systemctl restart celery-worker
pm2 restart coderenew-frontend

# 4. Verify rollback
curl http://staging.coderenew.com/api/health

# 5. Restore database if needed
sudo -u postgres psql coderenew_staging < ~/backups/coderenew_staging_pre_epss_*.sql
```

---

## 📊 Post-Deployment Monitoring (24 hours)

### Metrics to Track

**Day 1 (First 24 hours):**

```bash
# Check every 2 hours:

# 1. Error rate
sudo tail -100 /var/log/coderenew/api.log | grep -i error | wc -l

# 2. EPSS API response times
sudo grep "EPSS API" /var/log/coderenew/api.log | tail -20

# 3. Database query performance
psql coderenew_staging -c "
SELECT
    query,
    mean_exec_time,
    calls
FROM pg_stat_statements
WHERE query LIKE '%epss%'
ORDER BY mean_exec_time DESC
LIMIT 5;
"

# 4. Celery task success rate
celery -A app.core.celery_app inspect stats | grep epss

# 5. Cache hit rate (add logging to track this)
sudo grep "cache hit" /var/log/coderenew/api.log | wc -l
```

### Daily Report Template

```
EPSS Staging Deployment - Day 1 Report
Date: 2025-11-22

✅ Deployment Status: Success

📊 Metrics:
- API Uptime: 100%
- Error Rate: 0.1%
- EPSS API Response Time: 250ms avg
- Database Query Time: 3ms avg
- Cache Hit Rate: 92%
- Celery Task Success: 100%

🔍 Issues Found: None

📝 Next Steps:
- Continue monitoring for 48 hours
- Prepare production deployment plan
```

---

## ✅ Deployment Success Criteria

**Before proceeding to production:**

- [ ] No critical errors in 24 hours
- [ ] API response time < 500ms (95th percentile)
- [ ] Database query time < 10ms
- [ ] Cache hit rate > 85%
- [ ] Celery task success rate > 95%
- [ ] Frontend displays correctly
- [ ] No user-reported issues
- [ ] Performance acceptable under load
- [ ] Rollback procedure tested and documented

---

## 📞 Support & Escalation

**Issues During Deployment:**

| Severity | Response Time | Contact |
|----------|--------------|---------|
| P0 - Critical (Site Down) | Immediate | DevOps Team Lead |
| P1 - High (Feature Broken) | < 1 hour | Backend Developer |
| P2 - Medium (Degraded) | < 4 hours | Development Team |
| P3 - Low (Minor Issues) | Next day | Bug Tracker |

**Emergency Contacts:**
- DevOps Lead: devops@coderenew.com
- Backend Lead: backend@coderenew.com
- On-call: +1-XXX-XXX-XXXX

---

## 📝 Deployment Checklist Summary

**Pre-Deployment:**
- [x] Backups completed
- [x] Code pulled from main
- [x] Dependencies installed

**Deployment:**
- [ ] Database migration run
- [ ] Backend API restarted
- [ ] Celery services restarted
- [ ] Frontend deployed

**Verification:**
- [ ] API health check passes
- [ ] Database schema verified
- [ ] Celery tasks working
- [ ] Frontend UI displays correctly
- [ ] Performance acceptable

**Monitoring:**
- [ ] Logs configured
- [ ] Alerts set up
- [ ] Health endpoint active
- [ ] Metrics dashboard updated

**Post-Deployment:**
- [ ] End-to-end test passed
- [ ] Smoke tests completed
- [ ] 24-hour monitoring plan active
- [ ] Team notified of deployment

---

**Deployment Timeline:**
- **Start:** 2025-11-22 10:00 AM
- **Expected End:** 2025-11-22 1:00 PM
- **Monitoring Period:** 24-48 hours

**Deployed By:** [Your Name]
**Reviewed By:** [Reviewer Name]
**Approved By:** [Manager Name]

---

**Status:** Ready for Staging Deployment ✅
