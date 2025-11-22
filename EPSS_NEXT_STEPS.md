# EPSS Integration - Next Steps & Action Items

**Status:** ✅ Implementation Complete - Ready for Testing Phase
**Last Updated:** 2025-11-22

---

## 🎯 Immediate Next Steps (Before Production)

### Step 1: Testing (Est: 1-2 days)

#### Unit Tests
Create `backend/tests/services/epss/test_epss_service.py`:

```python
import pytest
from app.services.epss import EPSSService, get_epss_service
from app.services.epss.enrichment import extract_cve_from_description

class TestEPSSService:
    @pytest.mark.asyncio
    async def test_get_single_epss_score(self):
        """Test fetching a single EPSS score"""
        service = EPSSService()
        score = await service.get_epss_score('CVE-2021-44228')

        assert score is not None
        assert score.cve == 'CVE-2021-44228'
        assert 0 <= score.epss_score <= 1
        assert 0 <= score.percentile <= 1

    @pytest.mark.asyncio
    async def test_batch_query(self):
        """Test batch CVE queries"""
        service = EPSSService()
        cves = ['CVE-2021-44228', 'CVE-2024-1234']
        scores = await service.get_epss_scores(cves)

        assert len(scores) > 0
        assert all(0 <= data.epss_score <= 1 for data in scores.values())

    @pytest.mark.asyncio
    async def test_cache_functionality(self):
        """Test caching works correctly"""
        service = EPSSService()

        # First call - hits API
        score1 = await service.get_epss_score('CVE-2021-44228')

        # Second call - should hit cache
        score2 = await service.get_epss_score('CVE-2021-44228')

        assert score1.epss_score == score2.epss_score
        assert service._is_cache_valid()

    @pytest.mark.asyncio
    async def test_missing_cve_handling(self):
        """Test handling of non-existent CVE"""
        service = EPSSService()
        score = await service.get_epss_score('CVE-9999-99999')

        assert score is None

    def test_cve_extraction(self):
        """Test CVE ID extraction from descriptions"""
        test_cases = [
            ("WordPress XSS (CVE-2024-1234)", "CVE-2024-1234"),
            ("Security issue cve-2021-44228 found", "CVE-2021-44228"),
            ("No CVE here", None),
            ("Multiple CVE-2024-1111 and CVE-2024-2222", "CVE-2024-1111")
        ]

        for description, expected in test_cases:
            result = extract_cve_from_description(description)
            assert result == expected

    @pytest.mark.asyncio
    async def test_error_handling(self, monkeypatch):
        """Test API error handling and fallback to cache"""
        service = EPSSService()

        # Populate cache
        await service.get_epss_score('CVE-2021-44228')

        # Simulate API failure
        async def mock_fetch_error(*args, **kwargs):
            raise Exception("API Error")

        monkeypatch.setattr(service, '_fetch_from_api', mock_fetch_error)

        # Should return cached result despite error
        score = await service.get_epss_score('CVE-2021-44228')
        assert score is not None
```

Run tests:
```bash
cd backend
pytest tests/services/epss/ -v --cov=app/services/epss
```

**Target:** 80%+ code coverage

---

### Step 2: Database Migration (Est: 30 minutes)

```bash
cd backend

# Backup database first!
pg_dump coderenew > backup_pre_epss_$(date +%Y%m%d).sql

# Run migration
alembic upgrade head

# Verify migration
alembic current

# Test rollback capability
alembic downgrade -1
alembic upgrade head

# Check tables
psql coderenew -c "\d scan_results"
```

**Expected Output:**
```
Column          | Type                     | Nullable
----------------+--------------------------+----------
cve_id          | character varying        | YES
epss_score      | double precision         | YES
epss_percentile | double precision         | YES
epss_updated_at | timestamp with time zone | YES

Indexes:
    "ix_scan_results_cve_id"
    "ix_scan_results_epss_score"
    "ix_scan_results_scan_id_epss_score"
```

---

### Step 3: Celery Configuration (Est: 30 minutes)

Update `backend/app/core/celery_app.py`:

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'refresh-epss-daily': {
        'task': 'app.tasks.epss_tasks.refresh_all_epss_scores_daily',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM UTC daily
    },
}
```

Start Celery worker and beat:
```bash
# Terminal 1: Worker
celery -A app.core.celery_app worker --loglevel=info

# Terminal 2: Beat scheduler
celery -A app.core.celery_app beat --loglevel=info
```

Test task manually:
```bash
celery -A app.core.celery_app call app.tasks.epss_tasks.enrich_scan_results_with_epss --args='[1]'
```

---

### Step 4: Monitoring Setup (Est: 1 hour)

#### Add Health Check Endpoint

Create `backend/app/api/v1/endpoints/health.py`:

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
            "cache_size": len(service._cache)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

#### Add Logging

Update `backend/app/services/epss/epss_service.py`:

```python
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Add to get_epss_scores():
logger.info(f"Fetching EPSS scores for {len(cves)} CVEs")

# Add to _fetch_from_api():
logger.debug(f"EPSS API request: {cve_param}")
logger.info(f"EPSS API response time: {response.elapsed.total_seconds():.2f}s")
```

---

## 📊 Integration Testing (Est: 2-3 hours)

### Test Scenario 1: New Scan with CVEs

```python
@pytest.mark.integration
async def test_full_scan_workflow_with_epss():
    """Test complete scan workflow with EPSS enrichment"""

    # 1. Create scan
    scan = Scan(
        site_id=1,
        user_id=1,
        wordpress_version_from="6.0",
        wordpress_version_to="6.4"
    )
    db.add(scan)
    db.commit()

    # 2. Add scan results with CVE IDs
    results = [
        ScanResult(
            scan_id=scan.id,
            severity="high",
            issue_type="security_issue",
            description="Log4Shell vulnerability (CVE-2021-44228)",
            cve_id="CVE-2021-44228"
        ),
        ScanResult(
            scan_id=scan.id,
            severity="medium",
            issue_type="security_issue",
            description="WordPress XSS (CVE-2024-1234)",
            cve_id="CVE-2024-1234"
        )
    ]
    db.add_all(results)
    db.commit()

    # 3. Enrich with EPSS
    from app.services.epss import enrich_results_with_epss
    await enrich_results_with_epss(results)

    # 4. Verify EPSS data
    db.refresh(results[0])
    assert results[0].epss_score is not None
    assert results[0].epss_percentile is not None
    assert results[0].epss_updated_at is not None

    # 5. Test sorting
    sorted_results = sorted(results, key=lambda r: r.epss_score or -1, reverse=True)
    assert sorted_results[0].epss_score >= sorted_results[1].epss_score
```

### Test Scenario 2: Background Task Enrichment

```python
@pytest.mark.integration
async def test_celery_enrichment_task():
    """Test Celery task enriches scan correctly"""

    # Create scan with results
    scan_id = create_test_scan_with_results()

    # Trigger enrichment task
    from app.tasks.epss_tasks import enrich_scan_results_with_epss
    result = enrich_scan_results_with_epss.delay(scan_id)

    # Wait for completion
    while not result.ready():
        await asyncio.sleep(0.1)

    # Verify
    task_result = result.get()
    assert task_result['enriched'] > 0
    assert task_result['skipped'] >= 0
```

---

## 🚀 Deployment Steps

### Staging Deployment

```bash
# 1. Deploy backend
cd backend
alembic upgrade head
systemctl restart coderenew-api
systemctl restart celery-worker
systemctl restart celery-beat

# 2. Deploy frontend
cd frontend
npm run build
npm run deploy:staging

# 3. Verify
curl https://staging.coderenew.com/api/health/epss
```

### Production Deployment

```bash
# 1. Create backup
pg_dump coderenew_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Deploy during maintenance window
# - Run migration
# - Restart services
# - Monitor logs

# 3. Smoke tests
curl https://api.coderenew.com/api/health/epss
# Check first scan with EPSS data
```

---

## 📈 Post-Deployment Monitoring (First 7 Days)

### Metrics to Track

1. **EPSS API Performance**
   - Response times (target: <500ms)
   - Error rate (target: <1%)
   - Cache hit rate (target: >90%)

2. **Database Performance**
   - Query times for EPSS-sorted results (target: <10ms)
   - Index usage
   - Storage growth

3. **Celery Tasks**
   - Task success rate (target: >95%)
   - Task duration (target: <60s for 100 CVEs)
   - Queue depth

4. **User Engagement**
   - % of users using EPSS sorting
   - EPSS badge click-through rate
   - Feature adoption

### Monitoring Queries

```sql
-- Check EPSS data coverage
SELECT
    COUNT(*) as total_results,
    COUNT(epss_score) as with_epss,
    ROUND(COUNT(epss_score)::numeric / COUNT(*) * 100, 2) as coverage_pct
FROM scan_results
WHERE created_at > NOW() - INTERVAL '7 days';

-- Top 10 highest EPSS scores
SELECT cve_id, epss_score, epss_percentile, description
FROM scan_results
WHERE epss_score IS NOT NULL
ORDER BY epss_score DESC
LIMIT 10;

-- EPSS data freshness
SELECT
    COUNT(*) FILTER (WHERE epss_updated_at > NOW() - INTERVAL '24 hours') as fresh,
    COUNT(*) FILTER (WHERE epss_updated_at <= NOW() - INTERVAL '24 hours') as stale
FROM scan_results
WHERE epss_score IS NOT NULL;
```

---

## 🔧 Recommended Improvements (Post-Launch)

### Phase 1: Performance Optimization (Week 2-3)

1. **Redis Cache Implementation**
   ```python
   import redis
   from app.core.config import settings

   class EPSSService:
       def __init__(self):
           self.redis = redis.from_url(settings.REDIS_URL)

       async def get_epss_score(self, cve: str):
           # Check Redis cache
           cached = self.redis.get(f"epss:{cve}")
           if cached:
               return EPSSData(**json.loads(cached))

           # Fetch from API
           score = await self._fetch_from_api([cve])

           # Store in Redis with 24h TTL
           self.redis.setex(f"epss:{cve}", 86400, json.dumps(score))

           return score
   ```

2. **Circuit Breaker Pattern**
   ```bash
   pip install circuitbreaker
   ```

   ```python
   from circuitbreaker import circuit

   @circuit(failure_threshold=5, recovery_timeout=60)
   async def _fetch_from_api(self, cves: List[str]):
       # Existing implementation
   ```

### Phase 2: Enhanced Features (Month 2)

1. **WordPress CVE Mapping Database**
   - Build database mapping WordPress plugins/themes to CVEs
   - Auto-extract CVEs without relying on description parsing

2. **EPSS Trend Tracking**
   - Store historical EPSS scores
   - Show trends (rising/falling)
   - Alert on significant changes

3. **Custom Risk Thresholds**
   - Allow users to set their own risk levels
   - Custom EPSS thresholds per organization

---

## ✅ Success Criteria

### Week 1
- [ ] All unit tests passing (>80% coverage)
- [ ] Migration deployed to staging
- [ ] Celery tasks running successfully
- [ ] No critical bugs reported

### Month 1
- [ ] 100% of new scans have EPSS data (where CVE available)
- [ ] Average API response time < 500ms
- [ ] Cache hit rate > 90%
- [ ] Zero data loss incidents

### Quarter 1
- [ ] 80% of users use EPSS sorting
- [ ] Feature mentioned in customer feedback
- [ ] Redis cache implemented
- [ ] CVE mapping database operational

---

## 📞 Support & Escalation

### Issue Severity Levels

**P0 - Critical (Respond: Immediate)**
- EPSS API completely down
- Database migration failed
- Data corruption

**P1 - High (Respond: <4 hours)**
- High error rate (>5%)
- Slow API response (>2s)
- Cache not working

**P2 - Medium (Respond: <24 hours)**
- Individual CVE lookup failures
- UI display issues
- Documentation errors

**P3 - Low (Respond: <1 week)**
- Feature requests
- UX improvements
- Performance optimization ideas

---

## 📝 Documentation Updates

Keep these docs updated:
- [ ] `EPSS_IMPLEMENTATION_SUMMARY.md` - Mark as deployed
- [ ] `backend/app/services/epss/README.md` - Add production notes
- [ ] `CHANGELOG.md` - Add EPSS feature entry
- [ ] User documentation - Add EPSS feature guide

---

**Next Review Date:** 2025-12-22 (1 month post-deployment)
**Owner:** Development Team
**Status:** Ready for Testing Phase ✅
