# CodeRenew - WordPress Agency Execution Plan

**Last Updated**: 2025-11-18
**Status**: Pre-Launch Planning - WordPress Niche Focus
**Target**: Build MVP for small WordPress agencies and validate product-market fit

---

## Executive Summary

CodeRenew is pivoting to a **laser-focused niche**: AI-powered WordPress compatibility scanning for small agencies. Instead of building a generic code modernization tool, we're solving ONE specific problem for ONE specific customer: helping WordPress agencies confidently update client sites without fear of breakage.

**Key Insight**: WordPress agencies (518M sites, 43% of all websites) spend 2-5 hours per site monthly on updates and live in constant fear of breaking client sites. No AI-powered solution exists that analyzes custom code for compatibility issues.

**Critical Path**: Validate Demand → Build MVP → Beta Launch → Growth
**Timeline**: 12 weeks to paying customers

---

## Target Customer

**Primary**: Small WordPress Agencies
- 2-10 employees
- Manage 10-30 client WordPress sites
- Spend 2-3 hours per site monthly on updates
- Main pain: Risk of breaking client sites during WordPress updates (9/10 pain level)
- Current spend: $30-$100/month per site on maintenance
- Time cost: $200/site/month in labor (2 hours × $100/hr)

**Customer Job-to-Be-Done**:
"Give me confidence that updating WordPress won't break my client's site"

**Why They'll Pay**:
- For 20 sites: Save 30 hours/month = $3,000 value
- One broken site costs $500+ in emergency fixes + client trust damage
- Our tool at $199/month = 15x ROI

---

## Product Vision

**What We Build**: AI-powered WordPress compatibility scanner

**Core Workflow**:
1. Agency uploads custom theme/plugin files (ZIP)
2. AI analyzes code for compatibility with target WordPress version
3. System returns risk assessment: SAFE / WARNING / CRITICAL
4. Report shows: what will break, where (file/line), why, how to fix
5. Agency updates WordPress with confidence (or fixes issues first)

**Key Differentiator**:
Existing tools (All-in-One Migration, UpdraftPlus) backup/restore sites but don't analyze custom code. We understand what will break BEFORE the update happens.

---

## Phase 0: Validation (Week 1-2)

**Goal**: Prove agencies will pay for this before building

### Feature 0.1: Landing Page & Waitlist
**Timeline**: 1 day
**Owner**: TBD

**Deliverables**:
- [ ] Landing page: "Know if WordPress updates will break your sites BEFORE you click update"
- [ ] Email capture form with question: "What's your biggest WordPress update fear?"
- [ ] Pricing signal: $79-$149/month range
- [ ] "Join beta waitlist" CTA
- [ ] Thank you page with discovery call booking link

**Success Criteria**:
- 50+ email signups in 2 weeks = PROCEED
- 10+ discovery calls scheduled = STRONG SIGNAL
- <20 signups = PIVOT OR KILL

**Outreach Channels**:
- WordPress agency Facebook groups
- Reddit r/wordpress, r/webdev
- Direct outreach to 20 agencies via LinkedIn
- WordPress.org forums

---

### Feature 0.2: Manual Compatibility Analysis (Design Partners)
**Timeline**: 1-2 weeks (ongoing with first 5 agencies)
**Owner**: TBD

**Process**:
1. Recruit 5 agencies willing to be design partners
2. Agency provides: theme files, plugin list, current WP version, target version
3. We manually analyze using Claude (within 24 hours)
4. Deliver PDF report: compatibility assessment, warnings, recommended fixes
5. Follow-up call: gather feedback, validate value proposition

**Learning Goals**:
- What output format do agencies want?
- What questions do they ask?
- Can Claude accurately detect compatibility issues?
- What would they pay for this?

**Success Criteria**:
- 5 agencies willing to share files = TRUST ESTABLISHED
- Correctly identify 3+ real issues per site = TECHNICAL VALIDATION
- Agencies say "I'd pay $X for this" = PRICING VALIDATION

---

### Decision Point: GO/NO-GO for MVP Development

**GO if**:
- 50+ waitlist signups
- 5+ design partners complete manual analysis
- 3+ agencies express willingness to pay $79+/month
- Claude accurately detects compatibility issues (95%+ accuracy)

**NO-GO if**:
- <20 waitlist signups
- Agencies say "I'd just do this manually"
- Claude gives too many false positives (trust erodes)

---

## Phase 1: MVP Development (Week 3-8)

**Goal**: Buildable, sellable product for 10 beta customers
**Philosophy**: ONE workflow that works perfectly beats five half-baked features

### P0-1: File Upload & Site Analysis
**Timeline**: Week 3-4 (2 weeks)
**Priority**: CRITICAL

**Features**:
- [ ] Drag-and-drop ZIP file upload (themes + plugins)
- [ ] Support multiple files in single batch (1 theme + up to 10 plugins)
- [ ] Upload progress indicator
- [ ] File validation and parsing (extract PHP files, readme.txt, metadata)
- [ ] Temporary storage (auto-delete after 24 hours for security)
- [ ] Maximum file size: 50MB total per analysis
- [ ] Clear error messages for invalid files

**Acceptance Criteria**:
- 90% of uploads successfully processed
- Analysis completes in <2 minutes for typical site
- User can upload in <60 seconds

**Tech Stack**:
- Backend: FastAPI
- File storage: Temporary local filesystem (not S3 for MVP)
- Security: Sandbox file processing, malware scanning, no code execution

---

### P0-2: AI Compatibility Analysis Engine
**Timeline**: Week 4-5 (1.5 weeks)
**Priority**: CRITICAL

**Features**:
- [ ] Integrate Anthropic SDK (Claude 3.5 Sonnet)
- [ ] WordPress version compatibility database (WP 5.0 → current)
- [ ] Analyze PHP code for deprecated functions/hooks
- [ ] Detect PHP version requirements
- [ ] Identify breaking changes (jQuery updates, Gutenberg conflicts)
- [ ] Return structured JSON: risk_level, issues[], recommendations[]
- [ ] Each issue includes: severity, description, file/line numbers, remediation
- [ ] Analysis completes in <90 seconds

**WordPress-Specific Checks**:
- Deprecated functions (wp-includes/deprecated.php reference)
- Hook changes (add_action/add_filter signature changes)
- Global variable changes
- Template hierarchy changes
- REST API breaking changes
- Gutenberg block compatibility

**Acceptance Criteria**:
- 95% accuracy on known compatibility issues
- <2% false positive rate
- Zero critical misses (issues that break sites)

**Cost Management**:
- Token optimization (only send relevant code sections)
- Per-scan budget limit: $0.50 max in Claude API costs
- Fallback if API slow/unavailable

---

### P0-3: Simple Compatibility Report
**Timeline**: Week 5-6 (1 week)
**Priority**: CRITICAL

**Features**:
- [ ] Overall risk score: SAFE (green) / CAUTION (yellow) / HIGH RISK (red)
- [ ] Executive summary: "X critical issues, Y warnings, Z info items"
- [ ] Issue list sorted by severity
- [ ] Each issue shows: What breaks, Where (file:line), Why, How to fix
- [ ] Recommended action section
- [ ] Downloadable PDF for client communication
- [ ] Shareable link (expires in 7 days)

**Report Sections**:
1. **Summary**: Overall risk, site name, WordPress version (current → target)
2. **Critical Issues**: Must fix before updating (site will break)
3. **Warnings**: May cause issues (test thoroughly)
4. **Informational**: Best practices, optimization opportunities
5. **Next Steps**: Recommended action plan

**Acceptance Criteria**:
- 80% of beta users say "I understood immediately"
- Users spend <3 minutes reading report before deciding
- Report generation in <5 seconds after analysis

---

### P0-4: Basic User Authentication
**Timeline**: Week 6 (2 days)
**Priority**: NEEDED

**Features**:
- [ ] Email/password registration
- [ ] Email verification required
- [ ] Password reset flow
- [ ] User dashboard: list of past scans with date, site name, risk level
- [ ] Re-download previous reports
- [ ] Sessions persist for 7 days
- [ ] Rate limiting: max 10 scans/day during beta

**Implementation**:
- Use Auth0 or Firebase Auth (battle-tested, not custom)
- Transactional emails via SendGrid/Postmark

**Acceptance Criteria**:
- <5% support requests about login
- 90% successful registration on first try

---

### P0-5: Site Management (Basic)
**Timeline**: Week 6-7 (2 days)
**Priority**: IMPORTANT

**Features**:
- [ ] Add site name during upload (e.g., "Acme Corp - Main Site")
- [ ] Edit site name after scan
- [ ] Dashboard groups scans by site
- [ ] Filter by site name or date
- [ ] Delete old scans
- [ ] Maximum 30 sites per user during beta

**Acceptance Criteria**:
- 80% of users create named sites (not "untitled scan")
- Average user tracks 5+ sites

---

### Phase 1 Deliverable Checklist

**Before Beta Launch**:
- [ ] All P0 features complete (5/5)
- [ ] Manual testing with 10+ real WordPress sites
- [ ] Error handling works for edge cases
- [ ] UI is clean and intuitive
- [ ] Documentation: "How to export theme/plugin files from WordPress"
- [ ] Video walkthrough (<2 minutes)
- [ ] Privacy policy and Terms of Service (basic)

---

## Phase 2: Beta Launch (Week 9-12)

**Goal**: Convert 10 beta users to paying customers through trust and polish

### P1-1: Confidence Indicators
**Timeline**: Week 9 (3 days)
**Priority**: CRITICAL FOR CONVERSION

**Features**:
- [ ] "Evidence" section for each issue (code snippets)
- [ ] Links to WordPress documentation for deprecated functions
- [ ] "Analysis methodology" page (how detection works)
- [ ] Show number of files analyzed and processing time
- [ ] Badge: "Based on WordPress X.X compatibility database"
- [ ] "Report incorrect finding" button on each issue

**Success Criteria**:
- 60% of users view evidence/methodology
- <5% of findings reported as incorrect
- Beta-to-paid conversion >40%

---

### P1-2: Update Recommendations Dashboard
**Timeline**: Week 9-10 (4 days)
**Priority**: IMPORTANT

**Features**:
- [ ] At-a-glance view: all sites with traffic-light status
- [ ] Shows WordPress version (current → target) per site
- [ ] Days since last scan
- [ ] "Safe to update now" section (green sites)
- [ ] "Needs attention" section (yellow/red sites)
- [ ] One-click re-scan for stale data
- [ ] Export to CSV for client reporting

**Success Criteria**:
- 70% of users return to dashboard weekly
- Users scan each site 2x/month average
- Report 30+ minutes saved per maintenance cycle

---

### P1-3: Team Collaboration (Basic)
**Timeline**: Week 10 (2 days)
**Priority**: IMPORTANT

**Features**:
- [ ] Invite up to 5 team members (beta limit)
- [ ] Team members can view all scans
- [ ] Team members can run new scans
- [ ] Simple permissions: Owner vs. Member (no complex roles)
- [ ] Team members cannot manage billing or delete sites

**Success Criteria**:
- 40% of paid accounts invite ≥1 team member
- Accounts with teams have 2x scan volume

---

### P1-4: Onboarding Flow
**Timeline**: Week 10-11 (3 days)
**Priority**: CRITICAL

**Features**:
- [ ] Post-signup: 3-step wizard (Upload → Analyze → Save site)
- [ ] Contextual tooltips on first upload
- [ ] Sample report available ("See example analysis")
- [ ] Video: "How to export theme/plugins" (<90 seconds)
- [ ] Email drip: Day 1 (welcome), Day 3 (reminder), Day 7 (success stories)
- [ ] Checklist: "Get started in 5 minutes"

**Success Criteria**:
- 70% of signups complete first scan within 24 hours
- <10% contact support during onboarding

---

### P1-5: Pricing & Billing
**Timeline**: Week 11-12 (1 week)
**Priority**: CRITICAL

**Pricing Tiers**:

| Tier | Sites | Scans/Month | Price | Target Customer |
|------|-------|-------------|-------|-----------------|
| **Free Trial** | 3 sites | 10 scans | $0 (14 days) | Evaluation |
| **Starter** | 15 sites | 50 scans | $79/month | Freelancers |
| **Growth** | 30 sites | 150 scans | $149/month | Small agencies ← PRIMARY |
| **Agency** | 75 sites | Unlimited | $299/month | Medium agencies |

**Features**:
- [ ] Stripe Checkout integration
- [ ] 14-day free trial (no credit card required)
- [ ] Clear pricing page with tier comparison
- [ ] Usage dashboard (X scans used this month)
- [ ] Email notification at 80% of scan limit
- [ ] Upgrade/downgrade flow
- [ ] Cancel anytime (prorated refund)

**Acceptance Criteria**:
- Trial-to-paid conversion >30%
- <5% payment failures
- <10% churn in first 3 months

---

### Phase 2 Success Criteria

**Metrics to Track**:
- 50+ beta signups
- 10+ active beta users (≥3 scans each)
- 40% trial-to-paid conversion
- 70% positive feedback ("Would you recommend?")
- <10% month-2 churn
- 5+ unprompted testimonials

**GO/NO-GO for Phase 3**:
- **GO**: 10+ paying customers, >30% conversion, <10% churn
- **PIVOT**: <20% conversion, agencies say "too expensive" or "too limited"
- **KILL**: <5 paying customers, high churn, negative feedback

---

## Phase 3: Growth (Month 4-6)

**Goal**: Scale to 50+ paying customers, $7,500+ MRR

### P2-1: Scheduled Scans & Email Alerts
**Timeline**: Month 4 (1 week)

**Features**:
- [ ] Email alert when new WordPress version released
- [ ] Monthly reminder: "Time to scan your sites"
- [ ] Dashboard shows: "WordPress X.X released 3 days ago - 8 sites not scanned"
- [ ] Opt-in notifications (not forced)

**Value**: Keeps product top-of-mind, drives engagement

---

### P2-2: White-Label Client Reports
**Timeline**: Month 4-5 (1 week)

**Features**:
- [ ] Upload agency logo (shown on PDF reports)
- [ ] Customize report header with agency branding
- [ ] "Send to client" button (client-friendly version)
- [ ] Track when client opens report (read receipt)

**Value**: Agencies show reports to clients → referrals ("What tool is that?")

---

### P2-3: Plugin Vulnerability Scanning
**Timeline**: Month 5 (1 week)

**Features**:
- [ ] Cross-reference plugin versions against WPScan vulnerability database
- [ ] Show critical/high/medium vulnerabilities in report
- [ ] Include CVE numbers and severity scores
- [ ] Alert if plugin abandoned (no updates in 2+ years)

**Value**: Adjacent problem to compatibility, high perceived value

---

### P2-4: Historical Tracking & Trends
**Timeline**: Month 5-6 (1 week)

**Features**:
- [ ] Site detail page: scan history timeline
- [ ] Graph: risk score over time
- [ ] "Trends" dashboard: portfolio health across all sites
- [ ] Compare scans side-by-side

**Value**: Demonstrates value to clients, encourages regular scanning

---

### P2-5: API Access (Premium Feature)
**Timeline**: Month 6 (1 week)

**Features**:
- [ ] REST API: upload files, trigger scan, get results
- [ ] API key management
- [ ] Webhook support
- [ ] API documentation with Python/PHP examples
- [ ] Available only on Agency tier ($299/month)

**Value**: Attracts larger agencies, builds moat (integration = sticky)

---

## Features Explicitly CUT

### ❌ WordPress Plugin (Direct Site Scanning)
**Why**: Adds 4-6 weeks to timeline, WordPress.org approval process, increased support complexity. File upload achieves same outcome with lower risk.
**Decision**: Revisit in Phase 4 after PMF proven

### ❌ Automatic Update Execution
**Why**: Liability nightmare, agencies don't trust automation for critical updates
**Decision**: Never build - out of scope

### ❌ Visual Regression Testing
**Why**: Requires headless browser infrastructure (expensive/complex), false positives
**Decision**: Partner with existing tools instead

### ❌ Multi-Site Bulk Operations
**Why**: Agencies scan when planning updates (not all at once), complex UX
**Decision**: Add in Phase 4 if demanded

### ❌ Mobile App
**Why**: Agencies work at desk, doubles development effort
**Decision**: Never build unless research shows need

---

## Success Metrics by Phase

### Phase 0 (Week 1-2): Validation
- [ ] 50+ waitlist signups
- [ ] 5+ design partner agencies
- [ ] 95%+ accuracy on manual scans
- [ ] Clear pricing validation ($79-$149/month)

### Phase 1 (Week 3-8): MVP
- [ ] MVP is functional and stable
- [ ] 10 beta testers complete onboarding
- [ ] 70%+ say "this solves my problem"

### Phase 2 (Week 9-12): Beta Launch
- [ ] 50+ beta signups
- [ ] 10+ paying customers
- [ ] 40%+ trial-to-paid conversion
- [ ] <10% churn in first 3 months
- [ ] 5+ testimonials

### Phase 3 (Month 4-6): Growth
- [ ] 50+ paying customers
- [ ] $7,500+ MRR
- [ ] 60+ NPS score
- [ ] 20%+ of new customers from referrals

---

## Risk Management

### RISK 1: AI Accuracy Insufficient
**Impact**: HIGH - Agencies won't trust tool if false positives/negatives
**Mitigation**:
- Start conservative (flag more than fewer)
- Cross-reference WordPress deprecation database
- Confidence scores on all findings
- "Report incorrect finding" feedback loop
- Manual review of first 50 scans

**Contingency**: If accuracy <90%, pause beta and improve prompts/detection logic

---

### RISK 2: File Export Too Complicated
**Impact**: MEDIUM - High abandonment if users can't figure out upload
**Mitigation**:
- Clear video tutorial (<90 seconds)
- Step-by-step screenshots in docs
- Offer to do it for them in onboarding call (first 10 customers)

**Contingency**: If >30% abandon at upload step, build WordPress plugin to automate export

---

### RISK 3: Pricing Too High
**Impact**: MEDIUM - Low conversion if perceived value < price
**Mitigation**:
- Emphasize ROI (save 30 hours/month = $3,000 value)
- Show cost of one broken site ($500+ emergency fix)
- Free trial (no credit card required)
- Money-back guarantee in first 30 days

**Contingency**: If conversion <20%, test $49/month tier or usage-based pricing

---

### RISK 4: WordPress Ecosystem Changes
**Impact**: LOW - WordPress could change deprecation policy
**Mitigation**:
- Monitor WordPress core development (Trac, GitHub)
- Subscribe to WordPress dev blog
- Participate in WordPress community

**Contingency**: Update compatibility database quarterly

---

## Resource Requirements

### Phase 0 (Week 1-2): Validation
- **Time**: 1 week full-time
- **Cost**: $0 (landing page + manual analysis)
- **Tools**: Static site hosting, email service

### Phase 1 (Week 3-8): MVP
- **Time**: 6 weeks full-time (1-2 developers)
- **Infrastructure**: $100/month (hosting, database)
- **Claude API**: $0 during development, ~$50/month in beta (10 users × 5 scans × $1/scan)
- **Total**: Mostly time investment

### Phase 2 (Week 9-12): Beta Launch
- **Time**: 4 weeks full-time
- **Infrastructure**: $150/month
- **Claude API**: $250/month (50 users × 5 scans × $1/scan)
- **Stripe fees**: ~3% of revenue
- **Legal**: $1,000 (Terms of Service, Privacy Policy)
- **Total**: ~$2,000

### Phase 3 (Month 4-6): Growth
- **Time**: 3 months full-time
- **Infrastructure**: $300/month
- **Claude API**: $1,000/month (100 users × 10 scans × $1/scan)
- **Marketing**: $2,000/month (content, ads, WordCamp)
- **Total**: ~$10,000

---

## Go-to-Market Strategy

### Month 1-2: Validation
- Build landing page
- Post in WordPress Facebook groups (20+ groups, 50K+ members)
- Direct outreach to 50 agencies via LinkedIn
- Manual analysis for first 5 design partners

### Month 3-4: MVP Development
- Build core features (file upload, AI analysis, reports)
- Weekly updates to waitlist (build anticipation)
- Recruit 10 beta testers from waitlist

### Month 5-6: Beta Launch
- Invite beta testers (10 agencies)
- Weekly feedback calls
- Iterate based on feedback
- Build case studies/testimonials

### Month 7-8: Public Launch
- Open signups (freemium model)
- Content marketing: "WordPress Update Checklist", "Top 10 Compatibility Issues"
- WordCamp sponsorships ($500-$1,000)
- Guest posts on WordPress blogs (WP Tavern, etc.)

### Month 9-12: Growth
- Referral program (give $20, get $20)
- Integration with MainWP, ManageWP
- SEO optimization ("wordpress update compatibility", "wordpress breaking changes")
- Customer success outreach (reduce churn)

---

## Next Steps (Immediate)

### This Week:
1. **Build landing page** (1 day)
2. **Launch waitlist campaign** (post in 10 WordPress groups)
3. **Reach out to 20 agencies** for discovery calls
4. **Recruit 3 design partners** for manual analysis

### Next Week:
1. **Conduct 5 design partner analyses** (manual Claude scans)
2. **Validate pricing** ($79-$149/month sweet spot)
3. **Make GO/NO-GO decision** based on waitlist + feedback

### Week 3+ (if GO):
1. **Start MVP development** (Week 3-8)
2. **Weekly check-ins** with design partners
3. **Iterate based on feedback**

---

## Decision Points

### Before Starting Phase 0:
- [ ] Confirm 1-2 weeks available for validation
- [ ] Identify 20 agencies to contact
- [ ] Set up landing page infrastructure

### Before Starting Phase 1 (MVP):
- [ ] 50+ waitlist signups achieved
- [ ] 5 design partners validated concept
- [ ] Pricing validated ($79-$149/month)
- [ ] Claude accuracy >90% on manual tests

### Before Starting Phase 2 (Beta):
- [ ] MVP is stable and tested
- [ ] 10 beta testers recruited from waitlist
- [ ] Documentation complete (onboarding, FAQ)

### Before Starting Phase 3 (Growth):
- [ ] 10+ paying customers
- [ ] 40%+ trial-to-paid conversion
- [ ] <10% churn in first 3 months
- [ ] Clear product-market fit signals

---

## Customer Discovery Questions

**For WordPress Agencies**:
1. How many WordPress sites do you manage?
2. How much time do you spend on WordPress updates monthly?
3. What's your biggest fear when updating WordPress?
4. Have you ever had a site break after an update? What happened?
5. What tools do you currently use for updates?
6. How do you decide when it's safe to update?
7. Would you pay $149/month for a tool that scans your sites and warns you about compatibility issues before updating?
8. What features would make this a must-have vs. nice-to-have?
9. How do you communicate maintenance work to clients?
10. Would your developers use this, or just you?

---

**Document Version**: 2.0 (WordPress Agency Focus)
**Last Updated**: 2025-11-18
**Next Review**: After Phase 0 validation complete
