# Quick Staging Deployment Guide

## 🚀 3 Ways to Deploy EPSS Integration

### Option 1: Automated Script (Recommended - 15 minutes)

```bash
# Set environment variables (if needed)
export STAGING_HOST=staging.coderenew.com
export STAGING_USER=deploy

# Run deployment script
./scripts/deploy-staging.sh
```

**What it does:**
1. ✅ Creates backups (database + code)
2. ✅ Pulls latest code
3. ✅ Installs dependencies
4. ✅ Runs database migration
5. ✅ Restarts all services
6. ✅ Runs verification tests
7. ✅ Shows deployment summary

---

### Option 2: Manual Deployment (2-3 hours)

Follow the complete guide: **[EPSS_STAGING_DEPLOYMENT.md](./EPSS_STAGING_DEPLOYMENT.md)**

**Steps:**
1. Backup current state
2. Pull latest code
3. Install backend dependencies
4. Run database migration
5. Restart backend API
6. Configure Celery tasks
7. Deploy frontend
8. Verification & testing
9. Post-deployment monitoring

---

### Option 3: Docker Deployment (If using Docker)

```bash
# SSH into staging
ssh deploy@staging.coderenew.com

# Pull latest code
cd /var/www/coderenew
git pull origin main

# Rebuild and restart containers
docker-compose -f docker-compose.staging.yml down
docker-compose -f docker-compose.staging.yml up -d --build

# Run migration
docker-compose -f docker-compose.staging.yml exec backend \
  alembic upgrade head

# Verify
docker-compose -f docker-compose.staging.yml ps
docker-compose -f docker-compose.staging.yml logs -f
```

---

## ✅ Pre-Deployment Checklist

Before deploying:

- [ ] **Code committed:** Latest EPSS code is in git
- [ ] **Tests written:** Unit tests created (see EPSS_NEXT_STEPS.md)
- [ ] **Backup plan:** Know how to rollback if needed
- [ ] **Access verified:** Can SSH into staging server
- [ ] **Services identified:** Know which services to restart
- [ ] **Monitoring ready:** Logs and health checks accessible

---

## 🔍 Quick Verification (After Deployment)

### 1. Check Services Running

```bash
ssh deploy@staging.coderenew.com

# Check all services
sudo systemctl status coderenew-api
sudo systemctl status celery-worker
sudo systemctl status celery-beat
pm2 status  # for frontend
```

### 2. Test EPSS API

```bash
# Test EPSS service directly
curl "https://api.first.org/data/v1/epss?cve=CVE-2021-44228" | jq

# Test application health
curl http://staging.coderenew.com/api/health | jq
```

### 3. Verify Database

```bash
ssh deploy@staging.coderenew.com

# Connect to database
psql coderenew_staging

# Check EPSS columns exist
\d scan_results

# Check for EPSS data
SELECT COUNT(*) FROM scan_results WHERE epss_score IS NOT NULL;

\q
```

### 4. Test Frontend

**Open in browser:**
```
http://staging.coderenew.com/scans/1
```

**Verify:**
- [ ] Page loads without errors
- [ ] Sort dropdown shows "Exploit Risk (EPSS)"
- [ ] Risk badges are color-coded
- [ ] CVE IDs are displayed
- [ ] Sorting by EPSS works

### 5. Test Celery Task

```bash
ssh deploy@staging.coderenew.com
cd /var/www/coderenew/backend
source venv/bin/activate

# Manually trigger EPSS enrichment
celery -A app.core.celery_app call \
  app.tasks.epss_tasks.enrich_scan_results_with_epss \
  --args='[1]'

# Check task executed
celery -A app.core.celery_app inspect active
```

---

## 🚨 Rollback (If Something Goes Wrong)

### Quick Rollback

```bash
ssh deploy@staging.coderenew.com

# 1. Rollback database migration
cd /var/www/coderenew/backend
source venv/bin/activate
alembic downgrade -1

# 2. Restore previous code
cd /var/www/coderenew
tar -xzf ~/backups/coderenew_code_*.tar.gz

# 3. Restart services
sudo systemctl restart coderenew-api
sudo systemctl restart celery-worker
pm2 restart all

# 4. Verify
curl http://staging.coderenew.com/api/health
```

### Full Database Restore

```bash
# If migration caused issues
sudo -u postgres psql coderenew_staging < \
  ~/backups/coderenew_staging_pre_epss_*.sql
```

---

## 📊 Post-Deployment Monitoring

### Monitor for 24 Hours

```bash
# Watch API logs
ssh deploy@staging.coderenew.com
sudo tail -f /var/log/coderenew/api.log | grep -i epss

# Watch Celery logs
sudo tail -f /var/log/celery/worker.log | grep -i epss

# Check for errors every few hours
sudo tail -100 /var/log/coderenew/api.log | grep -i error
```

### Key Metrics to Track

| Metric | Target | Check Command |
|--------|--------|---------------|
| API Response Time | <500ms | `curl -w "%{time_total}\n" http://staging/api/health` |
| Error Rate | <1% | Check logs for error count |
| EPSS API Calls | Success | `grep "EPSS API" /var/log/coderenew/api.log` |
| Celery Tasks | Running | `celery -A app.core.celery_app inspect active` |
| Database Queries | <10ms | Check slow query log |

---

## 🎯 Success Criteria

**Deployment is successful when:**

- [x] All services running (API, Celery, Frontend)
- [x] Database migration completed (version 007)
- [x] EPSS columns exist in scan_results table
- [x] EPSS service responds to test queries
- [x] Frontend displays EPSS data correctly
- [x] No critical errors in logs (first hour)
- [x] Performance within acceptable range

---

## 📞 Getting Help

**If deployment fails:**

1. **Check logs first:**
   ```bash
   sudo tail -100 /var/log/coderenew/api.log
   sudo tail -100 /var/log/celery/worker.log
   ```

2. **Run verification tests:**
   ```bash
   # Test EPSS service
   cd /var/www/coderenew/backend
   source venv/bin/activate
   python -c "
   import asyncio
   from app.services.epss import get_epss_service
   async def test():
       epss = get_epss_service()
       score = await epss.get_epss_score('CVE-2021-44228')
       print(f'Score: {score.epss_score if score else None}')
   asyncio.run(test())
   "
   ```

3. **Check service status:**
   ```bash
   sudo systemctl status coderenew-api
   sudo systemctl status celery-worker
   ```

4. **Review deployment guide:**
   - Full guide: `EPSS_STAGING_DEPLOYMENT.md`
   - Code review: `EPSS_CODE_REVIEW.md`
   - Next steps: `EPSS_NEXT_STEPS.md`

---

## 📅 Deployment Timeline

**Estimated Timeline:**

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Preparation** | 30 min | Backups, pre-checks |
| **Deployment** | 45 min | Code, migration, services |
| **Verification** | 30 min | Tests, validation |
| **Monitoring** | 24 hours | Log monitoring, metrics |
| **Sign-off** | 1 hour | Documentation, report |

**Total:** ~3 hours active work + 24 hours monitoring

---

## ✨ After Successful Deployment

**Next Steps:**

1. **Monitor for 24-48 hours**
   - Watch error logs
   - Track performance metrics
   - Note any issues

2. **Run performance tests**
   - Load test with Apache Bench
   - Database query analysis
   - EPSS API stress test

3. **Gather user feedback**
   - Internal team testing
   - Note UX issues
   - Document improvements

4. **Prepare production deployment**
   - Update production checklist
   - Schedule deployment window
   - Communicate to stakeholders

---

## 🎉 Quick Deploy Command

**One-liner for experienced users:**

```bash
./scripts/deploy-staging.sh && \
  curl http://staging.coderenew.com/api/health && \
  echo "✅ Deployment complete!"
```

---

**Ready to deploy? Run:**
```bash
./scripts/deploy-staging.sh
```

**Questions? Check:**
- Full guide: `EPSS_STAGING_DEPLOYMENT.md`
- Troubleshooting: `EPSS_NEXT_STEPS.md`
