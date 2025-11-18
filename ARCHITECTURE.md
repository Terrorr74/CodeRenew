# CodeRenew - System Architecture

**Last Updated**: 2025-11-18
**Version**: 1.0
**Status**: Initial Architecture

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Technology Stack](#technology-stack)
4. [Component Architecture](#component-architecture)
5. [Database Schema](#database-schema)
6. [API Design](#api-design)
7. [Authentication & Security](#authentication--security)
8. [File Processing Pipeline](#file-processing-pipeline)
9. [AI Integration](#ai-integration)
10. [Deployment Architecture](#deployment-architecture)
11. [Scalability Considerations](#scalability-considerations)

---

## System Overview

CodeRenew is a full-stack web application that helps WordPress agencies analyze their sites for compatibility issues before updating WordPress versions. The system uses AI (Claude) to scan custom themes and plugins for deprecated functions, breaking changes, and security issues.

### Core Functionality

1. **User Management**: Registration, authentication, user profiles
2. **Site Management**: Track multiple WordPress sites per user
3. **File Upload**: Accept ZIP files containing WordPress themes/plugins
4. **AI Analysis**: Use Claude to analyze PHP code for compatibility issues
5. **Report Generation**: Display findings with severity levels and recommendations
6. **Dashboard**: Overview of all sites and their update readiness

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Client Layer                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │   Next.js Frontend (TypeScript + React)                       │  │
│  │   - Landing Page                                               │  │
│  │   - Authentication (Login/Register)                            │  │
│  │   - Dashboard                                                  │  │
│  │   - File Upload Interface                                      │  │
│  │   - Scan Results Display                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTPS/REST API
                                  │ JSON Request/Response
                                  │ JWT Authentication
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API Gateway Layer                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │   FastAPI Backend (Python)                                     │  │
│  │   - API Routers (Auth, Sites, Scans)                           │  │
│  │   - Request Validation (Pydantic)                              │  │
│  │   - JWT Token Verification                                     │  │
│  │   - CORS Configuration                                         │  │
│  │   - Rate Limiting                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
┌──────────────────────┐ ┌──────────────┐ ┌──────────────────────┐
│   Service Layer      │ │  Data Layer  │ │  External Services   │
│                      │ │              │ │                      │
│ ┌────────────────┐  │ │ ┌──────────┐ │ │ ┌────────────────┐  │
│ │WordPress       │  │ │ │PostgreSQL│ │ │ │Anthropic Claude│  │
│ │Scanner Service │  │ │ │Database  │ │ │ │API             │  │
│ └────────────────┘  │ │ └──────────┘ │ │ └────────────────┘  │
│                      │ │              │ │                      │
│ ┌────────────────┐  │ │ ┌──────────┐ │ │ ┌────────────────┐  │
│ │Claude AI       │  │ │ │SQLAlchemy│ │ │ │SendGrid/       │  │
│ │Service         │  │ │ │ORM       │ │ │ │Postmark Email  │  │
│ └────────────────┘  │ │ └──────────┘ │ │ └────────────────┘  │
│                      │ │              │ │                      │
│ ┌────────────────┐  │ │ ┌──────────┐ │ │                      │
│ │File Processor  │  │ │ │Alembic   │ │ │                      │
│ │Service         │  │ │ │Migrations│ │ │                      │
│ └────────────────┘  │ │ └──────────┘ │ │                      │
│                      │ │              │ │                      │
│ ┌────────────────┐  │ │              │ │                      │
│ │Report Generator│  │ │              │ │                      │
│ │Service         │  │ │              │ │                      │
│ └────────────────┘  │ │              │ │                      │
└──────────────────────┘ └──────────────┘ └──────────────────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
┌─────────────────────────────────────────────┐
│          Storage Layer                       │
│  ┌──────────────────────────────────────┐   │
│  │  Temporary File Storage (Local FS)   │   │
│  │  - Uploaded ZIP files                │   │
│  │  - Extracted theme/plugin files      │   │
│  │  - Auto-cleanup after 24 hours       │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend
- **Framework**: Next.js 14+ (React 18)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 3
- **HTTP Client**: Axios
- **State Management**: React Context API (for auth)
- **Form Validation**: Zod
- **UI Components**: Custom components with Tailwind

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **AI Integration**: Anthropic SDK

### Database
- **Database**: PostgreSQL 15
- **Connection Pooling**: SQLAlchemy async pool
- **Migrations**: Alembic

### Infrastructure
- **Development**: Docker Compose
- **Production**: Docker containers
- **Reverse Proxy**: Nginx (production)
- **SSL/TLS**: Let's Encrypt (production)

### External Services
- **AI**: Anthropic Claude API (Claude 3.5 Sonnet)
- **Email**: SendGrid or Postmark (transactional emails)
- **Future**: Stripe (payments), AWS S3 (file storage at scale)

---

## Component Architecture

### Frontend Architecture

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx            # Root layout
│   │   ├── page.tsx              # Landing page
│   │   ├── auth/                 # Authentication pages
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── dashboard/            # Dashboard pages
│   │   └── scan/                 # Scan results pages
│   │
│   ├── components/               # Reusable components
│   │   ├── forms/                # Form components
│   │   ├── layouts/              # Layout components
│   │   ├── ui/                   # UI primitives
│   │   └── scan/                 # Scan-specific components
│   │
│   ├── lib/                      # Utilities and integrations
│   │   ├── api/                  # API client
│   │   │   ├── client.ts         # Axios instance
│   │   │   ├── auth.ts           # Auth endpoints
│   │   │   ├── sites.ts          # Sites endpoints
│   │   │   └── scans.ts          # Scans endpoints
│   │   └── utils/                # Helper functions
│   │
│   └── types/                    # TypeScript type definitions
│       ├── auth.ts
│       ├── site.ts
│       └── scan.ts
```

### Backend Architecture

```
backend/
├── app/
│   ├── main.py                   # FastAPI app entry point
│   │
│   ├── core/                     # Core functionality
│   │   ├── config.py             # Settings management
│   │   ├── security.py           # JWT & password hashing
│   │   └── dependencies.py       # Dependency injection
│   │
│   ├── db/                       # Database configuration
│   │   ├── base.py               # Base model
│   │   └── session.py            # Database sessions
│   │
│   ├── models/                   # SQLAlchemy models
│   │   ├── user.py               # User model
│   │   ├── site.py               # Site model
│   │   ├── scan.py               # Scan model
│   │   └── scan_result.py        # ScanResult model
│   │
│   ├── schemas/                  # Pydantic schemas (validation)
│   │   ├── user.py               # User schemas
│   │   ├── site.py               # Site schemas
│   │   ├── scan.py               # Scan schemas
│   │   └── token.py              # Token schemas
│   │
│   ├── api/                      # API routes
│   │   └── v1/
│   │       ├── api.py            # API router
│   │       └── endpoints/
│   │           ├── auth.py       # Authentication
│   │           ├── sites.py      # Sites CRUD
│   │           └── scans.py      # Scans management
│   │
│   └── services/                 # Business logic
│       ├── wordpress/            # WordPress analysis
│       │   ├── scanner.py        # Code scanner
│       │   ├── deprecation_db.py # Deprecated functions DB
│       │   └── analyzer.py       # Analysis engine
│       │
│       ├── claude/               # Claude AI integration
│       │   ├── client.py         # API client
│       │   └── prompts.py        # Prompt templates
│       │
│       ├── file_processor/       # File handling
│       │   ├── extractor.py      # ZIP extraction
│       │   └── validator.py      # File validation
│       │
│       └── report/               # Report generation
│           └── generator.py      # PDF/HTML reports
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │───┐
│ email           │   │
│ hashed_password │   │
│ is_verified     │   │
│ created_at      │   │
└─────────────────┘   │
                      │ 1:N
                      │
        ┌─────────────┴───────────┐
        │                         │
        ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│     sites       │       │     scans       │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │───┐   │ id (PK)         │───┐
│ user_id (FK)    │   │   │ user_id (FK)    │   │
│ name            │   │   │ site_id (FK)    │   │
│ created_at      │   │   │ wp_version_from │   │
│ updated_at      │   │   │ wp_version_to   │   │
└─────────────────┘   │   │ risk_level      │   │
                      │   │ created_at      │   │
                      │   └─────────────────┘   │
                      │ 1:N                     │ 1:N
                      │                         │
                      └───┐                     │
                          ▼                     ▼
                  ┌─────────────────┐   ┌─────────────────┐
                  │  (scan → site)  │   │  scan_results   │
                  └─────────────────┘   ├─────────────────┤
                                        │ id (PK)         │
                                        │ scan_id (FK)    │
                                        │ issue_type      │
                                        │ severity        │
                                        │ file_path       │
                                        │ line_number     │
                                        │ description     │
                                        │ recommendation  │
                                        │ created_at      │
                                        └─────────────────┘
```

### Table Definitions

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### sites
```sql
CREATE TABLE sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sites_user_id ON sites(user_id);
```

#### scans
```sql
CREATE TABLE scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    site_id UUID REFERENCES sites(id) ON DELETE SET NULL,
    wordpress_version_from VARCHAR(50) NOT NULL,
    wordpress_version_to VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('safe', 'warning', 'critical')),
    file_size_bytes INTEGER,
    processing_time_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scans_user_id ON scans(user_id);
CREATE INDEX idx_scans_site_id ON scans(site_id);
CREATE INDEX idx_scans_created_at ON scans(created_at DESC);
```

#### scan_results
```sql
CREATE TABLE scan_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    issue_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'warning', 'info')),
    file_path VARCHAR(500) NOT NULL,
    line_number INTEGER,
    code_snippet TEXT,
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    evidence_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scan_results_scan_id ON scan_results(scan_id);
CREATE INDEX idx_scan_results_severity ON scan_results(severity);
```

---

## API Design

### REST API Endpoints

Base URL: `http://localhost:8000/api/v1`

#### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Create new user account | No |
| POST | `/auth/login` | Login and receive JWT token | No |
| GET | `/auth/me` | Get current user profile | Yes |
| POST | `/auth/verify-email` | Verify email with token | No |
| POST | `/auth/forgot-password` | Request password reset | No |
| POST | `/auth/reset-password` | Reset password with token | No |

#### Sites Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/sites` | List all user's sites | Yes |
| POST | `/sites` | Create new site | Yes |
| GET | `/sites/{site_id}` | Get site details | Yes |
| PUT | `/sites/{site_id}` | Update site name | Yes |
| DELETE | `/sites/{site_id}` | Delete site | Yes |

#### Scans Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/scans` | List user's scans | Yes |
| POST | `/scans/upload` | Upload files and start scan | Yes |
| GET | `/scans/{scan_id}` | Get scan details | Yes |
| GET | `/scans/{scan_id}/results` | Get scan results with issues | Yes |
| GET | `/scans/{scan_id}/report` | Download PDF report | Yes |
| DELETE | `/scans/{scan_id}` | Delete scan | Yes |

### Request/Response Examples

#### POST /api/v1/auth/register

**Request:**
```json
{
  "email": "agency@example.com",
  "password": "SecurePassword123!"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "agency@example.com",
  "is_verified": false,
  "created_at": "2025-11-18T10:00:00Z"
}
```

#### POST /api/v1/scans/upload

**Request (multipart/form-data):**
```
file: theme.zip (binary)
site_id: 550e8400-e29b-41d4-a716-446655440001
wordpress_version_from: 5.9
wordpress_version_to: 6.4
```

**Response (202 Accepted):**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "processing",
  "estimated_time_seconds": 60
}
```

#### GET /api/v1/scans/{scan_id}/results

**Response (200 OK):**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440002",
  "site_name": "Acme Corp - Main Site",
  "wordpress_version_from": "5.9",
  "wordpress_version_to": "6.4",
  "risk_level": "warning",
  "created_at": "2025-11-18T10:05:00Z",
  "summary": {
    "critical_issues": 2,
    "warnings": 5,
    "info_items": 3
  },
  "issues": [
    {
      "severity": "critical",
      "issue_type": "deprecated_function",
      "file_path": "functions.php",
      "line_number": 47,
      "code_snippet": "get_page($id)",
      "description": "Function get_page() was deprecated in WordPress 3.9",
      "recommendation": "Replace with get_post($id)",
      "evidence_url": "https://developer.wordpress.org/reference/functions/get_page/"
    }
  ]
}
```

---

## Authentication & Security

### JWT Authentication Flow

```
┌──────────┐                                           ┌──────────┐
│          │  1. POST /api/v1/auth/login              │          │
│  Client  │─────────────────────────────────────────>│  Server  │
│          │     { email, password }                   │          │
└──────────┘                                           └──────────┘
                                                            │
                                                            │ 2. Verify credentials
                                                            │    Hash password
                                                            │    Compare with DB
                                                            ▼
                                                       ┌──────────┐
                                                       │          │
                                                       │ Database │
                                                       │          │
                                                       └──────────┘
                                                            │
                                                            │ 3. Generate JWT token
                                                            │    Sign with secret key
                                                            │    Set expiration (7 days)
                                                            ▼
┌──────────┐                                           ┌──────────┐
│          │  4. Return JWT token                      │          │
│  Client  │<─────────────────────────────────────────│  Server  │
│          │     { access_token, token_type }          │          │
└──────────┘                                           └──────────┘
     │
     │ 5. Store token in memory/localStorage
     │
     ▼
┌──────────┐                                           ┌──────────┐
│          │  6. Subsequent requests with token        │          │
│  Client  │─────────────────────────────────────────>│  Server  │
│          │     Authorization: Bearer <token>         │          │
└──────────┘                                           └──────────┘
                                                            │
                                                            │ 7. Verify JWT signature
                                                            │    Check expiration
                                                            │    Extract user_id
                                                            ▼
                                                       [Process Request]
```

### Security Measures

**Password Security:**
- Bcrypt hashing (cost factor: 12)
- Minimum 8 characters, complexity requirements
- No password storage in logs or error messages

**Token Security:**
- HS256 algorithm for JWT signing
- 7-day expiration
- Secure secret key (256-bit)
- Tokens stored securely on client

**API Security:**
- CORS configuration (allow specific origins)
- Rate limiting (10 requests/minute for auth endpoints)
- Input validation with Pydantic
- SQL injection prevention via ORM
- XSS prevention (Content Security Policy headers)

**File Upload Security:**
- File size limits (50MB max)
- File type validation (ZIP only)
- Malware scanning before processing
- Sandboxed file processing
- Automatic cleanup after 24 hours

**Database Security:**
- Connection string in environment variables
- Prepared statements (via SQLAlchemy)
- Foreign key constraints
- Data encryption at rest (production)

---

## File Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    File Upload & Processing Flow                 │
└─────────────────────────────────────────────────────────────────┘

1. User uploads ZIP file (theme.zip)
   │
   ▼
2. Validate file
   ├─ Check file size (<50MB)
   ├─ Check file type (ZIP only)
   └─ Scan for malware
   │
   ▼
3. Store temporarily
   └─ /tmp/uploads/{user_id}/{scan_id}/theme.zip
   │
   ▼
4. Extract ZIP contents
   └─ /tmp/uploads/{user_id}/{scan_id}/extracted/
      ├── style.css
      ├── functions.php
      ├── template-parts/
      └── inc/
   │
   ▼
5. Parse PHP files
   ├─ Identify all .php files
   ├─ Extract function calls
   ├─ Detect WordPress hooks
   └─ Read file metadata (readme.txt, style.css)
   │
   ▼
6. Send to Claude AI for analysis
   ├─ Prompt: WordPress compatibility analysis
   ├─ Context: Current/target WP version, deprecation list
   ├─ Code: Concatenated PHP files
   └─ Request structured JSON response
   │
   ▼
7. Parse Claude response
   ├─ Extract issues array
   ├─ Validate JSON structure
   └─ Map to database schema
   │
   ▼
8. Save to database
   ├─ Create Scan record
   └─ Create ScanResult records (one per issue)
   │
   ▼
9. Generate report
   ├─ HTML report for web view
   └─ PDF report for download
   │
   ▼
10. Cleanup
    └─ Delete temporary files after 24 hours
```

### File Structure Example

**Input (theme.zip):**
```
mytheme/
├── style.css           # Theme metadata
├── functions.php       # Main theme functions
├── index.php           # Template files
├── header.php
├── footer.php
├── template-parts/     # Template components
│   ├── content.php
│   └── navigation.php
└── inc/                # Include files
    ├── customizer.php
    └── template-functions.php
```

**Extracted for Analysis:**
```
/tmp/uploads/550e8400-e29b-41d4-a716-446655440000/abc123/
├── theme.zip           # Original file
└── extracted/          # Extracted contents
    └── mytheme/
        ├── style.css
        ├── functions.php
        └── ...
```

---

## AI Integration

### Claude API Integration

**Service Architecture:**

```python
# backend/app/services/claude/client.py

class ClaudeService:
    """
    Handles communication with Anthropic Claude API
    """

    async def analyze_wordpress_compatibility(
        self,
        php_files: List[Dict[str, str]],
        current_version: str,
        target_version: str
    ) -> CompatibilityAnalysis:
        """
        Analyze WordPress code for compatibility issues

        Args:
            php_files: List of {filename: content} dicts
            current_version: Current WordPress version (e.g., "5.9")
            target_version: Target WordPress version (e.g., "6.4")

        Returns:
            CompatibilityAnalysis with risk level and issues
        """

        # Build prompt with context
        prompt = self._build_compatibility_prompt(
            php_files,
            current_version,
            target_version
        )

        # Call Claude API
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse structured response
        return self._parse_response(response)
```

### Prompt Engineering

**Compatibility Analysis Prompt:**

```python
COMPATIBILITY_PROMPT_TEMPLATE = """
You are a WordPress compatibility expert. Analyze the following PHP code for compatibility issues when upgrading from WordPress {current_version} to {target_version}.

## Context

**Deprecated Functions in WordPress {target_version}:**
{deprecated_functions_list}

**Breaking Changes:**
{breaking_changes_list}

**Security Considerations:**
{security_notes}

## Code to Analyze

{php_code_files}

## Instructions

Analyze the code and return a JSON response with the following structure:

```json
{{
  "risk_level": "safe|warning|critical",
  "overall_summary": "Brief summary of findings",
  "issues": [
    {{
      "severity": "critical|warning|info",
      "issue_type": "deprecated_function|breaking_change|security|best_practice",
      "file": "filename.php",
      "line": 123,
      "code_snippet": "the problematic code",
      "description": "Clear explanation of the issue",
      "recommendation": "Specific steps to fix",
      "evidence": "Link to WordPress documentation"
    }}
  ]
}}
```

## Severity Definitions

- **critical**: Code will definitely break, site will be non-functional
- **warning**: Code may break or cause issues, needs testing
- **info**: Best practice improvements, no immediate risk

Be thorough but conservative. Only flag real issues, not hypothetical ones.
"""
```

### Claude Response Processing

```python
def _parse_response(self, response: Message) -> CompatibilityAnalysis:
    """
    Parse Claude's JSON response into structured data
    """
    try:
        # Extract JSON from response
        content = response.content[0].text
        data = json.loads(content)

        # Validate structure
        risk_level = data.get("risk_level", "warning")
        issues = data.get("issues", [])

        # Map to domain models
        return CompatibilityAnalysis(
            risk_level=RiskLevel(risk_level),
            summary=data.get("overall_summary", ""),
            issues=[
                Issue(
                    severity=Severity(issue["severity"]),
                    issue_type=IssueType(issue["issue_type"]),
                    file_path=issue["file"],
                    line_number=issue.get("line"),
                    code_snippet=issue.get("code_snippet"),
                    description=issue["description"],
                    recommendation=issue["recommendation"],
                    evidence_url=issue.get("evidence")
                )
                for issue in issues
            ]
        )
    except (json.JSONDecodeError, KeyError) as e:
        raise ClaudeResponseError(f"Failed to parse Claude response: {e}")
```

### Cost Management

**Token Usage Tracking:**

```python
# Track usage per scan
scan_metrics = {
    "input_tokens": response.usage.input_tokens,
    "output_tokens": response.usage.output_tokens,
    "total_cost_usd": calculate_cost(response.usage)
}

# Claude 3.5 Sonnet pricing (as of Nov 2024)
INPUT_TOKEN_COST = 3.00 / 1_000_000   # $3 per million
OUTPUT_TOKEN_COST = 15.00 / 1_000_000  # $15 per million
```

**Budget Limits:**
- Max 50,000 input tokens per scan (~$0.15)
- Max 10,000 output tokens per scan (~$0.15)
- Total: ~$0.30 per scan maximum
- Alert if scan exceeds $0.50

---

## Deployment Architecture

### Development Environment

```yaml
# docker-compose.yml

services:
  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: coderenew
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: coderenew_dev
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://coderenew:dev_password@postgres/coderenew_dev
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
    volumes:
      - ./backend:/app
      - /tmp/uploads:/tmp/uploads

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
```

### Production Deployment (Future)

```
                    ┌──────────────┐
                    │   Cloudflare │
                    │   DNS + CDN  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Nginx     │
                    │ Reverse Proxy│
                    │  SSL/TLS     │
                    └──────┬───────┘
                           │
           ┌───────────────┴────────────────┐
           │                                │
           ▼                                ▼
    ┌──────────────┐              ┌──────────────┐
    │   Frontend   │              │   Backend    │
    │   Next.js    │              │   FastAPI    │
    │   Container  │              │   Container  │
    └──────────────┘              └──────┬───────┘
                                         │
                                         ▼
                                  ┌──────────────┐
                                  │  PostgreSQL  │
                                  │   Database   │
                                  └──────────────┘
```

**Infrastructure Components:**
- **Load Balancer**: AWS ALB or DigitalOcean Load Balancer
- **App Servers**: Docker containers (2-4 instances for redundancy)
- **Database**: Managed PostgreSQL (AWS RDS or DigitalOcean)
- **File Storage**: AWS S3 or DigitalOcean Spaces
- **Monitoring**: Sentry for errors, Prometheus + Grafana for metrics

---

## Scalability Considerations

### Current Architecture Limits

**MVP Capacity (Single Server):**
- Concurrent users: ~100-200
- Scans per hour: ~60-100
- Database: ~1 million scans
- File storage: Local disk (hundreds of scans per day)

### Scaling Strategies

**Phase 1 (0-100 users):**
- Single server deployment
- Local file storage
- Synchronous processing
- PostgreSQL on same server

**Phase 2 (100-1,000 users):**
- Separate database server
- AWS S3 for file storage
- Async processing with Celery + Redis
- 2-3 app servers behind load balancer

**Phase 3 (1,000+ users):**
- Auto-scaling app servers (Kubernetes)
- Database read replicas
- CDN for static assets
- Background job workers (separate containers)
- Rate limiting with Redis
- Caching layer (Redis)

### Performance Optimizations

**Database:**
- Connection pooling (SQLAlchemy async)
- Indexes on frequently queried fields
- Pagination for list endpoints
- Query optimization (select only needed fields)

**API:**
- Response compression (gzip)
- Async endpoints for long-running operations
- Request deduplication
- Rate limiting per user

**File Processing:**
- Stream processing for large files
- Chunked uploads for better UX
- Parallel file analysis (process multiple files concurrently)

**Caching:**
- Cache WordPress deprecation database (Redis)
- Cache user sessions (Redis)
- CDN for static frontend assets

---

## Monitoring & Observability

### Metrics to Track

**Application Metrics:**
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Active users (concurrent, daily, monthly)

**Business Metrics:**
- Scans per day/week/month
- Average scan processing time
- Claude API cost per scan
- Conversion rate (signup → paid)

**Infrastructure Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network bandwidth
- Database connections

### Logging Strategy

**Structured Logging (JSON):**
```python
logger.info(
    "Scan completed",
    extra={
        "user_id": user.id,
        "scan_id": scan.id,
        "processing_time": elapsed_seconds,
        "file_size_bytes": file_size,
        "risk_level": scan.risk_level,
        "issues_found": len(issues)
    }
)
```

**Log Levels:**
- **DEBUG**: Development only
- **INFO**: Normal operations (scan started, completed)
- **WARNING**: Recoverable issues (API rate limit approaching)
- **ERROR**: Errors that need attention (Claude API failure)
- **CRITICAL**: System failures (database down)

---

## Security Checklist

### Application Security
- [ ] HTTPS everywhere (no HTTP in production)
- [ ] JWT tokens with secure signing
- [ ] Password hashing with bcrypt (cost 12+)
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (ORM usage)
- [ ] XSS prevention (CSP headers)
- [ ] CSRF protection for state-changing operations
- [ ] Rate limiting on auth endpoints

### Infrastructure Security
- [ ] Firewall rules (only necessary ports open)
- [ ] Regular security updates (OS, dependencies)
- [ ] Secrets in environment variables (not code)
- [ ] Database encryption at rest
- [ ] Secure file upload handling
- [ ] Malware scanning on uploads
- [ ] Regular backups (database, configuration)

### Compliance
- [ ] Privacy Policy (GDPR, CCPA)
- [ ] Terms of Service
- [ ] Data retention policy (delete after X days)
- [ ] User data export capability
- [ ] User data deletion capability

---

## Development Workflow

### Local Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/CodeRenew.git
cd CodeRenew

# 2. Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Set Anthropic API key
# Edit backend/.env and add your ANTHROPIC_API_KEY

# 4. Start services
docker-compose up -d

# 5. Run migrations
docker-compose exec backend alembic upgrade head

# 6. Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Git Workflow

```
main
  └─ develop
       ├─ feature/user-authentication
       ├─ feature/wordpress-scanner
       └─ feature/report-generation
```

**Branch naming:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation

**Commit messages:**
```
<type>: <short summary>

<optional detailed description>

<optional footer>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

---

## Testing Strategy

### Backend Testing

**Unit Tests** (pytest):
```python
# tests/services/test_wordpress_scanner.py
def test_detect_deprecated_function():
    code = "<?php get_page(123); ?>"
    issues = scanner.analyze_code(code, "5.9", "6.4")
    assert len(issues) == 1
    assert issues[0].issue_type == "deprecated_function"
```

**Integration Tests:**
```python
# tests/api/test_scans.py
def test_create_scan_authenticated(client, auth_token):
    response = client.post(
        "/api/v1/scans/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": open("test_theme.zip", "rb")}
    )
    assert response.status_code == 202
```

### Frontend Testing

**Component Tests** (Jest + React Testing Library):
```typescript
// __tests__/components/LoginForm.test.tsx
test('submits form with valid credentials', async () => {
  render(<LoginForm />)
  fireEvent.change(screen.getByLabelText('Email'), {
    target: { value: 'test@example.com' }
  })
  fireEvent.change(screen.getByLabelText('Password'), {
    target: { value: 'password123' }
  })
  fireEvent.click(screen.getByText('Login'))
  await waitFor(() => {
    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123')
  })
})
```

**E2E Tests** (Playwright - future):
```typescript
test('complete scan workflow', async ({ page }) => {
  await page.goto('http://localhost:3000/login')
  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('input[name="password"]', 'password123')
  await page.click('button[type="submit"]')
  await page.waitForURL('**/dashboard')
  // ... continue workflow
})
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-18
**Next Review**: After MVP Phase 1 completion
