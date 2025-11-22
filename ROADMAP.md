# CodeRenew Product Roadmap 2025

**Vision**: The only all-in-one WordPress modernization platform combining security scanning, automated refactoring, and deployment integration.

**Strategy**: Move from detection-only to detection + fix, targeting WordPress agencies and enterprises.

---

## Q1 2025: Foundation & Quick Wins (Weeks 1-12)

**Goal**: Achieve market-competitive baseline with high-impact features

### Week 1-2: EPSS Integration ⚡
- **Feature**: Exploit Prediction Scoring System for vulnerability prioritization
- **Why**: Reduces alert fatigue, shows which CVEs are actively exploited
- **Implementation**:
  - Integrate EPSS API (https://api.first.org/data/v1/epss)
  - Add EPSS score column to scan results
  - Sort vulnerabilities by exploitation probability
- **Effort**: Low (external API integration)
- **Impact**: High (competitive parity with Aikido, Detectify)

### Week 3-4: Real-Time Webhook Notifications 🔔
- **Feature**: Instant alerts via Slack, Discord, email, custom HTTP
- **Why**: Critical for agencies managing client sites
- **Implementation**:
  - Build webhook delivery system using existing Celery tasks
  - Create webhook config UI in dashboard
  - Add webhook templates for common platforms
- **Effort**: Medium (Celery infrastructure already exists)
- **Impact**: High (premium feature, revenue driver)

### Week 5-8: Rector Integration (POC) 🛠️
- **Feature**: Automated PHP code refactoring and modernization
- **Why**: No competitor offers this - major differentiator
- **Implementation**:
  - Install Rector as subprocess (PHP 5.3 → 8.4 upgrades)
  - Create backend/app/services/refactoring/rector_service.py
  - Basic refactorings: deprecated functions, type hints
  - UI: Show before/after code diffs
- **Effort**: High (subprocess integration, security sandbox)
- **Impact**: Very High (unique market position)

### Week 9-12: API v1 Launch 🚀
- **Feature**: RESTful API for CI/CD integration
- **Why**: WPScan charges premium for API access
- **Implementation**:
  - FastAPI endpoints: /api/v1/scans, /api/v1/reports
  - API key authentication
  - Rate limiting (25/day free, unlimited paid)
  - OpenAPI documentation
- **Effort**: Medium (FastAPI routes)
- **Impact**: High (enables automation, new revenue stream)

**Q1 Deliverables**:
- ✅ EPSS vulnerability scoring
- ✅ Webhook notifications (Slack, Discord, email)
- ✅ Rector POC with basic refactorings
- ✅ API v1 with authentication

**Q1 Revenue Target**: $0 (Beta launch, 10 free users)

---

## Q2 2025: Differentiation Phase (Weeks 13-24)

**Goal**: Build features no competitor has, acquire first paying customers

### Week 13-16: Rector Full Integration 🎯
- **Feature**: Production-ready automated refactoring
- **Implementation**:
  - Expand refactoring rules library
  - One-click "Apply Fix" with git integration
  - Refactoring history and rollback
  - Safety checks (run tests before/after)
- **Effort**: High
- **Impact**: Very High (market differentiation)

### Week 17-20: Agency Multi-Site Dashboard 📊
- **Feature**: Manage scans across 100+ client sites
- **Why**: Gap in market - most tools are single-site
- **Implementation**:
  - Multi-tenant architecture enhancement
  - Bulk scanning interface
  - Client grouping and filtering
  - Aggregate vulnerability reports
  - Client portal (read-only access for end clients)
- **Effort**: High (significant frontend work)
- **Impact**: Very High (targets agency segment)

### Week 21-24: White-Label Reporting 📄
- **Feature**: Branded PDF/HTML reports for agencies
- **Implementation**:
  - Custom logo, colors, branding upload
  - PDF generation service (WeasyPrint/Playwright)
  - Report templates (executive, technical, compliance)
  - Scheduled report delivery
- **Effort**: Medium
- **Impact**: High (agency must-have)

**Q2 Deliverables**:
- ✅ Production Rector integration
- ✅ Agency multi-site dashboard
- ✅ White-label reporting system
- ✅ First Pro tier launch

**Q2 Revenue Target**:
- 5 Pro users @ $299/year = **$1,495 ARR**
- 2 Beta agency partners (free, for feedback)

---

## Q3 2025: AI & Automation (Weeks 25-36)

**Goal**: Leverage AI for intelligent automation, expand to deployment workflows

### Week 25-28: AI-Powered Fix Suggestions 🤖
- **Feature**: LLM-generated fix explanations and code suggestions
- **Implementation**:
  - Use mcp-tools framework (Context7 + Perplexity)
  - For each vulnerability: "Here's the modern alternative + code diff"
  - Human-in-loop approval required
  - Learn from accepted/rejected suggestions
- **Effort**: Medium (mcp-tools client already built)
- **Impact**: Very High (cutting-edge feature)

### Week 29-32: CI/CD Pipeline Integration 🔄
- **Feature**: Automated scanning in deployment workflows
- **Implementation**:
  - GitHub Actions integration
  - GitLab CI templates
  - Pre-commit hooks
  - Block deployments on critical vulnerabilities
  - Auto-create PRs with Rector fixes
- **Effort**: Medium
- **Impact**: High (DevOps adoption)

### Week 33-36: Custom Compliance Rules Engine ⚖️
- **Feature**: GDPR, WCAG, PCI-DSS compliance checking
- **Implementation**:
  - Rule builder UI (if X then flag Y)
  - Pre-built compliance packs
  - Custom rule creation for enterprises
  - Compliance report generation
- **Effort**: High (flexible rule engine required)
- **Impact**: High (enterprise selling point)

**Q3 Deliverables**:
- ✅ AI fix suggestions with Context7/Perplexity
- ✅ GitHub Actions + GitLab CI integration
- ✅ Compliance rules engine
- ✅ Agency tier launch

**Q3 Revenue Target**:
- 20 Pro users @ $299 = **$5,980 ARR**
- 3 Agency customers @ $699 = **$2,097 ARR**
- **Total: $8,077 ARR**

---

## Q4 2025: Scale & Enterprise (Weeks 37-48)

**Goal**: Enterprise-ready platform, scale to 1000+ sites

### Week 37-40: Advanced API v2 (GraphQL) 🌐
- **Feature**: Flexible querying, real-time subscriptions
- **Implementation**:
  - GraphQL endpoint with Strawberry
  - Subscriptions for real-time scan updates
  - Batch operations
  - Enhanced rate limiting and quotas
- **Effort**: High
- **Impact**: Medium (enterprise feature)

### Week 41-44: SSO/SAML for Enterprise 🔐
- **Feature**: Single Sign-On with corporate identity providers
- **Implementation**:
  - SAML 2.0 integration (Okta, Azure AD)
  - Team/role management
  - Audit logging
  - IP allowlisting
- **Effort**: High (security critical)
- **Impact**: Very High (enterprise blocker removed)

### Week 45-48: Performance Optimization at Scale ⚡
- **Feature**: Handle 1000+ concurrent site scans
- **Implementation**:
  - Database query optimization
  - Redis caching layer
  - Horizontal scaling (Kubernetes)
  - Queue prioritization
  - Background job optimization
- **Effort**: High
- **Impact**: Very High (scalability requirement)

**Q4 Deliverables**:
- ✅ GraphQL API v2
- ✅ SSO/SAML authentication
- ✅ Kubernetes deployment
- ✅ Enterprise tier launch
- ✅ 1000+ site capacity

**Q4 Revenue Target**:
- 50 Pro users @ $299 = **$14,950 ARR**
- 10 Agency customers @ $699 = **$6,990 ARR**
- 1 Enterprise deal @ $15,000 = **$15,000 ARR**
- **Total: $36,940 ARR**

---

## 2025 Summary

### Annual Revenue Target: **$37,000+ ARR**

### Customer Acquisition:
- **60 Pro users** (self-serve)
- **13 Agency customers** (sales-assisted)
- **1 Enterprise customer** (direct sales)

### Key Differentiators by End of 2025:
1. ✅ Only platform with automated Rector refactoring
2. ✅ AI-powered fix suggestions (Context7/Perplexity integration)
3. ✅ Agency-focused multi-site management
4. ✅ CI/CD native integration
5. ✅ Compliance rules engine

---

## Technical Dependencies

### Infrastructure Ready:
- ✅ FastAPI backend
- ✅ Celery for async tasks
- ✅ Email service
- ✅ Docker + Docker Compose
- ✅ Next.js 16 frontend
- ✅ MCP tools framework (zero-context AI)

### To Build:
- Rector subprocess integration
- Webhook delivery system
- Multi-tenant dashboard
- GraphQL layer
- SSO/SAML

### External Integrations:
- EPSS API (free)
- Rector PHP (open source)
- Context7 MCP (free/paid)
- Perplexity MCP (API key required)
- GitHub/GitLab APIs (OAuth)

---

## Risk Mitigation

### Q1 Risk: Rector Integration Complexity
**Mitigation**: Start with basic refactorings (deprecated functions), expand gradually. Create security sandbox.

### Q2 Risk: Agency Adoption
**Mitigation**: Partner with 2-3 WordPress agencies early for feedback. Offer free Beta tier.

### Q3 Risk: AI Fix Accuracy
**Mitigation**: Human-in-loop approval for all auto-fixes. Learn from user feedback.

### Q4 Risk: Scale Performance
**Mitigation**: Start load testing in Q3. Horizontal scaling architecture from day 1.

---

## Competitive Positioning

| Feature | CodeRenew | WPScan | Wordfence | Aikido | Rector |
|---------|-----------|--------|-----------|--------|--------|
| Vulnerability Scanning | ✅ | ✅ | ✅ | ✅ | ❌ |
| EPSS Scoring | ✅ Q1 | ✅ | ❌ | ✅ | ❌ |
| Webhooks | ✅ Q1 | ✅ (paid) | ❌ | ✅ | ❌ |
| Auto Refactoring | ✅ Q1 | ❌ | ❌ | ❌ | ✅ |
| AI Fix Suggestions | ✅ Q3 | ❌ | ❌ | ❌ | ❌ |
| Multi-Site Agency | ✅ Q2 | ❌ | ❌ | ❌ | ❌ |
| CI/CD Integration | ✅ Q3 | Partial | ❌ | ✅ | Manual |
| Compliance Rules | ✅ Q3 | ❌ | ❌ | ✅ | ❌ |

**Result**: By Q4 2025, CodeRenew is the only platform offering **scanning + refactoring + AI + agency management** in one product.

---

## Team Requirements

**Recommended Team (2-3 developers)**:
- 1 Backend (Python/FastAPI, Rector integration)
- 1 Frontend (React/Next.js, dashboard)
- 0.5-1 DevOps (Docker, Kubernetes, CI/CD)

**Can execute roadmap with current infrastructure + MCP tools framework for AI features.**

---

*Roadmap created with Sequential Thinking MCP analysis*
*Last updated: 2025-11-22*
