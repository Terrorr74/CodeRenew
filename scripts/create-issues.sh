#!/bin/bash

# GitHub Issue Creation Script
# Uses gh CLI to create all roadmap issues
#
# Prerequisites:
#   1. Install gh CLI: brew install gh
#   2. Authenticate: gh auth login
#   3. Run: bash scripts/create-issues.sh

set -e

OWNER="Terrorr74"
REPO="CodeRenew"

echo "🚀 Creating GitHub issues for CodeRenew 2025 Roadmap"
echo "=================================================="
echo ""

# Check if gh is authenticated
if ! gh auth status &>/dev/null; then
    echo "❌ Not authenticated with GitHub"
    echo "Please run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Function to create an issue
create_issue() {
    local title="$1"
    local body="$2"
    local labels="$3"

    echo "📝 Creating: $title"

    gh issue create \
        --repo "$OWNER/$REPO" \
        --title "$title" \
        --body "$body" \
        --label "$labels" \
        2>&1 || echo "  ⚠️  Failed to create issue"

    sleep 1  # Rate limiting
}

echo "=== Q1 2025 Issues ==="
echo ""

# Q1 Issue 1: EPSS Integration
create_issue \
    "[Q1] EPSS Integration" \
    "## Description
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
Weeks 1-2 of Q1 2025" \
    "enhancement,security,P0,size:S,Q1-2025"

# Q1 Issue 2: Webhooks
create_issue \
    "[Q1] Real-Time Webhook Notifications" \
    "## Description
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
Weeks 3-4 of Q1 2025" \
    "enhancement,backend,P0,size:M,Q1-2025"

# Q1 Issue 3: Rector POC
create_issue \
    "[Q1] Rector Integration (Proof of Concept)" \
    "## Description
Integrate Rector PHP for automated code refactoring and modernization. Start with basic refactorings as POC.

## Acceptance Criteria
- [ ] Install and configure Rector as subprocess
- [ ] Create security sandbox for Rector execution
- [ ] Implement basic refactoring rules (deprecated functions, type hints)
- [ ] Build backend/app/services/refactoring/rector_service.py
- [ ] Display before/after code diffs in UI
- [ ] Add \"Preview Refactoring\" functionality
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
- Performance with large codebases" \
    "enhancement,refactoring,backend,P0,size:L,Q1-2025"

# Q1 Issue 4: API v1
create_issue \
    "[Q1] API v1 Launch" \
    "## Description
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
Weeks 9-12 of Q1 2025" \
    "enhancement,api,backend,P1,size:M,Q1-2025"

echo ""
echo "=== Q2 2025 Issues ==="
echo ""

# Q2 Issue 5: Rector Full
create_issue \
    "[Q2] Rector Full Production Integration" \
    "## Description
Expand Rector POC to production-ready automated refactoring with git integration and safety checks.

## Acceptance Criteria
- [ ] Expand refactoring rules library (50+ rules)
- [ ] One-click \"Apply Fix\" with git commit integration
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
- **Requires:** [Q1] Rector Integration (POC)

## Timeline
Weeks 13-16 of Q2 2025" \
    "enhancement,refactoring,backend,P1,size:L,Q2-2025"

# Q2 Issue 6: Multi-site Dashboard
create_issue \
    "[Q2] Agency Multi-Site Dashboard" \
    "## Description
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
Weeks 17-20 of Q2 2025" \
    "enhancement,frontend,agency,P1,size:XL,Q2-2025"

# Q2 Issue 7: White-label Reports
create_issue \
    "[Q2] White-Label Reporting System" \
    "## Description
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
Weeks 21-24 of Q2 2025" \
    "enhancement,frontend,agency,P1,size:M,Q2-2025"

echo ""
echo "=== Q3 2025 Issues ==="
echo ""

# Q3 Issue 8: AI Fixes
create_issue \
    "[Q3] AI-Powered Fix Suggestions" \
    "## Description
LLM-generated fix explanations and code suggestions using Context7/Perplexity MCP.

## Acceptance Criteria
- [ ] Integrate mcp-tools framework (Context7 + Perplexity clients)
- [ ] For each vulnerability, generate fix suggestion
- [ ] Display \"Suggested Fix\" with code diff
- [ ] Human-in-loop approval required
- [ ] Learn from accepted/rejected suggestions
- [ ] Add \"Explain this vulnerability\" feature

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
Weeks 25-28 of Q3 2025" \
    "enhancement,ai,backend,P2,size:M,Q3-2025"

# Q3 Issue 9: CI/CD
create_issue \
    "[Q3] CI/CD Pipeline Integration" \
    "## Description
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
- **Requires:** [Q1] API v1 Launch

## Timeline
Weeks 29-32 of Q3 2025" \
    "enhancement,api,devops,P2,size:M,Q3-2025"

# Q3 Issue 10: Compliance
create_issue \
    "[Q3] Custom Compliance Rules Engine" \
    "## Description
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
Weeks 33-36 of Q3 2025" \
    "enhancement,enterprise,backend,frontend,P2,size:L,Q3-2025"

echo ""
echo "=== Q4 2025 Issues ==="
echo ""

# Q4 Issue 11: GraphQL
create_issue \
    "[Q4] GraphQL API v2" \
    "## Description
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
- **Requires:** [Q1] API v1 Launch

## Timeline
Weeks 37-40 of Q4 2025" \
    "enhancement,api,backend,enterprise,P3,size:L,Q4-2025"

# Q4 Issue 12: SSO
create_issue \
    "[Q4] SSO/SAML Authentication" \
    "## Description
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
Weeks 41-44 of Q4 2025" \
    "enhancement,security,backend,enterprise,P3,size:XL,Q4-2025"

# Q4 Issue 13: Performance
create_issue \
    "[Q4] Performance Optimization at Scale" \
    "## Description
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
Weeks 45-48 of Q4 2025" \
    "enhancement,performance,backend,devops,enterprise,P3,size:XL,Q4-2025"

echo ""
echo "=================================================="
echo "✅ All 13 issues created successfully!"
echo ""
echo "View at: https://github.com/$OWNER/$REPO/issues"
echo ""
