# EPSS Integration for CodeRenew

## Overview

This module integrates the **Exploit Prediction Scoring System (EPSS)** into CodeRenew to prioritize vulnerabilities by their actual exploitation probability, not just theoretical severity.

### What is EPSS?

EPSS is a data-driven model maintained by [FIRST.org](https://www.first.org/epss/) that predicts the probability that a vulnerability will be exploited in the wild within the next 30 days. It uses real-world exploit data, threat intelligence, and machine learning to provide scores from 0-1 (0% to 100% probability).

**Key Benefits:**
- Reduces alert fatigue by focusing on truly dangerous vulnerabilities
- Data-driven prioritization (not just CVSS scores)
- Updated daily with latest exploit intelligence
- Industry-standard risk metric used by major security vendors

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Scan Workflow                             │
│                                                               │
│  1. Detect Vulnerabilities                                   │
│  2. Extract CVE IDs → enrich_results_with_epss()            │
│  3. Save to Database with EPSS scores                        │
│  4. Display in Frontend (sorted by EPSS risk)               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   EPSS Service                               │
│                                                               │
│  - API Client (httpx)                                        │
│  - Batch CVE queries                                         │
│  - 24-hour cache (EPSS updates daily)                       │
│  - Retry logic with exponential backoff                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               FIRST.org EPSS API                            │
│                                                               │
│  GET https://api.first.org/data/v1/epss?cve=CVE-2021-44228 │
│                                                               │
│  Response:                                                   │
│  {                                                           │
│    "data": [{                                                │
│      "cve": "CVE-2021-44228",                               │
│      "epss": "0.944500000",    # 94.45% exploit prob        │
│      "percentile": "0.999890000" # Top 0.01% most exploited│
│    }]                                                        │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### ScanResult Model Additions

```python
class ScanResult:
    # ... existing fields ...

    # EPSS fields
    cve_id = Column(String, nullable=True, index=True)
    epss_score = Column(Float, nullable=True)           # 0-1 (exploit probability)
    epss_percentile = Column(Float, nullable=True)      # 0-1 (ranking among all CVEs)
    epss_updated_at = Column(DateTime, nullable=True)   # Last EPSS refresh
```

**Indexes for Performance:**
- `ix_scan_results_epss_score` - Sort by risk
- `ix_scan_results_scan_id_epss_score` - Filter high-risk vulnerabilities by scan
- `ix_scan_results_cve_id` - Lookup by CVE

## Usage

### 1. Basic Usage in Scan Workflow

```python
from app.services.epss.enrichment import enrich_results_with_epss, extract_cve_from_description

async def scan_wordpress_plugin(plugin_code: str) -> List[ScanResult]:
    results = []

    # Detect vulnerabilities
    for vulnerability in detect_vulnerabilities(plugin_code):
        result = ScanResult(
            issue_type=vulnerability.type,
            severity=vulnerability.severity,
            description=vulnerability.description,
            # Extract CVE from description
            cve_id=extract_cve_from_description(vulnerability.description)
        )
        results.append(result)

    # Enrich with EPSS scores
    await enrich_results_with_epss(results)

    # Results now have epss_score, epss_percentile populated
    return results
```

### 2. Background Enrichment (Async)

```python
from app.services.epss.enrichment import trigger_epss_enrichment_task

# After scan completes
scan_id = 123
task_id = trigger_epss_enrichment_task(scan_id)
# Task runs in background via Celery
```

### 3. Direct API Access

```python
from app.services.epss import get_epss_service

epss = get_epss_service()

# Single CVE
score = await epss.get_epss_score('CVE-2021-44228')
print(f"EPSS: {score.epss_score:.1%}, Percentile: {score.percentile:.1%}")

# Batch query (efficient)
scores = await epss.get_epss_scores(['CVE-2021-44228', 'CVE-2024-1234'])
for cve, data in scores.items():
    print(f"{cve}: {data.epss_score:.1%}")
```

## Celery Tasks

### Daily EPSS Refresh Task

```python
# Configure in backend/app/core/celery_app.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'refresh-epss-daily': {
        'task': 'app.tasks.epss_tasks.refresh_all_epss_scores_daily',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM UTC
    },
}
```

### Manual Refresh

```bash
# Refresh all stale EPSS scores (older than 24 hours)
celery -A app.core.celery_app call app.tasks.epss_tasks.refresh_stale_epss_scores

# Enrich specific scan
celery -A app.core.celery_app call app.tasks.epss_tasks.enrich_scan_results_with_epss --args='[123]'
```

## Frontend Display

### Risk Level Badges

EPSS scores are color-coded in the UI:

| EPSS Score | Risk Level    | Color         | Meaning                              |
|------------|---------------|---------------|--------------------------------------|
| ≥ 0.8      | Critical Risk | Red           | Top 20% most exploited               |
| 0.5 - 0.8  | High Risk     | Orange        | Moderate exploitation probability    |
| 0.2 - 0.5  | Medium Risk   | Yellow        | Low exploitation probability         |
| < 0.2      | Low Risk      | Green         | Very low exploitation probability    |

### Sort Options

Users can sort scan results by:
1. **Exploit Risk (EPSS)** - Default, shows highest-risk vulnerabilities first
2. **Severity** - Traditional severity-based sorting (Critical → High → Medium → Low)

## API Response Example

### GET /scans/{scan_id}

```json
{
  "id": 123,
  "status": "completed",
  "results": [
    {
      "id": 1,
      "severity": "high",
      "issue_type": "deprecated_function",
      "description": "Log4Shell vulnerability (CVE-2021-44228)",
      "cve_id": "CVE-2021-44228",
      "epss_score": 0.9445,
      "epss_percentile": 0.99989,
      "epss_updated_at": "2025-11-22T10:30:00Z"
    }
  ]
}
```

## Migration

### Run Database Migration

```bash
cd backend
alembic upgrade head
```

This creates the new EPSS columns and indexes.

### Backfill Existing Data

```python
# If you have existing scan results with CVE IDs
from app.tasks.epss_tasks import enrich_scan_results_with_epss

# Enrich each scan
for scan_id in [1, 2, 3, ...]:
    enrich_scan_results_with_epss.delay(scan_id)
```

## Testing

### Unit Tests

```python
import pytest
from app.services.epss import EPSSService

@pytest.mark.asyncio
async def test_epss_service():
    service = EPSSService()

    # Test single CVE
    score = await service.get_epss_score('CVE-2021-44228')
    assert score is not None
    assert 0 <= score.epss_score <= 1

    # Test batch query
    scores = await service.get_epss_scores(['CVE-2021-44228', 'CVE-2024-1234'])
    assert len(scores) > 0
```

### Manual Testing

```bash
# Test EPSS service directly
python -c "
import asyncio
from app.services.epss import get_epss_service

async def test():
    epss = get_epss_service()
    score = await epss.get_epss_score('CVE-2021-44228')
    print(f'EPSS: {score.epss_score:.1%}')

asyncio.run(test())
"
```

## Performance Considerations

### Caching Strategy

- **Cache TTL:** 24 hours (EPSS updates daily)
- **Cache Location:** In-memory (singleton service instance)
- **Refresh:** Automatic daily refresh via Celery beat

### API Rate Limiting

- FIRST.org EPSS API has no documented rate limits
- We implement retry logic with exponential backoff for reliability
- Batch queries reduce API calls (single request for multiple CVEs)

### Database Indexes

Three indexes added for query performance:
1. `epss_score` - Sort by risk
2. `scan_id, epss_score` - Composite index for filtered sorting
3. `cve_id` - Lookup efficiency

## Troubleshooting

### EPSS Score is NULL

**Possible causes:**
1. CVE ID not found in EPSS database (new CVE, not yet scored)
2. CVE ID extraction failed (check `extract_cve_from_description()`)
3. EPSS API temporarily unavailable (check logs)

**Solution:**
- Verify CVE ID format: `CVE-YYYY-NNNNN`
- Check EPSS API directly: `https://api.first.org/data/v1/epss?cve=CVE-YYYY-NNNNN`
- Re-run enrichment task if API was down

### Stale EPSS Scores

**Symptom:** `epss_updated_at` is older than 24 hours

**Solution:**
```bash
# Manually trigger refresh
celery -A app.core.celery_app call app.tasks.epss_tasks.refresh_stale_epss_scores
```

### Task Failures

**Check Celery logs:**
```bash
tail -f logs/celery.log
```

**Common issues:**
- Network connectivity to FIRST.org API
- Database connection issues
- Invalid CVE format

## References

- [EPSS Official Website](https://www.first.org/epss/)
- [EPSS API Documentation](https://www.first.org/epss/api)
- [EPSS Research Paper](https://www.first.org/epss/articles/prob_have_been_exploited.html)
- [NIST CVE Database](https://nvd.nist.gov/)

## Competitive Analysis

| Feature | CodeRenew | WPScan | Wordfence | Aikido | Detectify |
|---------|-----------|--------|-----------|--------|-----------|
| EPSS Scoring | ✅ | ❌ | ❌ | ✅ | ✅ |
| Daily Updates | ✅ | - | - | ✅ | ✅ |
| Sort by Risk | ✅ | ❌ | ❌ | ✅ | ✅ |

**Differentiation:** By adding EPSS integration, CodeRenew reaches competitive parity with enterprise security platforms like Aikido and Detectify, while surpassing WPScan and Wordfence.

---

**Implementation Date:** 2025-11-22
**Status:** ✅ Complete (Q1 2025 - Week 1-2)
**GitHub Issue:** #2 [Q1] EPSS Integration
