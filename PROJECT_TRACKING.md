# CodeRenew Project Tracking Setup

This document contains all GitHub issues to create for the 2025 roadmap.

**How to use:**
1. Option A: Run `gh auth login` then `node scripts/setup-github-tracking.js`
2. Option B: Manually create issues from the templates below
3. Option C: Use GitHub's bulk issue import (see instructions at end)

---

## Labels to Create First

Create these labels in GitHub Settings → Labels:

| Label | Color | Description |
|-------|-------|-------------|
| `Q1-2025` | `#0E8A16` | Q1 2025 (Weeks 1-12) |
| `Q2-2025` | `#1D76DB` | Q2 2025 (Weeks 13-24) |
| `Q3-2025` | `#5319E7` | Q3 2025 (Weeks 25-36) |
| `Q4-2025` | `#D93F0B` | Q4 2025 (Weeks 37-48) |
| `P0` | `#B60205` | Critical Priority |
| `P1` | `#D93F0B` | High Priority |
| `P2` | `#FBCA04` | Medium Priority |
| `P3` | `#0E8A16` | Low Priority |
| `size:XS` | `#C2E0C6` | 1-2 days |
| `size:S` | `#BFDADC` | 3-5 days |
| `size:M` | `#BFD4F2` | 1-2 weeks |
| `size:L` | `#D4C5F9` | 3-4 weeks |
| `size:XL` | `#F9C5D5` | 1-2 months |
| `enhancement` | `#A2EEEF` | New feature |
| `security` | `#EE0701` | Security related |
| `refactoring` | `#006B75` | Code refactoring |
| `api` | `#0366D6` | API related |
| `frontend` | `#FBCA04` | Frontend work |
| `backend` | `#5319E7` | Backend work |
| `agency` | `#1D76DB` | Agency features |
| `enterprise` | `#D93F0B` | Enterprise features |
| `devops` | `#0E8A16` | DevOps/Infrastructure |
| `ai` | `#E99695` | AI/ML features |

---

# Q1 2025 Issues (Weeks 1-12)

## Issue 1: [Q1] EPSS Integration

**Title:** `[Q1] EPSS Integration`

**Labels:** `enhancement`, `security`, `P0`, `size:S`, `Q1-2025`

**Body:**
```markdown
## Description
Integrate Exploit Prediction Scoring System (EPSS) to prioritize vulnerabilities by exploitation probability.

## Acceptance Criteria
- [ ] Integrate EPSS API (https://api.first.org/data/v1/epss)
- [ ] Add EPSS score column to scan results table
- [ ] Sort vulnerabilities by EPSS score (highest risk first)
- [ ] Display EPSS score in vulnerability details
- [ ] Cache EPSS data (refresh daily)

## Technical Notes
- External API: https://api.first.org/data/v1/epss
- Add to backend/app/services/epss/
- Update database schema: add epss_score column
- Frontend: Update scan results component

## Effort
- Size: S (3-5 days)
- Priority: P0 (Critical path)

## Dependencies
None

## Timeline
Weeks 1-2 of Q1 2025

## References
- ROADMAP.md Q1 Section
- Competitive Analysis: Aikido, Detectify have this feature
```

---

## Issue 2: [Q1] Real-Time Webhook Notifications

**Title:** `[Q1] Real-Time Webhook Notifications`

**Labels:** `enhancement`, `backend`, `P0`, `size:M`, `Q1-2025`

**Body:**
```markdown
## Description
Enable real-time alerts via Slack, Discord, email, and custom HTTP webhooks when vulnerabilities are detected.

## Acceptance Criteria
- [ ] Create webhook configuration UI in dashboard
- [ ] Build webhook delivery service using Celery
- [ ] Support Slack webhook integration
- [ ] Support Discord webhook integration
- [ ] Support custom HTTP webhooks
- [ ] Add webhook testing interface
- [ ] Implement retry logic for failed deliveries
- [ ] Add webhook delivery logs

## Technical Notes
- Use existing Celery infrastructure (backend/app/tasks/)
- Create backend/app/services/webhooks/
- Webhook templates for Slack/Discord
- Store webhook configs in database (encrypted URLs)

## Effort
- Size: M (1-2 weeks)
- Priority: P0 (Critical path)

## Dependencies
None (Celery already set up)

## Timeline
Weeks 3-4 of Q1 2025

## References
- backend/app/core/celery_app.py (existing)
- backend/app/tasks/ (existing)
```

---

## Issue 3: [Q1] Rector Integration (Proof of Concept)

**Title:** `[Q1] Rector Integration (Proof of Concept)`

**Labels:** `enhancement`, `refactoring`, `backend`, `P0`, `size:L`, `Q1-2025`

**Body:**
```markdown
## Description
Integrate Rector PHP for automated code refactoring and modernization. Start with basic refactorings as POC.

## Acceptance Criteria
- [ ] Install and configure Rector as subprocess
- [ ] Create security sandbox for Rector execution
- [ ] Implement basic refactoring rules (deprecated functions, type hints)
- [ ] Build backend/app/services/refactoring/rector_service.py
- [ ] Display before/after code diffs in UI
- [ ] Add "Preview Refactoring" functionality
- [ ] Handle PHP version compatibility (5.3 → 8.4)

## Technical Notes
- Rector installation: https://getrector.com
- Run as subprocess with timeout
- Security: Sandbox execution (Docker container?)
- Store refactoring history
- Frontend: Code diff viewer component

## Effort
- Size: L (3-4 weeks)
- Priority: P0 (Critical differentiator)

## Dependencies
None

## Timeline
Weeks 5-8 of Q1 2025

## Risks
- Rector integration complexity
- Security sandbox requirements
- Performance with large codebases

## References
- ROADMAP.md: Rector is key differentiator
- Competitive analysis: No competitor offers this
```

---

## Issue 4: [Q1] API v1 Launch

**Title:** `[Q1] API v1 Launch`

**Labels:** `enhancement`, `api`, `backend`, `P1`, `size:M`, `Q1-2025`

**Body:**
```markdown
## Description
RESTful API for programmatic access to scans, enabling CI/CD integration.

## Acceptance Criteria
- [ ] Create FastAPI endpoints: /api/v1/scans, /api/v1/reports, /api/v1/sites
- [ ] Implement API key authentication
- [ ] Add rate limiting (25/day free tier, unlimited paid)
- [ ] Generate OpenAPI/Swagger documentation
- [ ] Add API key management UI
- [ ] Implement API usage analytics
- [ ] Create example integration scripts

## Technical Notes
- FastAPI routes in backend/app/api/v1/
- API key storage in database (hashed)
- Rate limiting with Redis
- OpenAPI auto-generation
- API documentation at /api/docs

## Effort
- Size: M (1-2 weeks)
- Priority: P1

## Dependencies
None

## Timeline
Weeks 9-12 of Q1 2025

## References
- WPScan API model: Free (25/day), Paid (unlimited)
```

---

# Q2 2025 Issues (Weeks 13-24)

## Issue 5: [Q2] Rector Full Production Integration

**Title:** `[Q2] Rector Full Production Integration`

**Labels:** `enhancement`, `refactoring`, `backend`, `P1`, `size:L`, `Q2-2025`

**Body:**
```markdown
## Description
Expand Rector POC to production-ready automated refactoring with git integration and safety checks.

## Acceptance Criteria
- [ ] Expand refactoring rules library (50+ rules)
- [ ] One-click "Apply Fix" with git commit integration
- [ ] Refactoring history and rollback functionality
- [ ] Run tests before/after refactoring (safety checks)
- [ ] Batch refactoring across multiple files
- [ ] Refactoring impact analysis
- [ ] Performance optimization for large codebases

## Technical Notes
- Build on Q1 Rector POC
- Git integration for automatic commits
- Test runner integration (PHPUnit, Codeception)
- Progress tracking for long-running refactorings

## Effort
- Size: L (3-4 weeks)
- Priority: P1

## Dependencies
- **Requires:** Issue #3 - [Q1] Rector Integration (POC)

## Timeline
Weeks 13-16 of Q2 2025
```

---

## Issue 6: [Q2] Agency Multi-Site Dashboard

**Title:** `[Q2] Agency Multi-Site Dashboard`

**Labels:** `enhancement`, `frontend`, `agency`, `P1`, `size:XL`, `Q2-2025`

**Body:**
```markdown
## Description
Multi-tenant dashboard for agencies to manage scans across 100+ client sites.

## Acceptance Criteria
- [ ] Multi-tenant architecture enhancement
- [ ] Bulk scanning interface (select multiple sites)
- [ ] Client grouping and filtering
- [ ] Aggregate vulnerability reports across sites
- [ ] Client portal (read-only access for end clients)
- [ ] Site comparison view
- [ ] Export bulk reports (CSV, JSON)

## Technical Notes
- Frontend: New React components in frontend/src/components/agency/
- Backend: Multi-tenant queries, permissions
- Database: Add site_group table
- Performance: Pagination for 100+ sites

## Effort
- Size: XL (1-2 months)
- Priority: P1

## Dependencies
None

## Timeline
Weeks 17-20 of Q2 2025

## Market Opportunity
- Gap in market - most tools are single-site focused
- Primary target: WordPress agencies with 50-200 clients
```

---

## Issue 7: [Q2] White-Label Reporting System

**Title:** `[Q2] White-Label Reporting System`

**Labels:** `enhancement`, `frontend`, `agency`, `P1`, `size:M`, `Q2-2025`

**Body:**
```markdown
## Description
Branded PDF/HTML reports for agencies to share with their clients.

## Acceptance Criteria
- [ ] Custom logo, colors, branding upload
- [ ] PDF generation service (WeasyPrint or Playwright)
- [ ] Report templates: Executive, Technical, Compliance
- [ ] Scheduled report delivery (daily, weekly, monthly)
- [ ] Email report distribution
- [ ] Report history and versioning

## Technical Notes
- PDF generation: WeasyPrint (Python) or Playwright (Node)
- Store branding in database (agency settings)
- Report templates in backend/app/templates/reports/
- Celery task for scheduled delivery

## Effort
- Size: M (1-2 weeks)
- Priority: P1

## Dependencies
None

## Timeline
Weeks 21-24 of Q2 2025
```

---

# Q3 2025 Issues (Weeks 25-36)

## Issue 8: [Q3] AI-Powered Fix Suggestions

**Title:** `[Q3] AI-Powered Fix Suggestions`

**Labels:** `enhancement`, `ai`, `backend`, `P2`, `size:M`, `Q3-2025`

**Body:**
```markdown
## Description
LLM-generated fix explanations and code suggestions using Context7/Perplexity MCP.

## Acceptance Criteria
- [ ] Integrate mcp-tools framework (Context7 + Perplexity clients)
- [ ] For each vulnerability, generate fix suggestion
- [ ] Display "Suggested Fix" with code diff
- [ ] Human-in-loop approval required
- [ ] Learn from accepted/rejected suggestions
- [ ] Add "Explain this vulnerability" feature

## Technical Notes
- Use existing mcp-tools/client/mcp-client.ts
- Backend: backend/app/services/ai/fix_suggester.py
- Context7 for documentation lookup
- Perplexity for reasoning about fixes
- Store suggestions in database

## Effort
- Size: M (1-2 weeks)
- Priority: P2

## Dependencies
- **Requires:** mcp-tools framework (already built ✅)

## Timeline
Weeks 25-28 of Q3 2025

## Differentiation
- NO competitor has AI-powered fix suggestions
- Leverages zero-context MCP integration
```

---

## Issue 9: [Q3] CI/CD Pipeline Integration

**Title:** `[Q3] CI/CD Pipeline Integration`

**Labels:** `enhancement`, `api`, `devops`, `P2`, `size:M`, `Q3-2025`

**Body:**
```markdown
## Description
Automated scanning in deployment workflows (GitHub Actions, GitLab CI).

## Acceptance Criteria
- [ ] GitHub Actions workflow templates
- [ ] GitLab CI templates
- [ ] Pre-commit hook generation
- [ ] Block deployments on critical vulnerabilities
- [ ] Auto-create PRs with Rector fixes
- [ ] Integration documentation and examples

## Technical Notes
- Create .github/workflows/ templates
- GitLab CI YAML templates
- API integration for pipeline status
- GitHub API for PR creation

## Effort
- Size: M (1-2 weeks)
- Priority: P2

## Dependencies
- **Requires:** Issue #4 - [Q1] API v1 Launch

## Timeline
Weeks 29-32 of Q3 2025
```

---

## Issue 10: [Q3] Custom Compliance Rules Engine

**Title:** `[Q3] Custom Compliance Rules Engine`

**Labels:** `enhancement`, `enterprise`, `backend`, `frontend`, `P2`, `size:L`, `Q3-2025`

**Body:**
```markdown
## Description
GDPR, WCAG, PCI-DSS compliance checking with custom rule builder.

## Acceptance Criteria
- [ ] Rule builder UI (if X then flag Y)
- [ ] Pre-built compliance packs (GDPR, WCAG, PCI-DSS)
- [ ] Custom rule creation for enterprises
- [ ] Rule testing interface
- [ ] Compliance report generation
- [ ] Rule sharing/import/export

## Technical Notes
- Backend: backend/app/services/compliance/
- Rule engine: Python expression evaluation (safely)
- Store rules in database (JSON format)
- Frontend: Drag-drop rule builder

## Effort
- Size: L (3-4 weeks)
- Priority: P2

## Dependencies
None

## Timeline
Weeks 33-36 of Q3 2025
```

---

# Q4 2025 Issues (Weeks 37-48)

## Issue 11: [Q4] GraphQL API v2

**Title:** `[Q4] GraphQL API v2`

**Labels:** `enhancement`, `api`, `backend`, `enterprise`, `P3`, `size:L`, `Q4-2025`

**Body:**
```markdown
## Description
Flexible querying with GraphQL and real-time subscriptions for enterprise clients.

## Acceptance Criteria
- [ ] GraphQL endpoint with Strawberry
- [ ] Real-time subscriptions for scan updates
- [ ] Batch operations
- [ ] Enhanced rate limiting and quotas
- [ ] GraphQL playground/documentation
- [ ] Migration guide from REST API v1

## Technical Notes
- Strawberry GraphQL for Python
- WebSocket support for subscriptions
- Backend: backend/app/api/graphql/
- Maintain REST API v1 for backwards compatibility

## Effort
- Size: L (3-4 weeks)
- Priority: P3

## Dependencies
- **Requires:** Issue #4 - [Q1] API v1 Launch

## Timeline
Weeks 37-40 of Q4 2025
```

---

## Issue 12: [Q4] SSO/SAML Authentication

**Title:** `[Q4] SSO/SAML Authentication`

**Labels:** `enhancement`, `security`, `backend`, `enterprise`, `P3`, `size:XL`, `Q4-2025`

**Body:**
```markdown
## Description
Single Sign-On with corporate identity providers for enterprise customers.

## Acceptance Criteria
- [ ] SAML 2.0 integration (Okta, Azure AD, Google Workspace)
- [ ] Team and role management
- [ ] Audit logging for all actions
- [ ] IP allowlisting
- [ ] Session management
- [ ] SSO configuration UI

## Technical Notes
- Python SAML library (python3-saml)
- Backend: backend/app/auth/saml/
- Store SAML configs per organization
- Security audit: penetration testing required

## Effort
- Size: XL (1-2 months)
- Priority: P3

## Dependencies
None

## Timeline
Weeks 41-44 of Q4 2025

## Enterprise Requirement
- Blocker for Fortune 500 companies
- Must pass security audit
```

---

## Issue 13: [Q4] Performance Optimization at Scale

**Title:** `[Q4] Performance Optimization at Scale`

**Labels:** `enhancement`, `performance`, `backend`, `devops`, `enterprise`, `P3`, `size:XL`, `Q4-2025`

**Body:**
```markdown
## Description
Handle 1000+ concurrent site scans with optimized infrastructure.

## Acceptance Criteria
- [ ] Database query optimization (add indexes, optimize queries)
- [ ] Redis caching layer
- [ ] Kubernetes deployment configuration
- [ ] Horizontal scaling (multiple workers)
- [ ] Queue prioritization (premium customers first)
- [ ] Background job optimization
- [ ] Load testing (1000+ concurrent scans)
- [ ] Performance monitoring dashboard

## Technical Notes
- Database: Add indexes, query profiling
- Redis for caching and queue management
- Kubernetes: deployment manifests
- Celery: Worker scaling configuration
- Load testing: Locust or k6

## Effort
- Size: XL (1-2 months)
- Priority: P3

## Dependencies
None

## Timeline
Weeks 45-48 of Q4 2025

## Success Metrics
- 1000+ concurrent scans
- < 5 min scan time for avg WordPress site
- 99.9% uptime
```

---

# Bulk Import Instructions

## Option 1: Use gh CLI (Recommended)

1. Authenticate:
```bash
gh auth login
```

2. Run the setup script:
```bash
node scripts/setup-github-tracking.js
```

## Option 2: Manual Creation

Copy each issue template above and create manually in GitHub Issues.

## Option 3: GitHub Projects Import

1. Go to https://github.com/Terrorr74/CodeRenew/issues
2. Click "New Issue" for each template above
3. Copy/paste title, body, and add labels

---

# Project Board Setup

Create a GitHub Project Board with columns:

| Column | Description |
|--------|-------------|
| 📋 Backlog | All unstarted issues |
| 🎯 Q1 2025 | In progress (Weeks 1-12) |
| 🚀 Q2 2025 | Planned (Weeks 13-24) |
| 🤖 Q3 2025 | Future (Weeks 25-36) |
| ⚡ Q4 2025 | Future (Weeks 37-48) |
| ✅ Done | Completed |

Filter by labels to view:
- Priority: P0, P1, P2, P3
- Size: XS, S, M, L, XL
- Type: enhancement, security, api, etc.

---

*Generated from ROADMAP.md using Sequential Thinking MCP*
*Total Issues: 13 (4 Q1, 3 Q2, 3 Q3, 3 Q4)*
