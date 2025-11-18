# CodeRenew - Prioritized Execution Plan

**Last Updated**: 2025-11-17
**Status**: Pre-Launch Planning
**Target**: Build MVP and validate product-market fit

---

## Executive Summary

CodeRenew is currently a **specification document**, not a functioning product. This execution plan prioritizes building a viable MVP, validating AI quality, and proving product-market fit before scaling.

**Key Insight**: The biggest risk is not technical execution but proving that AI-powered code modernization delivers reliable, production-ready results that users will pay for.

**Critical Path**: Build MVP → Validate Quality → Prove Value Proposition → Scale

---

## Target Customer (Phase 0-1)

**Primary**: Individual Developers / Freelancers
- Most willing to try MVP
- Tolerant of rough edges
- Can provide fast feedback
- Lower security requirements

**Secondary** (Future): Small Development Teams, then Enterprise

---

## Phase 0: Pre-Launch MVP (Weeks 1-3)

**Goal**: Build functional product that 10 beta testers can use safely

### Critical Path Tasks

#### ✅ TODO 1: Build MVP from Blueprint (P0-1) - 2 weeks
**Priority**: P0 - CRITICAL
**Effort**: 2 weeks
**Owner**: TBD

**Subtasks**:
- [ ] Set up project structure (backend + frontend)
- [ ] Implement FastAPI backend
  - [ ] `/api/modernize-file` endpoint
  - [ ] `/api/download/{task_id}` endpoint
  - [ ] File upload handling
  - [ ] Temp directory management
- [ ] Implement Next.js frontend
  - [ ] Home page (`pages/index.jsx`)
  - [ ] Upload page (`pages/upload.jsx`)
  - [ ] FileUploader component
  - [ ] CodeViewer component
  - [ ] API integration
- [ ] Basic error handling
- [ ] Manual testing with sample files

**Acceptance Criteria**:
- User can upload a single code file
- System returns modernized code, diff, and explanation
- User can download results as ZIP
- Basic error messages display correctly

---

#### ✅ TODO 2: Integrate Official Anthropic SDK (P0-2) - 2 days
**Priority**: P0 - CRITICAL
**Effort**: 2 days
**Owner**: TBD

**Rationale**: Current plan uses custom HTTP requests. This is fragile and risky.

**Subtasks**:
- [ ] Install `anthropic` Python SDK (`pip install anthropic`)
- [ ] Replace custom HTTP in `services/claude_service.py`
- [ ] Implement proper error handling for API failures
- [ ] Add rate limiting awareness
- [ ] Test with various file sizes and edge cases

**Acceptance Criteria**:
- Uses official Anthropic Python SDK
- Handles API errors gracefully (rate limits, timeouts, invalid keys)
- Returns structured responses consistently

**Resources**: https://docs.anthropic.com/claude/reference/getting-started-with-the-api

---

#### ✅ TODO 3: Add File Size Limits (P0-3) - 4 hours
**Priority**: P0 - CRITICAL
**Effort**: 4 hours
**Owner**: TBD

**Rationale**: Prevent cost spirals and service abuse.

**Subtasks**:
- [ ] Add file size validation in upload endpoint
- [ ] Set limit: 500 lines OR 50KB (whichever is smaller)
- [ ] Return clear error message if file exceeds limit
- [ ] Add limit info to frontend UI
- [ ] Log rejected uploads for monitoring

**Acceptance Criteria**:
- Files over 500 lines/50KB are rejected with clear message
- Limit is displayed prominently on upload page
- Rejection doesn't crash the service

**Configuration**:
```python
MAX_FILE_SIZE_KB = 50
MAX_FILE_LINES = 500
```

---

#### ✅ TODO 4: Implement User-Provided API Keys (P0-5 Option A) - 3 days
**Priority**: P0 - CRITICAL
**Effort**: 3 days
**Owner**: TBD

**Rationale**: Reduces liability, makes costs transparent, simplifies launch.

**Subtasks**:
- [ ] Add API key input field to upload form
- [ ] Validate API key format (basic check)
- [ ] Test API key with Anthropic API before processing
- [ ] Display clear error if key is invalid
- [ ] Add security warning: "Your key is sent directly to Anthropic, not stored"
- [ ] Option: Encrypt key in browser local storage for convenience (optional)
- [ ] Update backend to accept API key per request

**Acceptance Criteria**:
- User provides Claude API key on upload page
- System validates key is functional before processing
- Clear error if key is invalid/expired
- Security message is visible

**Security Notes**:
- DO NOT store keys in database (unless encrypted with user-specific encryption)
- DO NOT log keys
- Consider: Store encrypted in browser localStorage for user convenience

---

#### ✅ TODO 5: Add Cost Estimation (P0-4) - 1 day
**Priority**: P0 - CRITICAL
**Effort**: 1 day
**Owner**: TBD

**Rationale**: Users need to know costs before committing.

**Subtasks**:
- [ ] Calculate estimated tokens from file size
- [ ] Display estimated cost based on Claude pricing
- [ ] Show estimate BEFORE user clicks "Modernize"
- [ ] Link to Claude API pricing page
- [ ] Add disclaimer: "Actual cost may vary"

**Acceptance Criteria**:
- Before processing, user sees: "Estimated tokens: ~1,500 | Est. cost: ~$0.02"
- Calculation is visible in UI
- Link to Anthropic pricing docs

**Formula**:
```
Estimated tokens ≈ (characters / 4) * 1.5  # 1.5x for prompt overhead
Cost = tokens * price_per_token
```

**Current Claude Pricing** (verify before launch):
- Claude 3.5 Sonnet: $3 per million input tokens, $15 per million output tokens

---

### Phase 0 Deliverable Checklist

**Before showing to beta testers**:
- [ ] All P0 tasks complete (5/5)
- [ ] Manual testing with 10+ sample files (Python, JavaScript, Java, etc.)
- [ ] Error handling works for common failures
- [ ] UI is functional (doesn't need to be beautiful)
- [ ] Cost estimation is accurate within 20%
- [ ] Security warning about API keys is clear
- [ ] README with setup instructions

**Beta Tester Selection**:
- 10 developers from your network
- Mix of languages (Python, JavaScript, PHP, etc.)
- Willing to provide honest feedback

---

## Phase 1: Validation (Weeks 4-8)

**Goal**: Validate product-market fit with 50-100 users

### Critical Path Tasks

#### ✅ TODO 6: Add Quality Feedback Loop (P1-1) - 3 days
**Priority**: P1 - HIGH
**Effort**: 3 days
**Owner**: TBD

**Rationale**: THIS IS YOUR #1 VALIDATION MECHANISM. Without this, you can't tell if the product works.

**Subtasks**:
- [ ] Add rating UI to results page
  - [ ] Thumbs up / thumbs down buttons
  - [ ] Optional text feedback field
  - [ ] "What could be improved?" prompt
- [ ] Store feedback with task_id in database
- [ ] Create admin dashboard to view feedback
- [ ] Email yourself on negative feedback (for fast response)
- [ ] Track: % positive, common issues, which languages work best

**Acceptance Criteria**:
- Every modernization result has feedback buttons
- Feedback is stored persistently
- You can view all feedback in simple dashboard
- You receive alerts on negative feedback

**Success Metric**: 70%+ positive feedback rate

---

#### ✅ TODO 7: Add Language/Framework Targeting (P1-3) - 1 week
**Priority**: P1 - HIGH
**Effort**: 1 week
**Owner**: TBD

**Rationale**: Generic "modernize this code" produces mediocre results. Specific migrations produce much better results.

**Subtasks**:
- [ ] Add dropdown: "What are you modernizing?"
  - Python 2.7 → Python 3.11
  - JavaScript ES5 → ES2023
  - jQuery → React
  - PHP 5 → PHP 8
  - Java 8 → Java 17
- [ ] Create specialized prompt templates for each migration
- [ ] Test each migration type with 5+ real-world examples
- [ ] Document which migrations work well vs poorly
- [ ] Update UI with migration-specific tips

**Acceptance Criteria**:
- User selects specific migration type
- Prompt is customized based on selection
- Each migration has been manually validated with sample code
- Migration quality feedback is tracked separately

**Prompt Engineering**:
```python
MIGRATIONS = {
    'py27_to_py311': {
        'prompt': 'Modernize this Python 2.7 code to Python 3.11. Focus on: print statements → print(), unicode handling, iteritems() → items(), division operator, type annotations.',
        'examples': [...] # Few-shot examples
    },
    # ... other migrations
}
```

---

#### ✅ TODO 8: Implement Multi-File Processing (P1-2) - 2 weeks
**Priority**: P1 - HIGH (but can defer if Phase 0 feedback shows single-file is sufficient)
**Effort**: 2 weeks
**Owner**: TBD

**Rationale**: Real codebases are multi-file projects. This is key differentiator vs "just asking Claude."

**Subtasks**:
- [ ] Accept ZIP file upload (in addition to single file)
- [ ] Extract ZIP to temp directory
- [ ] Limit: Max 20 files or 5MB total
- [ ] Analyze project structure (detect language, find entry points)
- [ ] Process files with project context awareness
  - [ ] Identify import/dependency relationships
  - [ ] Maintain consistency across files
  - [ ] Update import statements
- [ ] Generate consolidated project report
- [ ] Return modernized project as ZIP
- [ ] Update cost estimation for multi-file

**Acceptance Criteria**:
- User can upload ZIP with up to 20 files
- System detects project structure
- Import statements are updated correctly
- Cross-file consistency is maintained
- Cost estimate reflects multi-file processing

**⚠️ WARNING**: This significantly increases Claude API costs. Make sure cost estimation and limits are working first.

**Defer if**: Phase 0 feedback shows users are happy with single-file processing.

---

#### ✅ TODO 9: Add Async Task Processing (P1-4) - 1 week
**Priority**: P1 - MEDIUM-HIGH
**Effort**: 1 week
**Owner**: TBD

**Rationale**: Better UX for larger files, enables scaling.

**Subtasks**:
- [ ] Install Celery + Redis
- [ ] Convert modernize endpoint to async task
- [ ] Return task_id immediately
- [ ] Add `/api/status/{task_id}` endpoint
- [ ] Frontend: Poll for completion every 2 seconds
- [ ] Show progress indicator
- [ ] Handle task failures gracefully

**Acceptance Criteria**:
- Upload returns immediately with task_id
- User sees progress/spinner while processing
- Results appear automatically when ready
- Failed tasks show clear error message

**Tech Stack**:
```bash
pip install celery redis
docker run -d -p 6379:6379 redis
```

**Can defer to Phase 2 if**: Users tolerate synchronous processing for MVP.

---

### Phase 1 Validation Metrics

**Track Weekly**:
- Total modernizations processed
- Unique active users
- Positive feedback rate (target: 70%+)
- Return user rate (target: 30%+ weekly)
- Most popular language migrations
- Average file size
- API cost per modernization

**Success Criteria for Phase 2**:
- [ ] 50+ active users
- [ ] 70%+ positive feedback rate
- [ ] 30%+ users return within 7 days
- [ ] At least 2 language migrations have >80% positive feedback
- [ ] Users can articulate value vs using Claude directly

**Failure Conditions** (consider pivot):
- < 50% positive feedback (AI quality insufficient)
- < 10% return rate (no repeat value)
- Users say "I can just do this in ChatGPT" (weak differentiation)

---

## Phase 2: Growth & Monetization (Months 3-6)

**Goal**: Scale to hundreds of users and validate monetization

### Tasks (Prioritize based on Phase 1 learnings)

#### ✅ TODO 10: Add Result Validation Features (MISSING-1) - 1 week
**Priority**: P2 - MEDIUM
**Effort**: 1 week

**Features**:
- [ ] Syntax validation (lint the modernized code)
- [ ] If tests exist, offer to run them
- [ ] Show before/after complexity metrics
- [ ] Highlight potential breaking changes
- [ ] Side-by-side diff viewer

---

#### ✅ TODO 11: Implement History & Iteration (MISSING-2) - 1 week
**Priority**: P2 - MEDIUM
**Effort**: 1 week

**Features**:
- [ ] User accounts (optional, can use email for now)
- [ ] View past modernizations
- [ ] Re-run with different parameters
- [ ] "Try again with more conservative changes" button
- [ ] Save favorite configurations

---

#### ✅ TODO 12: Add Unit Tests (P2-1) - 3-5 days
**Priority**: P2 - MEDIUM
**Effort**: 3-5 days

**Coverage**:
- [ ] Claude API response parsing
- [ ] JSON extraction logic
- [ ] Diff generation
- [ ] File upload validation
- [ ] Cost estimation calculation
- [ ] Multi-file project analysis

---

#### ✅ TODO 13: Launch Freemium Pricing (MISSING-3) - 1 week + legal
**Priority**: P2 - HIGH
**Effort**: 1 week implementation + legal review

**Pricing Tiers** (DRAFT - validate with user feedback):

**Free Tier**:
- 10 files/month
- Single file only
- User provides API key
- Community support

**Pro ($19/month)**:
- 100 files/month
- Multi-file projects (up to 50 files)
- We provide API key (included in price)
- Email support
- History & iteration features

**Enterprise ($199/month)**:
- Unlimited files
- Batch API access
- Dedicated support
- SOC2 compliance (future)
- Self-hosted option (future)

**Implementation**:
- [ ] Stripe integration
- [ ] Usage tracking
- [ ] Tier enforcement
- [ ] Upgrade/downgrade flows
- [ ] Billing dashboard

**Legal Requirements**:
- [ ] Terms of Service
- [ ] Privacy Policy
- [ ] GDPR compliance plan
- [ ] API key handling disclosure

---

#### ✅ TODO 14: Docker Compose Production Setup (P2-3) - 2-3 days
**Priority**: P2 - MEDIUM
**Effort**: 2-3 days

**Setup**:
- [ ] Frontend container (Next.js)
- [ ] Backend container (FastAPI)
- [ ] Redis container (Celery)
- [ ] Nginx reverse proxy
- [ ] PostgreSQL (for user data)
- [ ] Volume mounts
- [ ] Environment variables
- [ ] Docker Compose file
- [ ] Deployment docs

---

## Phase 3: Enterprise Features (Months 6-12)

**Defer until Phase 2 success is proven**

- Team collaboration
- Batch processing API
- CI/CD integrations (GitHub Actions, GitLab CI)
- Advanced diff visualization
- Cost optimization (batching/chunking)
- SOC2 compliance
- Self-hosted enterprise option

---

## Risk Management

### RISK 1: AI Quality Insufficient
**Mitigation**:
- Start with narrow use cases (2-3 specific migrations)
- Collect quality feedback from day 1
- Be transparent that output requires review
- Have human review process for first 100 modernizations
- Consider: Offer "expert review" paid service

**Contingency**: If quality < 70% positive after 100 modernizations, pause and investigate:
- Are prompts optimized?
- Is Claude 3.5 Sonnet the right model?
- Do we need fine-tuning?
- Should we focus on even narrower use case?

---

### RISK 2: Weak Differentiation
**Mitigation**:
- Focus on multi-file project awareness
- Build specialized migration expertise
- Add validation and testing features
- Provide history and iteration
- Create community of shared learnings

**Contingency**: If users say "I can just use ChatGPT," add features that ChatGPT can't do:
- CI/CD integration
- Automated testing of results
- Team collaboration
- Enterprise security

---

### RISK 3: Cost Structure
**Mitigation**:
- Start with user-provided keys
- Add value beyond API orchestration
- Explore caching common patterns
- Consider hybrid model

**Contingency**: If margins are too thin, focus on premium features or enterprise self-hosted.

---

### RISK 4: Security Breach
**Mitigation**:
- Clear terms about data handling
- Encrypt sensitive data
- Regular security audits
- Liability insurance

**Contingency**: Have incident response plan ready.

---

## Success Metrics by Phase

### Phase 0 (Weeks 1-3)
- [ ] MVP is functional
- [ ] 10 beta testers complete testing
- [ ] Basic feedback is positive

### Phase 1 (Weeks 4-8)
- [ ] 50+ active users
- [ ] 70%+ positive feedback
- [ ] 30%+ weekly return rate
- [ ] 2+ migrations proven reliable

### Phase 2 (Months 3-6)
- [ ] 500+ users
- [ ] 100+ paying customers
- [ ] $2,000+ MRR
- [ ] 80%+ customer satisfaction

### Phase 3 (Months 6-12)
- [ ] 2,000+ users
- [ ] $10,000+ MRR
- [ ] 5+ enterprise customers
- [ ] Clear market leadership in 1+ niches

---

## Resource Requirements

### MVP (Phase 0)
- **Developer time**: 3 weeks full-time (or 6 weeks part-time)
- **Infrastructure**: $50/month (hosting, Redis)
- **Claude API**: $0 (users provide keys)
- **Total**: Mostly time investment

### Phase 1-2
- **Developer time**: 3-6 months
- **Infrastructure**: $200-500/month
- **Claude API**: $500-2000/month (if you provide keys)
- **Legal**: $2,000-5,000 (terms, privacy policy)
- **Marketing**: $1,000-5,000/month
- **Total**: $10,000-30,000 for 6 months

---

## Decision Points

### Before Starting Phase 0:
- [ ] Confirm you have 3 weeks to dedicate
- [ ] Decide: Bootstrap vs seek funding?
- [ ] Identify 10 beta testers

### Before Starting Phase 1:
- [ ] Validate: Did beta testers find value?
- [ ] Decide: Which 2-3 migrations to focus on?
- [ ] Commit to 3-month validation period

### Before Starting Phase 2:
- [ ] Validate: 70%+ positive feedback achieved?
- [ ] Validate: 30%+ users return weekly?
- [ ] Decide: Pricing model
- [ ] Decide: Continue solo or hire help?

### Before Starting Phase 3:
- [ ] Validate: $2,000+ MRR achieved?
- [ ] Decide: Continue bootstrapped or raise funding?
- [ ] Decide: Target enterprise or stay SMB?

---

## Next Steps (Immediate)

1. **Review this plan** - Does it match your goals and resources?
2. **Validate assumptions** - Talk to 5 potential users about their legacy code pain
3. **Set up development environment** - Clone repo, install dependencies
4. **Start TODO 1** - Build the MVP
5. **Schedule weekly check-ins** - Track progress against timeline

---

## Questions to Answer Before Starting

1. **Time commitment**: Can you dedicate 3 weeks full-time for MVP?
2. **Technical skills**: Comfortable with FastAPI + Next.js + Claude API?
3. **Target users**: Do you have access to 10-50 developers for beta testing?
4. **Financial runway**: Can you sustain 6 months without revenue?
5. **Competitive advantage**: What's your unique insight on code modernization?

---

## Appendix: Original Feature Prioritization

From product-quality-guardian analysis:

**P0 - CRITICAL** (Must have for any release):
- Build actual MVP
- Official Anthropic SDK
- File size limits
- Cost transparency
- API key management

**P1 - HIGH** (Critical for product-market fit):
- Quality feedback loop
- Multi-file processing
- Language/framework targeting
- Async task processing

**P2 - MEDIUM** (Important but not critical):
- Unit tests
- Cost control/batching
- Docker Compose setup

**P3 - LOW** (Nice to have):
- Advanced diff visualization
- Batch processing API

**MISSING FEATURES**:
- Result validation
- History & iteration
- Pricing/monetization strategy
- Value differentiation

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
**Next Review**: After Phase 0 completion
