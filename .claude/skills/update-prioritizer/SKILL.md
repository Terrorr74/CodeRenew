---
name: update-prioritizer
description: Helps WordPress agencies prioritize updates and fixes across multiple client sites based on severity, effort, and business impact
---

# Update Prioritizer

You help WordPress agencies make data-driven decisions about which sites and issues to address first when managing multiple client sites.

## Prioritization Matrix

### Priority Score Formula
```
Priority = (Severity × 0.4) + (Business Impact × 0.3) + (Effort Inverse × 0.2) + (Age × 0.1)
```

Where:
- **Severity**: 1-100 from scan results
- **Business Impact**: Site traffic, revenue, client tier
- **Effort Inverse**: 100 - estimated hours × 10 (quick wins score higher)
- **Age**: Days since issue detected (older = higher priority)

## Tier Classification

### Tier 1: Emergency (This Week)
- Critical security vulnerabilities
- Sites actively broken
- High-traffic client sites with severe issues
- Compliance/legal requirements

### Tier 2: Urgent (Within 2 Weeks)
- High severity deprecations
- Upcoming PHP/WP version deadlines
- Premium client sites
- Issues blocking other updates

### Tier 3: Planned (Within 1 Month)
- Medium severity issues
- Standard client sites
- Accumulated technical debt
- Performance optimizations

### Tier 4: Backlog (Quarterly)
- Low severity issues
- Code quality improvements
- Future-proofing
- Nice-to-have updates

## Input Format

Provide scan summaries in this format:
```json
{
  "sites": [
    {
      "name": "Client Site Name",
      "url": "https://example.com",
      "client_tier": "premium|standard|basic",
      "monthly_traffic": 50000,
      "revenue_impact": "high|medium|low",
      "issues": [
        {
          "id": "issue-123",
          "severity": 85,
          "category": "deprecated_function",
          "description": "get_currentuserinfo() usage",
          "occurrences": 12,
          "estimated_hours": 2
        }
      ],
      "wp_version": "6.4",
      "php_version": "8.1",
      "last_updated": "2024-01-15"
    }
  ]
}
```

## Output Format

### Executive Summary
```markdown
## Portfolio Health Overview

**Total Sites:** {count}
**Critical Issues:** {count} across {site_count} sites
**Estimated Total Effort:** {hours} hours

### Immediate Action Required
1. {site_name}: {critical_issue} - {hours}h
2. {site_name}: {critical_issue} - {hours}h

### This Week's Priorities
{prioritized_list}
```

### Detailed Recommendations
```markdown
## Prioritized Update Plan

### Phase 1: Critical (Week 1)
| Site | Issue | Severity | Effort | ROI |
|------|-------|----------|--------|-----|
| {site} | {issue} | {score} | {hours}h | {roi} |

### Phase 2: High Priority (Week 2-3)
{table}

### Phase 3: Standard (Month 1)
{table}

### Deferred Items
{table_with_reasoning}
```

## Batch Optimization

When multiple sites have similar issues:
1. Group by issue type
2. Develop fix once, apply to many
3. Calculate batch efficiency gains
4. Suggest update sequence to minimize testing

Example:
```markdown
### Batch Opportunity: get_currentuserinfo() Deprecation

**Affected Sites:** 8
**Individual Effort:** 2h × 8 = 16h
**Batched Effort:** 4h (develop + deploy)
**Savings:** 12 hours (75%)

**Recommended Order:**
1. staging.client1.com (test environment)
2. client2.com (lowest traffic)
3. client3.com, client4.com (similar configs)
4. premium-client.com (highest stakes, last)
```

## Risk Assessment

For each recommendation, include:
- **Rollback complexity**: Easy/Medium/Hard
- **Testing requirements**: Smoke test/Full QA/UAT
- **Downtime expected**: None/Minutes/Hours
- **Dependencies**: Other updates required first
